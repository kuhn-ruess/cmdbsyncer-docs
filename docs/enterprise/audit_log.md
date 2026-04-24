# Audit Log

Requires the [Enterprise Edition](index.md).

## What it does

The Audit Log is an **append-only, immutable** record of every
security- and compliance-relevant event in CMDBsyncer. It answers
questions like:

- *Who changed which Account yesterday?*
- *When was this Secret Binding created, and by whom?*
- *Which IP tried to trigger our webhook without a valid token?*
- *Did the admin rotate the webhook token last Tuesday, or did they
  change something else?*

Records are stored in their own Mongo collection, never updated,
never deleted from the admin UI — the view explicitly disables
create, edit, and delete. A dedicated retention action is available
for pruning, and that prune itself is audited.

Designed for ISO 27001 / SOC 2 evidence packs, 4-eyes security
reviews, and forensic post-mortems.

## What gets recorded automatically

### Login events

| Event                 | When                                              |
| --------------------- | ------------------------------------------------- |
| `user.login.success`  | After a successful login (local, LDAP, or SSO)    |
| `user.login.failure`  | Wrong password / user disabled / OTP missing or invalid / LDAP hook failed |
| `user.logout`         | After an explicit logout via the UI               |

Login events carry `metadata.method = local | ldap | remote_user`
and `metadata.mfa = true|false` on success; failures carry
`metadata.reason = wrong_password | user_disabled | otp_missing | otp_invalid | hook_exception`.

### Webhook events

| Event                 | When                                                        |
| --------------------- | ----------------------------------------------------------- |
| `webhook.triggered`   | A `POST /api/v1/syncer/cron/trigger/<group>` was accepted   |
| `webhook.rejected`    | The same call was rejected (token mismatch / webhook disabled) |

Rejected events include the source IP, so security teams can
correlate repeated failures with scan activity.

### CRUD on tracked models

Any create / update / delete on these collections:

- `Account`
- `User`
- `CronGroup`
- `Config`
- `CustomAttributeRule`
- `Rule` (syncer rules)
- `SecretStore`
- `AccountSecretBinding`

Event names follow `<model>.<action>`, e.g. `account.created`,
`user.updated`, `secret_store.deleted`.

**Field-level diffs** — every `*.updated` entry carries a
`changes` dictionary shaped as `{field: {before: X, after: Y}}`,
so you see *exactly* what was modified.

**Redacted fields** — these never appear in before/after pairs;
the diff records `***REDACTED***` instead so the fact *that* they
changed is preserved, but the value is not:

- `password`, `password_crypted`
- `webhook_token`
- `master_password_env`, `vault_token_env`
- `tfa_secret`, `totp_secret`

**Ignored fields** — these flap every save and would only add
noise; they are excluded from diffs entirely:

- `last_login`, `date_password`
- `last_start`, `last_ended`, `last_success_at`, `next_run`
- `is_running`, `last_message`, `all_messages`, `pid`
- `run_once_next`

### Not tracked

- `Host` — sync runs produce millions of host saves per day. A
  separate "operational log" already captures host-level activity.
- `LogEntry` — the existing application log is its own collection
  with its own view; audit-logging it would be circular.

## Using the UI

**Admin menu → Audit Log → Audit Log**.

The list view shows, by default, timestamp (UTC), event type,
outcome (green / red badge), actor name, IP, target type and name,
changes, and metadata. Each column is filterable:

- **Event type** — partial match on `account.`, `user.login.`, …
- **Outcome** — filter to `failure` only when responding to an
  incident.
- **Actor** — partial match on email/name, for per-user reviews.
- **Target type / name** — e.g. "everything that happened to
  Account `checkmk-prod`".
- **Actor IP** — useful for scan / brute-force investigations.

**Export** — the toolbar offers CSV and JSON export of the current
filter. Drop the CSV into Excel or into your SIEM evidence folder.

## Retention

The Audit Log is meant to survive. Keeping it forever is safe on
Mongo — one entry is a few hundred bytes, and a busy installation
produces low tens of thousands per month, not millions.

When you *do* need to prune (regulatory maximum retention, disk
pressure), use the **"Prune entries older than 365 days"** bulk
action. It:

1. Deletes all entries older than 365 days.
2. Writes a single `audit.pruned` entry with the cutoff timestamp
   and the number of deleted rows.

So even pruning is auditable. There is no UI or API for deleting
individual entries — this is intentional.

## Fields on each entry

