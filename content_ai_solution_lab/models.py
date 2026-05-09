from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ContentItem:
    item_id: str
    title: str
    content_type: str
    department: str
    sensitivity: str
    lifecycle_stage: str
    owner: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DiscoverySignal:
    stakeholder: str
    business_problem: str
    current_state: str
    desired_outcome: str
    systems: tuple[str, ...]
    compliance_needs: tuple[str, ...]


@dataclass(frozen=True)
class WorkflowRecommendation:
    workflow_name: str
    use_case: str
    target_users: tuple[str, ...]
    api_actions: tuple[str, ...]
    ai_agent_actions: tuple[str, ...]
    governance_controls: tuple[str, ...]
    success_metrics: tuple[str, ...]
    demo_steps: tuple[str, ...]
    risk_notes: tuple[str, ...]


@dataclass(frozen=True)
class DemoScenario:
    customer: str
    industry: str
    discovery_signals: tuple[DiscoverySignal, ...]
    content_items: tuple[ContentItem, ...]
    recommendations: tuple[WorkflowRecommendation, ...]

