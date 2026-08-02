# API Contract

The mock platform exposes a small set of operations that are common in enterprise content workflows.

## `get_item(item_id)`

Returns a content object by ID. Raises a clear error for an unknown ID.

## `update_metadata(item_id, **metadata)`

Adds or overwrites metadata fields on a content object and writes an audit event.

## `create_shared_link(item_id, audience)`

Creates a deterministic shared-link URL for demo purposes and writes an audit event.

## `route_for_approval(item_id, approver, status="pending_review", reason="")`

Creates a review packet with the approver email, status, and optional reason, then writes an audit event. `status` is `pending_review` for a normal human gate or `blocked_pending_review` for a policy conflict.

## `export_audit_log(path)`

Writes the audit trail to JSON so a solutions engineer can show governance and traceability in the demo.

## Browser API

The dependency-free web server exposes the same data through JSON endpoints. Every endpoint is local/mock unless deployed as the repository's public demo.

### `GET /api/health`

Returns provider name, deterministic mode, and whether credentials are required.

### `GET /api/scenario`

Returns the customer, industry, discovery signals, extracted themes, requirements, catalog summary, workflow recommendations, handoff phases, API mapping, and explicit demo boundaries.

### `GET /api/content?department=&sensitivity=&query=`

Returns representative content metadata after optional exact department/sensitivity filters and token-based query matching. The response shape is `{ "items": [...], "total": number }`.

### `GET /api/content/{item_id}/evaluation`

Returns one content item and its deterministic governance decision. A decision includes `classification`, `retention_policy`, `confidence`, `disposition`, `risk_level`, `approver`, `rationale`, `next_action`, `link_policy`, `policy_flags`, and `detected_signals`.

### `POST /api/run`

Accepts `{ "item_ids": ["CNT-1001"], "mode": "simulation" }`. The server returns a deterministic `run_id`, summary counts, per-item results, evaluation controls, and the audit log. `mode` may be `simulation` or `dry_run`: simulation applies mock provider actions in memory, while dry run returns projected actions and writes no metadata, links, approvals, or audit events. Invalid payloads return `400` or `422`; unknown item IDs are isolated as `failed` results so mixed runs can return `status: partial`.

### Disposition contract

- `auto_process`: apply metadata and create an internal-only deterministic shared link.
- `needs_review`: apply metadata and route a `pending_review` packet to the mapped approver; no link is created.
- `blocked`: apply only trace metadata and route a `blocked_pending_review` packet to Security; no link is created.
