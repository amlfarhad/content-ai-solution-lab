# Architecture

`content-ai-solution-lab` is a solutions-engineering portfolio project for customer-facing enterprise AI workflows. It is intentionally built without vendor-specific credentials so the demo can be run locally, inspected in code review, and discussed in interviews without exposing any private platform.

## Components

- `catalog.py` loads and filters enterprise content objects by department, content type, sensitivity, and query terms.
- `discovery.py` turns stakeholder discovery notes into solution themes such as automation, governance, AI, search, and analytics.
- `platform.py` exposes a small API-like content platform surface: metadata updates, shared-link creation, approval routing, audit export, and item lookup.
- `agents.py` provides deterministic AI-agent behavior for classification, retention-policy recommendation, summarization, and approver selection.
- `solution.py` maps discovery signals and catalog context into customer-facing workflow recommendations.
- `brief.py` renders a Markdown solution brief and a browser-ready HTML demo dashboard.
- `cli.py` packages the workflow into repeatable commands for catalog review, discovery analysis, agent execution, and full demo generation.

## Design Choices

- The AI agent is deterministic rather than model-backed. This keeps the project reproducible while still showing prompt-like decomposition, explainability, and human-reviewable output.
- API actions are represented by a mock platform class. This demonstrates product/API thinking without claiming access to a real enterprise tenant.
- Governance is first-class: each recommendation includes access, audit, retention, or sensitivity controls alongside the AI workflow.
- The generated dashboard is a customer-demo artifact, not a backend admin screen. The goal is to show how a solutions engineer would connect product capabilities to business problems.

## Data Flow

1. Load stakeholder discovery notes and sample content metadata.
2. Extract solution themes from the discovery notes.
3. Build workflow recommendations matched to business problems, target users, API actions, AI-agent actions, controls, and metrics.
4. Run the content AI agent against sensitive items to classify and route approval packets.
5. Export a solution brief, demo dashboard, and audit log.

