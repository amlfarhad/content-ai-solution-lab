from __future__ import annotations

from .discovery import extract_solution_themes
from .models import ContentItem, DiscoverySignal, WorkflowRecommendation


def build_recommendations(
    signals: tuple[DiscoverySignal, ...],
    items: tuple[ContentItem, ...],
) -> tuple[WorkflowRecommendation, ...]:
    themes = extract_solution_themes(signals)
    top_theme = max(themes, key=themes.get)
    departments = tuple(sorted({item.department for item in items}))

    recommendations = [
        WorkflowRecommendation(
            workflow_name="AI-assisted contract and invoice intake",
            use_case="Classify incoming content, apply metadata, and route high-risk items to the right approver.",
            target_users=("Legal Ops", "Finance Operations", "Sales Operations"),
            api_actions=("metadata update", "shared link creation", "approval routing", "audit export"),
            ai_agent_actions=("classify content type", "summarize document", "recommend approver", "flag retention policy"),
            governance_controls=("restricted-link defaults", "department-based approver mapping", "audit log export"),
            success_metrics=("approval cycle time", "manual routing touches", "metadata completeness", "policy exception rate"),
            demo_steps=(
                "Ingest mixed contract, invoice, and employee-record content.",
                "Run the content AI agent to classify each item and apply metadata.",
                "Route sensitive items to the mapped approver and create an auditable action trail.",
                "Show how the workflow reduces manual handoffs while preserving governance.",
            ),
            risk_notes=("AI recommendations stay explainable and reviewable before approval actions are finalized.",),
        ),
        WorkflowRecommendation(
            workflow_name="Executive content intelligence workspace",
            use_case="Give business and IT leaders a single view of content volume, sensitivity, workflow health, and AI-assisted actions.",
            target_users=("Business Leaders", "IT Administrators", "Solutions Engineers"),
            api_actions=("catalog search", "metadata aggregation", "audit-log readout", "dashboard export"),
            ai_agent_actions=("summarize business context", "prioritize workflow candidates", "surface governance gaps"),
            governance_controls=("sensitivity segmentation", "owner accountability", "compliance-tag visibility"),
            success_metrics=("time to find documents", "workflow adoption", "sensitive-content coverage", "demo conversion notes"),
            demo_steps=(
                "Open the customer scenario dashboard.",
                "Walk through pain points gathered in discovery.",
                "Connect each workflow recommendation to a business outcome and platform capability.",
                "Close with success metrics and a phased rollout plan.",
            ),
            risk_notes=("Dashboard uses aggregate metadata and avoids exposing restricted document text.",),
        ),
    ]

    if top_theme in {"search", "analytics"} or len(departments) > 2:
        return tuple(recommendations)
    return (recommendations[0],)