| Field                                                            | Meaning                                                         |
| ---------------------------------------------------------------- | --------------------------------------------------------------- |
| `timestamp`                                                      | UTC datetime with millisecond precision                          |
| `event_type`                                                     | Dot-separated identifier (`account.updated`, `webhook.rejected`) |
| `outcome`                                                        | `success` or `failure`                                           |
| `actor_type`                                                     | `user` / `system` / `cron` / `api_token` / `webhook` / `anonymous` |
| `actor_id` / `actor_name` / `actor_ip`                           | Who did it                                                       |
| `target_type` / `target_id` / `target_name`                      | What was affected                                                |
| `changes`                                                        | `{field: {before, after}}` with sensitive values redacted        |
| `metadata`                                                       | Free-form context (`method`, `reason`, `auth`, …)                |
| `request_method` / `request_path` / `user_agent` / `trace_id`    | HTTP context when triggered from a web request                   |

`trace_id` is pulled from `X-Request-ID`, `X-Cloud-Trace-Context`,
`X-Amzn-Trace-Id`, or `traceparent` — the same header list used by
the [JSON Logging](json_logging.md) feature. Correlate audit entries
with the log stream by matching on the `trace.id` field.

## Streaming to an external SIEM

An optional sibling capability, **Audit SIEM Streaming**, fans
every persisted `AuditEntry` out to one or more external sinks in
real time. The local Mongo collection remains the primary store;
the SIEM is an **additional, write-only** copy that compliance
teams can treat as tamper-evident — even a Mongo-savvy insider
can't retroactively remove entries that already reached the SIEM.

Each sink points at a Syncer **Account** that carries the endpoint
and any token. Configure sinks under **Audit Log → SIEM Sinks** —
the `account` field is a dropdown of existing Accounts. What goes
where on the Account:

| Type             | Account `address` | Account `password`        | Account `custom_fields` |
| ---------------- | ----------------- | ------------------------- | ----------------------- |
| `splunk_hec`     | HEC URL           | HEC token                 | —                       |
| `syslog_tcp`     | hostname          | *(unused)*                | `port` *(default 514)*  |
| `syslog_tls`     | hostname          | *(unused)*                | `port` *(default 6514)* |
| `https_webhook`  | URL               | Bearer token *(optional)* | —                       |

On the sink itself you still set `verify_tls` and the optional
`splunk_index` / `splunk_source` / `splunk_sourcetype`.

Every entry is shipped as ECS-shaped JSON so most SIEMs extract
fields out of the box. Syslog output uses RFC5424 with octet-counted
framing — rsyslog, syslog-ng, and Fluent Bit's syslog input all
accept it.

Delivery is asynchronous (bounded queue, background worker). A
slow or unreachable sink never back-pressures the recorder —
local audit writes happen first and stay consistent; the SIEM copy
is best-effort-plus-logged.

**Example: Splunk HEC sink**

1. In Splunk, **Data Inputs → HTTP Event Collector → New Token**,
   assign to an index like `cmdbsyncer-audit`, copy the token.
2. Create a Syncer Account for Splunk:

    | Field    | Value                                                 |
    | -------- | ----------------------------------------------------- |
    | name     | `splunk-hec`                                          |
    | address  | `https://splunk.example.com:8088/services/collector`  |
    | password | *(the HEC token)*                                     |

3. Create a sink:

    | Field              | Value                 |
    | ------------------ | --------------------- |
    | name               | `splunk-prod`         |
    | type               | `splunk_hec`          |
    | account            | `splunk-hec`          |
    | splunk_index       | `cmdbsyncer-audit`    |
    | splunk_sourcetype  | `cmdbsyncer:audit`    |
    | verify_tls         | `True`                |

**Example: syslog to rsyslog over TLS**

1. Create a Syncer Account for the syslog server:

    | Field            | Value                       |
    | ---------------- | --------------------------- |
    | name             | `syslog-central`            |
    | address          | `rsyslog.example.com`       |
    | custom_fields    | `port: 6514`                |

2. Create a sink:

    | Field       | Value                             |
    | ----------- | --------------------------------- |
    | name        | `rsyslog-central`                 |
    | type        | `syslog_tls`                      |
    | account     | `syslog-central`                  |
    | verify_tls  | `True`                            |

## Emitting custom events

If you extend CMDBsyncer with your own plugin and want it to
participate in audit:

```python
from application.helpers.audit import audit

audit(
    'my_plugin.action_performed',
    target_type='MyObject',
    target_id=str(obj.id),
    target_name=obj.name,
    metadata={'extra': 'context'},
)
```

The call is a no-op in community installs, so your plugin keeps
working there without changes.
