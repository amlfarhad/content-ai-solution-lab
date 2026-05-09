from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agents import ContentAIAgent
from .brief import write_demo_dashboard, write_solution_brief
from .catalog import load_content_items, summarize_catalog
from .discovery import extract_solution_themes, load_discovery_signals
from .models import DemoScenario
from .platform import ContentPlatformMock
from .solution import build_recommendations


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"


def build_scenario(content_path: Path, discovery_path: Path) -> DemoScenario:
    items = load_content_items(content_path)
    signals = load_discovery_signals(discovery_path)
    recommendations = build_recommendations(signals, items)
    return DemoScenario(
        customer="Northstar Manufacturing",
        industry="Manufacturing and field services",
        discovery_signals=signals,
        content_items=items,
        recommendations=recommendations,
    )


def cmd_catalog(args: argparse.Namespace) -> None:
    items = load_content_items(args.content)
    print(json.dumps(summarize_catalog(items), indent=2))


def cmd_discovery(args: argparse.Namespace) -> None:
    signals = load_discovery_signals(args.discovery)
    print(json.dumps(extract_solution_themes(signals), indent=2))


def cmd_agent(args: argparse.Namespace) -> None:
    items = load_content_items(args.content)
    platform = ContentPlatformMock(items)
    agent = ContentAIAgent(platform)
    packet = agent.prepare_approval_packet(args.item_id)
    print(json.dumps(packet, indent=2))


def cmd_demo(args: argparse.Namespace) -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    scenario = build_scenario(args.content, args.discovery)
    brief_path = REPORTS_DIR / "solution_brief.md"
    dashboard_path = REPORTS_DIR / "demo_dashboard.html"
    audit_path = REPORTS_DIR / "agent_audit_log.json"

    platform = ContentPlatformMock(scenario.content_items)
    agent = ContentAIAgent(platform)
    for item in scenario.content_items:
        if item.sensitivity in {"confidential", "restricted"}:
            agent.prepare_approval_packet(item.item_id)
    platform.export_audit_log(audit_path)

    write_solution_brief(scenario, brief_path)
    write_demo_dashboard(scenario, dashboard_path)
    print(f"Wrote {brief_path}")
    print(f"Wrote {dashboard_path}")
    print(f"Wrote {audit_path}")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build customer-facing AI content workflow demos.")
    p.add_argument("--content", type=Path, default=DATA_DIR / "sample_content.json")
    p.add_argument("--discovery", type=Path, default=DATA_DIR / "discovery_notes.json")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("catalog", help="Summarize the sample content catalog.").set_defaults(func=cmd_catalog)
    sub.add_parser("discovery", help="Extract solution themes from discovery notes.").set_defaults(func=cmd_discovery)
    agent = sub.add_parser("agent", help="Run an AI-agent approval packet for one item.")
    agent.add_argument("item_id")
    agent.set_defaults(func=cmd_agent)
    sub.add_parser("demo", help="Generate a solution brief, demo dashboard, and audit log.").set_defaults(func=cmd_demo)
    return p


def main() -> None:
    args = parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

