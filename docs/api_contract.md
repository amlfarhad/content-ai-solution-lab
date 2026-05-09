# API Contract

The mock platform exposes a small set of operations that are common in enterprise content workflows.

## `get_item(item_id)`

Returns a content object by ID. Raises a clear error for an unknown ID.

## `update_metadata(item_id, **metadata)`

Adds or overwrites metadata fields on a content object and writes an audit event.

## `create_shared_link(item_id, audience)`

Creates a deterministic shared-link URL for demo purposes and writes an audit event.

## `route_for_approval(item_id, approver)`

Creates a pending approval packet with the approver email and writes an audit event.

## `export_audit_log(path)`

Writes the audit trail to JSON so a solutions engineer can show governance and traceability in the demo.

