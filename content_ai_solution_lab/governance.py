from __future__ import annotations

from .models import ContentItem


_RETENTION_BY_QUEUE = {
    "legal-review": "contract-lifecycle",
    "finance-automation": "7-year-finance",
    "hr-confidential": "employee-record",
    "security-review": "security-questionnaire",
    "security-escalation": "security-exception",
    "business-owner-review": "standard-business",
}

_APPROVER_BY_DEPARTMENT = {
    "Legal": "legal-ops@example.com",
    "Finance": "ap-controller@example.com",
    "People": "people-ops@example.com",
    "Security": "security-ops@example.com",
}


def evaluate_content_item(item: ContentItem) -> dict[str, object]:
    """Return an explainable, deterministic governance decision for one item.

    The rules intentionally favor a human checkpoint whenever sensitivity or
    policy ambiguity is present. They model the contract a real provider could
    implement without pretending that this local demo has access to a tenant or
    an external model.
    """

    text = f"{item.title} {item.text}".lower()
    policy_flags: list[str] = []
    detected_signals: list[str] = []

    critical_signals = {
        "credential-exposure": ("password", "credential", "secret", "api key"),
        "approval-bypass": ("bypass approval", "skip approval", "without approval", "bypass review"),
        "unsafe-access-request": ("production access", "admin access", "temporary admin", "elevated access"),
        "external-sharing-risk": ("external contractor", "external sharing", "public link", "share broadly"),
    }
    for flag, terms in critical_signals.items():
        matched = [term for term in terms if term in text]
        if matched:
            policy_flags.append(flag)
            detected_signals.extend(matched)

    ambiguous_terms = ("unclear", "unknown", "maybe", "tbd", "missing context", "urgent exception")
    ambiguous_matches = [term for term in ambiguous_terms if term in text]
    if ambiguous_matches:
        policy_flags.append("ambiguous-request")
        detected_signals.extend(ambiguous_matches)

    if "security" in text or "access control" in text or "encryption" in text:
        queue = "security-review"
        detected_signals.append("security-content")
    elif "invoice" in text or "payment" in text:
        queue = "finance-automation"
        detected_signals.append("finance-content")
    elif "contract" in text or "msa" in text:
        queue = "legal-review"
        detected_signals.append("contract-content")
    elif "employee" in text or "compensation" in text:
        queue = "hr-confidential"
        detected_signals.append("people-content")
    else:
        queue = "business-owner-review"
        detected_signals.append("general-business-content")

    if critical_signals and any(flag in policy_flags for flag in critical_signals):
        queue = "security-escalation"

    if item.sensitivity == "restricted":
        policy_flags.append("restricted-content")
    elif item.sensitivity == "confidential":
        policy_flags.append("confidential-content")

    if queue == "security-escalation":
        disposition = "blocked"
        risk_level = "high"
        confidence = "high" if len(policy_flags) >= 2 else "medium"
        rationale = "Policy engine detected a potentially unsafe access or sharing request; no link or automatic action is allowed."
        next_action = "Security owner must validate the exception and remove any credential or access-risk language."
        link_policy = "no_link"
    elif "ambiguous-request" in policy_flags or item.sensitivity in {"restricted", "confidential"}:
        disposition = "needs_review"
        risk_level = "medium"
        confidence = "medium"
        rationale = "The workflow can classify this item, but sensitivity or incomplete context requires a human checkpoint before handoff."
        next_action = "Route the approval packet to the mapped owner, then apply the retention policy after review."
        link_policy = "restricted_link_after_approval"
    else:
        disposition = "auto_process"
        risk_level = "low"
        confidence = "high"
        rationale = "Known content signals and an internal sensitivity level meet the demo policy for automatic metadata enrichment."
        next_action = "Apply metadata and create an internal-only link for the configured workflow audience."
        link_policy = "internal_only"

    approver = "security-ops@example.com" if queue == "security-escalation" else _APPROVER_BY_DEPARTMENT.get(item.department)
    if approver is None:
        approver = f"{item.owner.lower().replace(' ', '.')}@example.com"

    return {
        "classification": queue,
        "retention_policy": _RETENTION_BY_QUEUE[queue],
        "confidence": confidence,
        "disposition": disposition,
        "risk_level": risk_level,
        "approver": approver,
        "rationale": rationale,
        "next_action": next_action,
        "link_policy": link_policy,
        "policy_flags": tuple(dict.fromkeys(policy_flags)),
        "detected_signals": tuple(dict.fromkeys(detected_signals)),
    }
