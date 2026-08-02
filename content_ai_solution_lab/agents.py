from __future__ import annotations

from .governance import evaluate_content_item
from .models import ContentItem
from .platform import ContentPlatformMock


class ContentAIAgent:
    def __init__(self, platform: ContentPlatformMock) -> None:
        self.platform = platform

    def classify_item(self, item: ContentItem) -> dict[str, str]:
        decision = evaluate_content_item(item)
        return {
            "classification": str(decision["classification"]),
            "retention_policy": str(decision["retention_policy"]),
            "confidence": str(decision["confidence"]),
        }

    def evaluate_item(self, item: ContentItem) -> dict[str, object]:
        return evaluate_content_item(item)

    def prepare_approval_packet(self, item_id: str) -> dict[str, object]:
        item = self.platform.get_item(item_id)
        decision = self.evaluate_item(item)
        classification = {
            key: str(decision[key])
            for key in ("classification", "retention_policy", "confidence")
        }
        updated = self.platform.update_metadata(item_id, **classification)
        approver = str(decision["approver"] or self._select_approver(updated))
        approval = self.platform.route_for_approval(
            item_id,
            approver,
            status="blocked_pending_review" if decision["disposition"] == "blocked" else "pending_review",
            reason=str(decision["rationale"]),
        )
        return {
            "item": updated.title,
            "classification": classification,
            "approval": approval,
            "summary": self.summarize_item(updated),
            "decision": decision,
        }

    def summarize_item(self, item: ContentItem) -> str:
        words = item.text.replace("\n", " ").split()
        excerpt = " ".join(words[:24])
        return f"{item.title}: {excerpt}{'...' if len(words) > 24 else ''}"

    @staticmethod
    def _select_approver(item: ContentItem) -> str:
        if item.department == "Legal":
            return "legal-ops@example.com"
        if item.department == "Finance":
            return "ap-controller@example.com"
        if item.department == "People":
            return "people-ops@example.com"
        return f"{item.owner.lower().replace(' ', '.')}@example.com"
