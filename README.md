# Content AI Solution Lab

Customer-facing solutions engineering workspace for AI content workflows.

Content AI Solution Lab turns stakeholder discovery notes and enterprise content metadata into a complete demo package: workflow recommendations, API actions, AI-agent decisions, governance controls, success metrics, a solution brief, an audit log, and an HTML dashboard.

## Platform Capabilities

- Discovery-to-solution mapping for Legal, Finance, People, Security, and IT stakeholders.
- API-like content operations for metadata updates, shared links, approval routing, and audit export.
- Deterministic AI-agent logic for classification, retention-policy recommendation, summarization, and approver selection.
- Customer-facing outputs: solution brief, demo dashboard, and audit log.
- Reproducible tests covering catalog search, discovery analysis, AI-agent behavior, and scenario generation.

## Solution Workflow

1. Load stakeholder discovery notes and sample content metadata.
2. Extract business themes such as automation, governance, AI, search, and analytics.
3. Map the themes to recommended workflows, target users, API actions, AI-agent actions, governance controls, and success metrics.
4. Run the content AI agent against sensitive items to classify documents, recommend retention policies, summarize content, and route approvals.
5. Generate a customer-ready solution brief, dashboard, and audit log.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m unittest discover -s tests
content-solution catalog
content-solution discovery
content-solution agent CNT-1001
content-solution demo
```

The demo command writes:

- `reports/solution_brief.md`
- `reports/demo_dashboard.html`
- `reports/agent_audit_log.json`

## Example Agent Output

```json
{
  "classification": {
    "classification": "legal-review",
    "retention_policy": "contract-lifecycle",
    "confidence": "high"
  },
  "approval": {
    "approver": "legal-ops@example.com",
    "status": "pending_review"
  }
}
```

## Architecture Decisions

- **Separation of concerns:** discovery analysis, platform actions, AI-agent behavior, and demo generation are isolated and testable.
- **Deterministic AI behavior:** recommendations are reproducible and explainable without requiring external model credentials.
- **Governance-first workflow design:** auditability, sensitivity, and retention policies are handled as core product requirements.
- **Customer-ready outputs:** the solution brief, dashboard, success metrics, and demo steps are designed for stakeholder presentation.
