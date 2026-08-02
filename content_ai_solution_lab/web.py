from __future__ import annotations

import json
import mimetypes
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlsplit

from .agents import ContentAIAgent
from .catalog import load_content_items, search_content, summarize_catalog
from .cli import build_scenario
from .discovery import extract_solution_themes
from .workflow import run_workflow


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = PROJECT_ROOT / "web"
DATA_DIR = PROJECT_ROOT / "data"
CONTENT_PATH = DATA_DIR / "sample_content.json"
DISCOVERY_PATH = DATA_DIR / "discovery_notes.json"


class DemoApplication:
    """Small dependency-free HTTP application for the local and serverless demo."""

    def __init__(self, content_path: Path = CONTENT_PATH, discovery_path: Path = DISCOVERY_PATH) -> None:
        self.content_path = content_path
        self.discovery_path = discovery_path
        self.items = load_content_items(content_path)
        self.scenario = build_scenario(content_path, discovery_path)

    def handle(self, method: str, path: str, body: bytes = b"") -> tuple[int, dict[str, str], object]:
        parsed = urlsplit(path)
        route = parsed.path.rstrip("/") or "/"
        query = {key: values[-1] for key, values in parse_qs(parsed.query).items()}

        if route == "/api/health" and method == "GET":
            return 200, {}, {
                "status": "ok",
                "provider": {
                    "name": "Mock Content API",
                    "mode": "deterministic",
                    "credentials_required": False,
                    "message": "Local rules preserve a real integration-shaped contract without tenant credentials.",
                },
            }

        if route == "/api/scenario" and method == "GET":
            return 200, {}, self._scenario_payload()

        if route == "/api/content" and method == "GET":
            filtered = search_content(
                self.items,
                department=query.get("department") or None,
                sensitivity=query.get("sensitivity") or None,
                query=query.get("query") or None,
            )
            return 200, {}, {"items": [asdict(item) for item in filtered], "total": len(filtered)}

        if route.startswith("/api/content/") and route.endswith("/evaluation") and method == "GET":
            item_id = unquote(route.split("/")[3])
            try:
                item = next(item for item in self.items if item.item_id == item_id)
            except StopIteration:
                return self._error(404, f"Unknown content item: {item_id}")
            agent = ContentAIAgent(_platform_for(self.items))
            return 200, {}, {"item": asdict(item), "decision": agent.evaluate_item(item)}

        if route == "/api/run" and method == "POST":
            return self._run(body)

        if route == "/api/handoff" and method == "GET":
            return 200, {}, _handoff_payload()

        return self._error(404, "Route not found")

    def _run(self, body: bytes) -> tuple[int, dict[str, str], object]:
        try:
            payload = json.loads(body.decode("utf-8") or "{}")
        except (UnicodeDecodeError, json.JSONDecodeError):
            return self._error(400, "Request body must be valid JSON.")

        if not isinstance(payload, dict):
            return self._error(422, "Request body must be an object.")
        item_ids = payload.get("item_ids")
        mode = payload.get("mode", "simulation")
        if not isinstance(item_ids, list) or not item_ids:
            return self._error(422, "item_ids must be a non-empty array.")
        if len(item_ids) > 10:
            return self._error(422, "Select no more than 10 items per sample run.")
        if any(not isinstance(item_id, str) or not item_id.strip() for item_id in item_ids):
            return self._error(422, "Every item_id must be a non-empty string.")
        if mode not in {"simulation", "dry_run"}:
            return self._error(422, "mode must be simulation or dry_run.")

        return 200, {}, run_workflow(self.items, item_ids, mode=mode)

    def _scenario_payload(self) -> dict[str, object]:
        themes = extract_solution_themes(self.scenario.discovery_signals)
        departments = sorted({item.department for item in self.items})
        sensitivities = sorted({item.sensitivity for item in self.items})
        return {
            "customer": self.scenario.customer,
            "industry": self.scenario.industry,
            "engagement": "Sample engagement / no login",
            "source_label": "Deterministic mock content API",
            "github_url": "https://github.com/amalfarhad/content-ai-solution-lab",
            "discovery_signals": [asdict(signal) for signal in self.scenario.discovery_signals],
            "themes": themes,
            "requirements": _requirements_payload(self.scenario.discovery_signals),
            "catalog": {
                "total": len(self.items),
                "departments": departments,
                "sensitivities": sensitivities,
                "summary": summarize_catalog(self.items),
            },
            "recommendations": [asdict(recommendation) for recommendation in self.scenario.recommendations],
            "handoff": _handoff_payload(),
        }

    @staticmethod
    def _error(status: int, message: str) -> tuple[int, dict[str, str], object]:
        return status, {}, {"error": message}


