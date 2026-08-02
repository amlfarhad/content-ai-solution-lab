# Architecture

`content-ai-solution-lab` is a solutions-engineering portfolio project for customer-facing enterprise AI workflows. It is intentionally built without vendor-specific credentials so the demo can be run locally, inspected in code review, and discussed in interviews without exposing any private platform.

## Components

- `catalog.py` loads and filters enterprise content objects by department, content type, sensitivity, and query terms.
- `discovery.py` turns stakeholder discovery notes into solution themes such as automation, governance, AI, search, and analytics.
- `platform.py` exposes a small API-like content platform surface: metadata updates, shared-link creation, approval routing, audit export, and item lookup.
- `agents.py` provides deterministic AI-agent behavior for classification, retention-policy recommendation, summarization, and approver selection.
- `governance.py` evaluates sensitivity, ambiguity, credential/access signals, policy conflicts, disposition, and link policy.
- `workflow.py` executes a selected sample run, isolates item-level failures, applies mock API actions, and evaluates acceptance controls.
- `solution.py` maps discovery signals and catalog context into customer-facing workflow recommendations.
- `brief.py` renders a Markdown solution brief and a browser-ready HTML demo dashboard.
- `web.py` exposes the same contracts over dependency-free HTTP for the browser workbench and Vercel Python function.
- `web/` contains the responsive no-login operations view, including a static seeded fallback for hosting environments that cannot invoke Python.
- `cli.py` packages the workflow into repeatable commands for catalog review, discovery analysis, agent execution, full demo generation, and local web serving.

## Design Choices

- The AI agent is deterministic rather than model-backed. This keeps the project reproducible while still showing prompt-like decomposition, explainability, and human-reviewable output.
- API actions are represented by a mock platform class. This demonstrates product/API thinking without claiming access to a real enterprise tenant.
- Governance is first-class: each decision includes access, audit, retention, sensitivity, confidence, rationale, next action, and policy flags alongside the AI workflow.
- Failure isolation: a missing content ID becomes an item-level failure in a partial run instead of hiding successful decisions.
- Explicit execution modes: simulation records mock provider actions; dry run projects the same actions without mutating metadata or audit state.
- The generated dashboard and browser workbench are customer-demo artifacts, not backend admin screens. The goal is to show how a solutions engineer would connect product capabilities to business problems.

## Data Flow

1. Load stakeholder discovery notes and sample content metadata.
2. Extract solution themes from the discovery notes.
3. Build workflow recommendations matched to business problems, target users, API actions, AI-agent actions, controls, and metrics.
4. Select representative content, including a deliberately unsafe exception.
5. Run the content AI agent and governance policy engine to classify, enrich, link, review, or block items.
6. Evaluate sensitive-review, unsafe-blocking, explainability, and failure-isolation controls.
7. Export a solution brief, demo dashboard, sample workflow run, and audit log.

## Mock versus real integration

The local `ContentPlatformMock` is the provider adapter. Its methods (`get_item`, `update_metadata`, `create_shared_link`, `route_for_approval`, and `export_audit_log`) preserve a shape a real content API could implement, but all links and data are sample-only. The browser API and the fallback use the same output vocabulary. A production adapter would add authentication, tenant scoping, provider retries, rate limits, and an explicit rollback strategy without changing the customer-facing decision contract.

## Security and privacy boundaries

The repository contains no credentials, tokens, customer identifiers, or private content. The unsafe sample uses fictional language and a fake password request; it exists to prove that the workflow can block a request. The browser does not expose raw document text in aggregate views, and the sample shared-link host is `content.example`, not a real platform.
