from __future__ import annotations

from http.server import BaseHTTPRequestHandler

from content_ai_solution_lab.web import DemoApplication


class handler(BaseHTTPRequestHandler):  # noqa: N801 - Vercel's Python function contract
    def do_GET(self) -> None:  # noqa: N802
        self._respond(*DemoApplication().handle("GET", self.path))

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        self._respond(*DemoApplication().handle("POST", self.path, self.rfile.read(length)))

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def _respond(self, status: int, headers: dict[str, str], payload: object) -> None:
        import json

        raw = json.dumps(payload, default=list).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(raw)
