# content-ai-solution-lab

Customer-facing solutions engineering lab for AI content workflows. The project turns stakeholder discovery notes into a product demo: content catalog review, AI-agent classification, metadata enrichment, approval routing, audit logging, solution brief generation, and an HTML dashboard.

The goal is to demonstrate the work behind a strong Associate Solutions Engineer conversation: active listening, mapping business problems to product capabilities, using APIs, explaining AI workflows, and presenting a governed rollout plan.

## What It Shows

- Discovery-to-solution mapping for Legal, Finance, People, Security, and IT stakeholders.
- API-like content operations for metadata updates, shared links, approval routing, and audit export.
- Deterministic AI-agent logic for classification, retention-policy recommendation, summarization, and approver selection.
- Customer-facing outputs: solution brief, demo dashboard, and audit log.
- Reproducible tests covering catalog search, discovery analysis, AI-agent behavior, and scenario generation.

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

## Interview Talking Points

- I separated discovery, platform actions, AI-agent behavior, and demo generation so each part is explainable and testable.
- I kept the AI behavior deterministic because the point is to show solution design and governance, not hide logic behind a model call.
- I treated auditability, sensitivity, and retention as product requirements rather than afterthoughts.
- I built outputs a solutions engineer could use with a customer: a talk track, dashboard, success metrics, and governance controls.