def _platform_for(items: tuple[Any, ...]):
    from .platform import ContentPlatformMock

    return ContentPlatformMock(items)


def _requirements_payload(signals: tuple[Any, ...]) -> list[dict[str, object]]:
    return [
        {
            "id": "route",
            "label": "Route work to the right owner",
            "evidence": signals[0].desired_outcome,
            "status": "observed",
        },
        {
            "id": "govern",
            "label": "Keep sensitive content governed",
            "evidence": signals[2].desired_outcome,
            "status": "observed",
        },
        {
            "id": "enrich",
            "label": "Enrich metadata before handoff",
            "evidence": signals[1].desired_outcome,
            "status": "observed",
        },
        {
            "id": "explain",
            "label": "Make every AI decision reviewable",
            "evidence": "Confidence, policy flags, rationale, and next action stay visible in the run record.",
            "status": "design control",
        },
    ]


def _handoff_payload() -> dict[str, object]:
    return {
        "phases": [
            {
                "label": "01 / Map",
                "title": "Confirm source and owner mapping",
                "detail": "Validate repository IDs, department ownership, lifecycle fields, and approver groups with the customer.",
            },
            {
                "label": "02 / Pilot",
                "title": "Run a governed sample",
                "detail": "Measure routing coverage, metadata completeness, manual review touches, and policy exceptions on representative content.",
            },
            {
                "label": "03 / Handoff",
                "title": "Operationalize the contract",
                "detail": "Replace mock adapters with authenticated provider calls, preserve audit events, and define rollback ownership.",
            },
        ],
        "api_mapping": [
            {"sample": "catalog search", "real_integration_shape": "content.search", "owner": "Solutions Engineering"},
            {"sample": "metadata update", "real_integration_shape": "content.updateMetadata", "owner": "Content Operations"},
            {"sample": "approval routing", "real_integration_shape": "workflow.createApproval", "owner": "Control Owner"},
            {"sample": "audit export", "real_integration_shape": "governance.exportAudit", "owner": "IT / Security"},
        ],
        "boundaries": [
            "No customer credentials, private tenant, or production content is used.",
            "Sample shared links are deterministic placeholders and do not resolve to real content.",
            "The evaluation demonstrates control behavior; it does not claim customer business impact.",
        ],
    }


class DemoRequestHandler(BaseHTTPRequestHandler):
    application = DemoApplication()

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler contract
        route = urlsplit(self.path).path
        if route.startswith("/api/"):
            self._send_json(*self.application.handle("GET", self.path))
            return
        self._send_static(route)

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler contract
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        self._send_json(*self.application.handle("POST", self.path, body))

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def _send_json(self, status: int, headers: dict[str, str], payload: object) -> None:
        raw = json.dumps(payload, default=list).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(raw)

    def _send_static(self, route: str) -> None:
        relative = "index.html" if route in {"", "/"} else route.lstrip("/")
        candidate = (WEB_ROOT / relative).resolve()
        if WEB_ROOT not in candidate.parents and candidate != WEB_ROOT:
            self._send_json(403, {}, {"error": "Forbidden path"})
            return
        if not candidate.is_file():
            self._send_json(404, {}, {"error": "Asset not found"})
            return
        raw = candidate.read_bytes()
        content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def create_server(host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), DemoRequestHandler)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Serve the Content AI Solution Lab browser demo.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    server = create_server(args.host, args.port)
    print(f"Content AI Solution Lab running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
