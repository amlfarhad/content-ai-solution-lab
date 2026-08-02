# Content AI Solution Lab

Customer-facing solutions engineering workspace for AI content workflows.

Content AI Solution Lab turns stakeholder discovery notes and enterprise content metadata into an inspectable customer workflow: requirements, API/data mapping, deterministic classification, governance controls, human review, policy exceptions, evaluation evidence, a handoff plan, and a browser-ready operations view.

The primary artifact is a no-login sample engagement for a solutions engineer. It is explicit about what is real in the repository and what is simulated: the mock content provider preserves integration-shaped contracts, while the policy engine keeps decisions deterministic and explainable without tenant credentials or an external model.

## Platform Capabilities

- Discovery-to-solution mapping for Legal, Finance, People, Security, and IT stakeholders.
- API-like content operations for metadata updates, shared links, approval routing, and audit export.
- Deterministic AI-agent logic for classification, retention-policy recommendation, summarization, and approver selection.
- Customer-facing outputs: interactive operations workbench, solution brief, dashboard, workflow run, and audit log.
- Reproducible tests covering catalog search, discovery analysis, API contracts, classification/routing, governance rules, failures, evaluation controls, and the browser journey.

## Solution Workflow

1. Load stakeholder discovery notes and sample content metadata.
2. Extract business themes such as automation, governance, AI, search, and analytics.
3. Map the themes to recommended workflows, target users, API actions, AI-agent actions, governance controls, and success metrics.
4. Run the content AI agent against sensitive items to classify documents, recommend retention policies, summarize content, and route approvals.
5. Evaluate the sample run: automatic processing, human-review routing, blocked policy conflicts, failure isolation, and audit evidence.
6. Close with API mapping, pilot measures, security/privacy boundaries, and a phased implementation handoff.

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
content-solution web --port 8765
```

Open `http://127.0.0.1:8765/` for the no-login browser workbench. The same app can be served with `python -m content_ai_solution_lab.web --port 8765`.

The deployed public product is [content-ai-solution-lab.vercel.app](https://content-ai-solution-lab.vercel.app). It includes a visible GitHub source link and uses the Python API when available, with a clearly labeled seeded browser fallback for static-only environments.

The demo command writes:

- `reports/solution_brief.md`
- `reports/demo_dashboard.html`
- `reports/agent_audit_log.json`
- `reports/sample_workflow_run.json`

## Browser verification

The repository includes a black-box Playwright journey at `tests/browser_journey.py`. With Playwright available, run it through the server lifecycle helper:

```bash
python /Users/amlfarhad/.agents/skills/webapp-testing/scripts/with_server.py \
  --server "python3 -m content_ai_solution_lab.web --port 8765" --port 8765 \
  -- python3 tests/browser_journey.py
```

The journey exercises the seeded sample selection, the automatic/review/blocked operations queues, degraded-provider recovery, and empty-selection validation. It writes a screenshot to `artifacts/browser_journey.png`.

## Workflow configuration

The workbench exposes two execution modes rather than treating configuration as decorative:

- **Simulation** runs the mock provider contract in memory, records metadata/link/approval audit events, and shows the resulting operations queues.
- **Dry run** evaluates the same policy logic but projects metadata, links, and approvals without mutating the mock provider or writing audit events.

The acceptance controls and their limits are documented in [`docs/evaluation.md`](docs/evaluation.md).

## Public demo boundaries

- The current provider is a deterministic mock. It has no customer credentials, no private tenant, and no production content.
- `https://content.example/shared/...` URLs are deterministic placeholders and do not resolve to real content.
- `CNT-1006` is an intentionally unsafe sample exception containing credential, approval-bypass, external-sharing, and production-access signals. The policy engine routes it to `security-escalation`, blocks automatic links, and creates a `blocked_pending_review` packet.
- Evaluation results demonstrate control behavior on the sample catalog. They do not claim customer deployments, measured business impact, or proprietary platform integrations.
- The Vercel configuration provides a Python API function plus a browser fallback so the public artifact remains inspectable if serverless Python is unavailable.

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
- **Customer-ready outputs:** the browser workbench, solution brief, dashboard, sample run, success metrics, and demo steps are designed for stakeholder presentation.
