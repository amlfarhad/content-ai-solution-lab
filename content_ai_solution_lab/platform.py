from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from .models import ContentItem


class ContentPlatformMock:
    """Small API-like surface that mirrors common enterprise content operations."""

    def __init__(self, items: tuple[ContentItem, ...]) -> None:
        self._items = {item.item_id: item for item in items}
        self._audit_log: list[dict[str, str]] = []

    def get_item(self, item_id: str) -> ContentItem:
        try:
            return self._items[item_id]
        except KeyError as exc:
            raise KeyError(f"Unknown content item: {item_id}") from exc

    def update_metadata(self, item_id: str, **metadata: str) -> ContentItem:
        item = self.get_item(item_id)
        updated = ContentItem(
            item_id=item.item_id,
            title=item.title,
            content_type=item.content_type,
            department=item.department,
            sensitivity=item.sensitivity,
            lifecycle_stage=item.lifecycle_stage,
            owner=item.owner,
            text=item.text,
            metadata={**item.metadata, **metadata},
        )
        self._items[item_id] = updated
        self._audit("metadata.updated", item_id, f"Updated {sorted(metadata)}")
        return updated

    def create_shared_link(self, item_id: str, audience: str) -> str:
        link = self.preview_shared_link(item_id, audience)
        item = self.get_item(item_id)
        self._audit("shared_link.created", item.item_id, f"Audience={audience}")
        return link

    def preview_shared_link(self, item_id: str, audience: str) -> str:
        """Return the deterministic link that would be created, without auditing it."""

        item = self.get_item(item_id)
        token = hashlib.sha1(f"{item.item_id}:{audience}".encode("utf-8")).hexdigest()[:12]
        return f"https://content.example/shared/{token}"

    def route_for_approval(
        self,
        item_id: str,
        approver: str,
        *,
        status: str = "pending_review",
        reason: str = "",
    ) -> dict[str, str]:
        item = self.get_item(item_id)
        detail = f"Approver={approver}; Status={status}"
        if reason:
            detail += f"; Reason={reason}"
        self._audit("approval.routed", item.item_id, detail)
        packet = {
            "item_id": item.item_id,
            "title": item.title,
            "approver": approver,
            "status": status,
        }
        if reason:
            packet["reason"] = reason
        return packet

    def audit_log(self) -> tuple[dict[str, str], ...]:
        return tuple(self._audit_log)

    def export_audit_log(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self._audit_log, indent=2), encoding="utf-8")

    def _audit(self, action: str, item_id: str, detail: str) -> None:
        self._audit_log.append({"action": action, "item_id": item_id, "detail": detail})

    def snapshot(self) -> list[dict[str, object]]:
        return [asdict(item) for item in self._items.values()]
