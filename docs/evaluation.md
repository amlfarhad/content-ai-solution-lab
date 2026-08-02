# Evaluation Criteria

The sample engagement is accepted on control behavior, not on a claimed customer KPI. A run must make the decision path inspectable and keep unsafe actions from becoming automatic side effects.

## Acceptance controls

| Control | Pass condition | Evidence in the run |
| --- | --- | --- |
| Sensitive review | Confidential and restricted items never receive an automatic link. | `needs_review` disposition and mapped approver. |
| Unsafe blocking | Credential, access, external-sharing, or approval-bypass signals route to Security and stop link creation. | `blocked` disposition, policy flags, `blocked_pending_review`. |
| Explainable routing | Every processed item exposes classification, retention, confidence, rationale, flags, and next action. | Per-item `decision` object and decision-detail panel. |
| Failure isolation | An unknown item does not hide successful decisions for other selected items. | `status: partial`, failed item record, preserved successful results. |
| Dry-run safety | A dry run projects metadata and downstream actions without writing mock metadata, links, approvals, or audit events. | `mode: dry_run`, projected actions, empty audit log. |

## What this does not measure

- Approval-cycle reduction, search time, adoption, or any other customer business impact.
- Model accuracy against a labeled production corpus.
- Security compliance for a real tenant or provider.

Those measures belong in a customer pilot after source IDs, owner mappings, policy definitions, and authenticated provider contracts are confirmed. The handoff view names them as pilot questions instead of presenting sample control passes as business results.
