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

    def publish(self, title: str, content: str) -> dict[str, str]:
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
        self._run("push", self.remote, self.branch)
        return {"path": relative, "action": "updated" if existed else "created"}
