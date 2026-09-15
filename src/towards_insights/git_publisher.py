from __future__ import annotations

import subprocess
from pathlib import Path

from .markdown import case_path


class GitPublisher:
    def __init__(
        self, repo_path: str = ".", remote: str = "origin", branch: str = "main"
    ) -> None:
        self.repo_path = Path(repo_path).resolve()
        self.remote = remote
        self.branch = branch

    def _run(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=self.repo_path, text=True, capture_output=True
        )
        if result.returncode:
            raise RuntimeError(
                result.stderr.strip() or result.stdout.strip() or "Git command failed."
            )
        return result.stdout.strip()

    def _sync_with_remote(self) -> None:
        """Integrate remote commits before changing the case file."""
        if self._run("status", "--porcelain"):
            raise RuntimeError(
                "The repository has local changes. Commit or stash them before publishing a case."
            )
        self._run("fetch", self.remote, self.branch)
        try:
            self._run("rebase", f"{self.remote}/{self.branch}")
        except RuntimeError as error:
            try:
                self._run("rebase", "--abort")
            except RuntimeError:
                pass
            raise RuntimeError(
                "Could not integrate the latest GitHub changes automatically. "
                "Resolve the rebase conflict locally, then publish again."
            ) from error

    def publish(self, title: str, content: str) -> dict[str, str]:
        self._sync_with_remote()
        path = case_path(self.repo_path, title)
        path.parent.mkdir(exist_ok=True)
        existed = path.exists()
        path.write_text(content, encoding="utf-8")
        relative = str(path.relative_to(self.repo_path))
        self._run("add", "--", relative)
        self._run(
            "commit",
            "-m",
            f"{'Update' if existed else 'Add'} case: {title}",
            "--",
            relative,
        )
        try:
            self._run("push", self.remote, self.branch)
        except RuntimeError as error:
            try:
                self._sync_with_remote()
                self._run("push", self.remote, self.branch)
            except RuntimeError as retry_error:
                raise RuntimeError(
                    "GitHub changed while publishing. The case commit remains local; "
                    "resolve the branch state and publish again."
                ) from retry_error
        return {"path": relative, "action": "updated" if existed else "created"}
