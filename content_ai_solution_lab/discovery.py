from __future__ import annotations

import json
from pathlib import Path

from .models import DiscoverySignal


def load_discovery_signals(path: str | Path) -> tuple[DiscoverySignal, ...]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return tuple(
        DiscoverySignal(
            stakeholder=row["stakeholder"],
            business_problem=row["business_problem"],
            current_state=row["current_state"],
            desired_outcome=row["desired_outcome"],
            systems=tuple(row["systems"]),
            compliance_needs=tuple(row["compliance_needs"]),
        )
        for row in payload["discovery_signals"]
    )


def extract_solution_themes(signals: tuple[DiscoverySignal, ...]) -> dict[str, int]:
    vocabulary = {
        "approval": ("approval", "review", "routing", "sign-off"),
        "search": ("search", "find", "locate", "discover"),
        "governance": ("governance", "retention", "compliance", "access"),
        "automation": ("manual", "handoff", "automate", "duplicate"),
        "analytics": ("visibility", "metrics", "tracking", "status"),
        "ai": ("summarize", "classify", "agent", "recommend"),
    }

    theme_counts = {theme: 0 for theme in vocabulary}
    for signal in signals:
        text = " ".join(
            [
                signal.business_problem,
                signal.current_state,
                signal.desired_outcome,
                " ".join(signal.systems),
                " ".join(signal.compliance_needs),
            ]
        ).lower()
        for theme, terms in vocabulary.items():
            theme_counts[theme] += sum(1 for term in terms if term in text)
    return dict(sorted(theme_counts.items(), key=lambda item: (-item[1], item[0])))

