from __future__ import annotations

import hashlib
from collections import Counter
from typing import Iterable

from .agents import ContentAIAgent
from .models import ContentItem
from .platform import ContentPlatformMock


def run_workflow(items: Iterable[ContentItem], item_ids: Iterable[str], *, mode: str = "simulation") -> dict[str, object]:
    """Run the customer workflow while isolating item-level failures.

    The return shape is intentionally API-friendly: a caller can render the
    same result as a console report, a browser operations view, or a future
    provider adapter without changing the decision contract.
    """

    selected_ids = tuple(dict.fromkeys(item_ids))
    platform = ContentPlatformMock(tuple(items))
    agent = ContentAIAgent(platform)
    results: list[dict[str, object]] = []

    for item_id in selected_ids:
        try:
            item = platform.get_item(item_id)
            decision = agent.evaluate_item(item)
            metadata_patch = {
                "classification": str(decision["classification"]),
                "retention_policy": str(decision["retention_policy"]),
                "confidence": str(decision["confidence"]),
                "disposition": str(decision["disposition"]),
                "risk_level": str(decision["risk_level"]),
            }
            if decision["policy_flags"]:
                metadata_patch["policy_flags"] = ", ".join(decision["policy_flags"])
            updated = platform.update_metadata(item_id, **metadata_patch)

            actions: dict[str, object] = {"metadata_updated": True}
            if decision["disposition"] == "auto_process":
                actions["shared_link"] = platform.create_shared_link(item_id, "internal-workflow")
            else:
                status = "blocked_pending_review" if decision["disposition"] == "blocked" else "pending_review"
                actions["approval"] = platform.route_for_approval(
                    item_id,
                    str(decision["approver"]),
                    status=status,
                    reason=str(decision["rationale"]),
                )

            results.append(
                {
                    "item_id": item_id,
                    "title": updated.title,
                    "status": "processed",
                    "item": {
                        "department": updated.department,
                        "content_type": updated.content_type,
                        "sensitivity": updated.sensitivity,
                        "lifecycle_stage": updated.lifecycle_stage,
                        "owner": updated.owner,
                    },
                    "decision": decision,
                    "actions": actions,
                    "summary": agent.summarize_item(updated),
                }
            )
        except KeyError as exc:
            results.append(
                {
                    "item_id": item_id,
                    "title": "Unknown content item",
                    "status": "failed",
                    "error": str(exc),
                    "decision": None,
                    "actions": {},
                }
            )

    processed = [result for result in results if result["status"] == "processed"]
    failed = [result for result in results if result["status"] == "failed"]
    dispositions = Counter(
        str(result["decision"]["disposition"])
        for result in processed
        if result["decision"] is not None
    )
    controls = _evaluate_controls(processed, failed)
    run_key = ",".join(selected_ids) or "empty"
    run_id = f"RUN-{hashlib.sha1(run_key.encode('utf-8')).hexdigest()[:8].upper()}"

    return {
        "run_id": run_id,
        "mode": mode,
        "status": "partial" if failed and processed else ("failed" if failed else "complete"),
        "summary": {
            "selected": len(selected_ids),
            "processed": len(processed),
            "failed": len(failed),
            "auto_process": dispositions.get("auto_process", 0),
            "needs_review": dispositions.get("needs_review", 0),
            "blocked": dispositions.get("blocked", 0),
        },
        "results": results,
        "evaluation": {
            "status": "pass" if all(control["passed"] for control in controls) else "review",
            "passed": sum(1 for control in controls if control["passed"]),
            "total": len(controls),
            "controls": controls,
        },
        "audit_log": list(platform.audit_log()),
    }


def _evaluate_controls(processed: list[dict[str, object]], failed: list[dict[str, object]]) -> list[dict[str, object]]:
    sensitive_review = all(
        not (
            result["item"]["sensitivity"] in {"restricted", "confidential"}
            and result["decision"]["disposition"] == "auto_process"
        )
        for result in processed
    )
    unsafe_blocked = all(
        result["decision"]["disposition"] == "blocked"
        for result in processed
        if "policy-conflict" in result["decision"]["policy_flags"]
        or result["decision"]["classification"] == "security-escalation"
    )
    traceable = all(
        result["decision"]["rationale"] and result["decision"]["next_action"]
        for result in processed
    )
    failure_isolated = not failed or bool(processed)
    return [
        {
            "id": "sensitive-review",
            "label": "Sensitive content requires review",
            "passed": sensitive_review,
            "detail": "Confidential and restricted items never receive an automatic link.",
        },
        {
            "id": "unsafe-blocked",
            "label": "Unsafe requests are blocked",
            "passed": unsafe_blocked,
            "detail": "Credential, access, and approval-bypass signals stop automatic processing.",
        },
        {
            "id": "explainable-routing",
            "label": "Every route has a reason",
            "passed": traceable,
            "detail": "Each processed item includes confidence, policy flags, rationale, and next action.",
        },
        {
            "id": "failure-isolation",
            "label": "Item failures stay isolated",
            "passed": failure_isolated,
            "detail": "A missing item is reported without hiding successful decisions for the rest of the run.",
        },
    ]
