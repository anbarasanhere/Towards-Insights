from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .git_publisher import GitPublisher
from .markdown import render_case
from .models import AnalysisRequest, AnalysisResult
from .providers import analyze

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "web"


class Handler(BaseHTTPRequestHandler):
    def _send(
        self, status: int, payload: object, content_type: str = "application/json"
    ) -> None:
        body = (
            payload
            if isinstance(payload, bytes)
            else (
                json.dumps(payload).encode()
                if content_type == "application/json"
                else str(payload).encode()
            )
        )
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        asset = {
            "/": (WEB / "index.html", "text/html"),
            "/style.css": (WEB / "style.css", "text/css"),
            "/app.js": (WEB / "app.js", "application/javascript"),
        }.get(self.path)
        if asset:
            path, content_type = asset
            self._send(200, path.read_bytes(), content_type)
            return
        if self.path != "/":
            self._send(404, {"error": "Not found"})
            return

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        try:
            data = json.loads(self.rfile.read(length))
            request = AnalysisRequest(**data)
            request.validate()
            if self.path == "/api/analyze":
                self._send(200, analyze(request).to_dict())
            elif self.path == "/api/publish":
                result = AnalysisResult.from_dict(data["analysis"])
                content = render_case(request, result)
                config = {
                    "repo_path": os.getenv("REPOSITORY_PATH", str(ROOT)),
                    "remote": os.getenv("GIT_REMOTE", "origin"),
                    "branch": os.getenv("GIT_BRANCH", "main"),
                }
                self._send(
                    200, GitPublisher(**config).publish(request.case_title, content)
                )
            else:
                self._send(404, {"error": "Not found"})
        except (ValueError, KeyError, TypeError, RuntimeError, OSError) as error:
            self._send(400, {"error": str(error)})

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    port = int(os.getenv("PORT", "8765"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Towards Insights running at http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
