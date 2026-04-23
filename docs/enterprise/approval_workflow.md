# 4-Eyes Approval Workflow

Requires the [Enterprise Edition](index.md).

## What it does

Adds a **second-admin sign-off** gate to mutations on sensitive
resource types. Instead of writing directly to Mongo, a change goes
into a *Pending Changes* queue where a different admin reviews the
diff and approves or rejects it.

Designed for regulated environments where "least privilege" and
"separation of duties" are audit requirements — banking (BaFin,
PCI-DSS), healthcare (HIPAA), public-sector C5, ISO 27001.

Integrates with the rest of the enterprise stack:

- Every submit / approve / reject is written to the
  [Audit Log](audit_log.md).
- Every state change fires into the
  [Notification Routing](notifications.md) pipeline — review
  requests land in #approvers, decisions go back to the requester.
- Sensitive field values (passwords, tokens) are **redacted in the
  diff view** but the real value is kept in the payload so the
  change can still be applied on approval.

## Concepts

### Approval Policies

One row per resource type that should be gated. Types available
out of the box:

| Resource type            | What gating does                                             |
| ------------------------ | ------------------------------------------------------------ |
| `Account`                | New sources, credential changes, target systems              |
| `User`                   | User creation, role grants, disabling                        |
| `CronGroup`              | Scheduling, enabled flag, task composition                   |
| `CustomAttributeRule`    | Rule logic that drives host attributes                       |
| `Rule`                   | Syncer rules (filters, rewrites, actions)                    |
| `SecretStore`            | Vault endpoints, credential configuration                    |
| `AccountSecretBinding`   | Which account pulls from which vault                         |
| `WebhookPolicy`          | HMAC gating on the webhook trigger                           |
| `NotificationChannel`    | Slack/Teams webhook URLs, email recipients                   |
| `NotificationRule`       | Routing rules, who gets alerted                              |
| `BackupConfig`           | Backup destinations, retention, encryption settings          |
| `AuditSink`              | External SIEM targets for audit streaming                    |

### Pending Changes

One row per queued mutation. Carries:

- `operation` — `create` / `update` / `delete`
- `before_payload` / `after_payload` — raw BSON-compatible snapshots
- `requester_id` + `requester_name` — who submitted
- `status` — `pending` / `approved` / `rejected` / `applied` / `error`
- `approver_id` + `approver_name` — who decided (after decision)
- `reject_reason` / `error_message` — populated when relevant

## Setup

1. Global admin goes to **Approvals → Approval Policies → Create**.
2. Pick the resource type to gate, check `enabled`, save.
3. Repeat for every type that should require 4-Eyes.

From that moment on, any admin action on a gated type **stages**
instead of applies. The requester sees:

> Change submitted for approval — another admin must approve it before
> it takes effect.

The original record stays untouched until the decision.

## Reviewing a Pending Change

1. A second admin opens **Approvals → Pending Changes**.
2. The list shows each queued change with:
    - Timestamp (UTC)
    - Resource type + operation (`update Account` etc.)
    - Resource name
    - Requester
    - Status badge
    - **Changes** column — a side-by-side diff of only the fields
      that differ (redacted for secrets)
3. Select the rows and pick:
    - **Approve selected** → the change is applied immediately;
      status becomes `applied`.
    - **Reject selected** → status becomes `rejected`; stays in
      the history for audit.
4. **Hard gate**: the requester cannot approve or reject their
   own submission. The action silently skips those rows and a
   warning flash lists the skipped count.

## Security design

### Same-user gate

Enforced at the action level. The requester's ObjectId is stored
on the `PendingChange` and compared against the current admin. No
amount of role juggling lets you approve your own submission.

### Storage guarantees

- `PendingChange` entries are written before the OSS view returns
  success, so there is no "approved but not queued" state.
- On approval, the change is applied through the raw pymongo driver
  (`replace_one` / `insert_one` / `delete_one`) so nested
  EmbeddedDocuments / ReferenceFields / DictFields round-trip
  byte-for-byte. The admin form's own validation already ran at
  submit time, so the payload is known-good.
- If the apply fails (target got deleted meanwhile, Mongo error,
  etc.), the `PendingChange` moves to status `error` with the
  message — the admin can see what went wrong and re-submit if
  needed.

### Secret redaction

Fields known to hold secrets (`password`, `password_crypted`,
`webhook_token`, `master_password_env`, `vault_token_env`,
`tfa_secret`, `signing_secret`) are **redacted in the admin diff
view** but the real value is kept in the stored payload so
password / token rotations actually apply on approval.

### Excluded collections

Some admin views are intentionally *not* gated — gating them would
either be recursive or would lock operators out of fixing the
feature itself:

- `PendingChange`, `ApprovalPolicy` — the feature's own collections
- `AuditEntry` — already append-only WORM
- `CronStats`, `BackupHistory`, `LogEntry`, `NotificationState` —
  read-only system tables, written by system code, never by users
- `Host` — too high-volume; gate the rules that *produce* host
  changes instead

## Audit trail

Every stage emits its own audit event:

| Event                       | When                                          |
| --------------------------- | --------------------------------------------- |
| `approval.submitted`        | Admin clicked Save on a gated resource        |
| `approval.approved`         | Second admin clicked Approve, apply succeeded |
| `approval.rejected`         | Second admin clicked Reject                    |
| `approval.apply_failed`     | Approval succeeded but the apply step failed  |

Metadata always includes `requester`, `approver` (when decided),
`operation`, `resource_type`, `resource_name`, and the
`pending_change_id` so the audit row links back to the queue
entry.

## Notifications

Routes these events into the notifications dispatcher when the
`notifications` feature is co-licensed:

- `approval.submitted` (severity `warning`) — so the approvers'
  channel pings on every review request.
- `approval.approved` / `approval.rejected` — so the requester
  knows the outcome.

Build a matching rule:

```
event_type_match: ^approval\.submitted$
channels:         [slack-approvers]
title_template:   "Approval needed: {{ details.operation }} {{ details.resource_type }}"
message_template: "{{ details.requester }} submitted a {{ details.operation }} on {{ details.resource_name }}. Please review under Approvals → Pending Changes."
cooldown_minutes: 0
```

## Rollout recommendations

1. **Start small** — gate `SecretStore` and `AccountSecretBinding`
   first; credentials are the most sensitive surface.
2. **Widen to production-facing rules** — `Rule`,
   `CustomAttributeRule`, `CronGroup`.
3. **Add Account** only when the team is used to the queue flow —
   gating Account blocks new-source onboarding on 4-Eyes, which
   is usually desirable but slows down initial rollouts.
4. **Leave Users and Webhook Policies** for last — those changes
   are rare and often urgent (e.g. disabling a compromised user);
   make sure your review workflow is fast before gating them.

## Known limitations

- **Bulk-action reject** uses a fixed reason string. A richer
  "Reject with reason" form is on the roadmap.
- **No automatic cleanup** of old `applied` / `rejected` entries.
  If the queue grows too large, delete old decided rows by date
  with a one-off Mongo script.
- **Dynamic wrapping cache TTL is 5 seconds** — enabling /
  disabling an `ApprovalPolicy` takes effect within 5 s for every
  admin worker, without a restart.
