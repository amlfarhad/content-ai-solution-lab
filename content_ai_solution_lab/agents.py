from __future__ import annotations

from .models import ContentItem
from .platform import ContentPlatformMock


class ContentAIAgent:
    def __init__(self, platform: ContentPlatformMock) -> None:
        self.platform = platform

    def classify_item(self, item: ContentItem) -> dict[str, str]:
        text = f"{item.title} {item.text}".lower()
        if "invoice" in text or "payment" in text:
            queue = "finance-automation"
            retention = "7-year-finance"
        elif "contract" in text or "msa" in text:
            queue = "legal-review"
            retention = "contract-lifecycle"
        elif "employee" in text or "compensation" in text:
            queue = "hr-confidential"
            retention = "employee-record"
        else:
            queue = "business-owner-review"
            retention = "standard-business"

        confidence = "high" if item.sensitivity in {"confidential", "restricted"} else "medium"
        return {
            "classification": queue,
            "retention_policy": retention,
            "confidence": confidence,
        }

    def prepare_approval_packet(self, item_id: str) -> dict[str, object]:
        item = self.platform.get_item(item_id)
        classification = self.classify_item(item)
        updated = self.platform.update_metadata(item_id, **classification)
        approver = self._select_approver(updated)
        approval = self.platform.route_for_approval(item_id, approver)
        return {
            "item": updated.title,
            "classification": classification,
            "approval": approval,
            "summary": self.summarize_item(updated),
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

