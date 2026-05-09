from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .models import ContentItem


def load_content_items(path: str | Path) -> tuple[ContentItem, ...]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return tuple(ContentItem(**row) for row in payload["content_items"])


def search_content(
    items: Iterable[ContentItem],
    *,
    department: str | None = None,
    content_type: str | None = None,
    sensitivity: str | None = None,
    query: str | None = None,
) -> tuple[ContentItem, ...]:
    query_terms = set((query or "").lower().split())
    matches: list[ContentItem] = []

    for item in items:
        if department and item.department.lower() != department.lower():
            continue
        if content_type and item.content_type.lower() != content_type.lower():
            continue
        if sensitivity and item.sensitivity.lower() != sensitivity.lower():
            continue
        if query_terms:
            haystack = f"{item.title} {item.text} {item.owner}".lower()
            if not query_terms.intersection(haystack.split()):
                continue
        matches.append(item)
    return tuple(matches)


def summarize_catalog(items: Iterable[ContentItem]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for item in items:
        key = f"{item.department}:{item.content_type}:{item.sensitivity}"
        summary[key] = summary.get(key, 0) + 1
    return dict(sorted(summary.items()))

