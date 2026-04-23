# Notification Routing

Requires the [Enterprise Edition](index.md).

## What it does

Turns CMDBsyncer's internal events into **active alerts** on the
channels your team already uses — Slack, MS Teams, email, or any
HTTPS webhook. Rule-based routing with dedup, cooldown, and rate
limits; payloads are rendered through Jinja templates so the text
your on-call receives is exactly what they want to see.

Complements [JSON Logging](json_logging.md) (passive: logs flow
into your aggregator) by pushing the **important** events — a
failed cron group, a rejected webhook attempt, a missing secret —
directly at a human, in real time.

## Event sources

| Event type                       | Fired by                                              |
| -------------------------------- | ----------------------------------------------------- |
| `cron.group.failed`              | A cron group ended with at least one failed task      |
| `cron.group.recovered`           | A previously-failing group ran clean again            |
| `user.login.failure`             | Login attempt rejected (via audit relay)              |
| `user.login.success`             | Login accepted (via audit relay)                      |
| `webhook.rejected`               | `cron/trigger` API call rejected (token mismatch etc.) |
| `webhook.triggered`              | A webhook successfully triggered a group              |
| `account.created` / `*.updated` / `*.deleted` | Account / User / Rule / Secret mutations (via audit relay) |

Events via "audit relay" are routed automatically **only when the
`audit_log` feature is co-licensed** — the audit recorder forwards
persisted entries into the dispatcher without any plugin change.

## Channels

Configured under **Notifications → Channels**. One row per
destination, reusable across rules.

### Slack

1. In Slack, **Apps → Incoming Webhooks → Add to Slack**, pick a
   channel, copy the webhook URL.
2. In CMDBsyncer, create a channel:

    | Field                | Value                                                  |
    | -------------------- | ------------------------------------------------------ |
    | name                 | `slack-ops`                                            |
    | type                 | `slack`                                                |
    | webhook_url          | *(paste the Slack URL)*                                |
    | slack_channel        | *(optional override, e.g. `#cmdb-alerts`)*             |
    | slack_mention        | *(optional, e.g. `<!here>`, `@netops`, `<!subteam^Sxxx>`)* |

Messages are Block Kit with severity-coloured headers and emoji:
:information_source: info, :warning: warning, :x: error,
:rotating_light: critical.

### MS Teams

1. In Teams, **Connectors → Incoming Webhook** (or a Workflows-based
   webhook on MS 365 tenants), copy the URL.
2. In CMDBsyncer, create a channel with `type=msteams` and that URL.

Messages are Adaptive Cards with severity-coloured titles and a
`FactSet` of the event details.

### Email

Reuses the SMTP settings from `local_config.py` (`MAIL_SERVER`,
`MAIL_PORT`, `MAIL_USERNAME`, …). Only set:

| Field                   | Value                                |
| ----------------------- | ------------------------------------ |
| email_recipients        | `alice@example.com, ops@example.com` |
| email_subject_prefix    | `[CMDBsyncer]` *(optional)*          |

### Generic HTTPS webhook

Raw JSON POST to your own endpoint. Optional HMAC-SHA256 signing
(GitHub-/Stripe-style):

| Field                | Value                                                        |
| -------------------- | ------------------------------------------------------------ |
| name                 | `pagerduty-primary`                                          |
| type                 | `webhook`                                                    |
| webhook_url          | `https://events.pagerduty.com/v2/enqueue`                    |
| webhook_secret_env   | `NOTIF_WEBHOOK_SECRET` *(env var; used for X-Signature-SHA256)* |
| extra_headers        | `{"Authorization": "Bearer ..."}` *(dict, optional)*         |

Body shape:

```json
{
  "timestamp": 1729678800,
  "payload": {
    "event_type": "cron.group.failed",
    "severity": "error",
    "title": "...",
    "message": "...",
    "source": "cron",
    "details": { "group": "prod-cmk-sync" }
  }
}
```

When `webhook_secret_env` is set, an `X-Signature-SHA256: sha256=<hex>`
header is added — the receiver verifies with HMAC-SHA256 over the
request body.

### Testing a channel

Select one or more channels in the list view and pick the
**"Send test notification"** bulk action. A minimal message is
dispatched immediately, and any per-channel failure surfaces as a
flash message so you know which endpoint is misconfigured *before*
a real incident.

## Rules

Under **Notifications → Rules**. Each rule matches events to channels.

| Field                 | Meaning                                                         |
| --------------------- | --------------------------------------------------------------- |
| `name`                | Human identifier                                                |
| `priority`            | Lower numbers evaluate first                                    |
| `continue_after_match`| If off (default), the first matched rule stops evaluation       |
| `event_type_match`    | Regex on `event_type` (empty = any)                             |
| `severity_min`        | Only events at or above this severity fire the rule             |
| `source_match`        | Regex on the `source` (`cron`, `audit`, `test`, ...)            |
| `target_match`        | Regex on the target name (e.g. account name, group name)        |
| `outcome_match`       | `failure` to restrict to failures                               |
| `channels`            | List of channels to dispatch through                            |
| `title_template`      | Jinja; has access to the full event dict                        |
| `message_template`    | Jinja; same                                                     |
| `cooldown_minutes`    | Same `dedup_key` is silent for this long after firing           |
| `max_per_hour`        | Hard cap per rule per hour                                      |

**Example rule — prod cron failures to PagerDuty + Slack:**

| Field                | Value                                                   |
| -------------------- | ------------------------------------------------------- |
| name                 | `Prod cron failures`                                    |
| priority             | `10`                                                    |
| event_type_match     | `^cron\.group\.failed$`                                 |
| source_match         | `^cron$`                                                |
| target_match         | `^prod-`                                                |
| severity_min         | `error`                                                 |
| channels             | `slack-ops`, `pagerduty-primary`                        |
| title_template       | `{{ title }}`                                           |
| message_template     | `{{ message }}\nLast success: {{ details.last_success_ago or "never" }}` |
| cooldown_minutes     | `15`                                                    |
| max_per_hour         | `6`                                                     |

## Dedup, cooldown, rate limits

Per dedup-key (defaults to `rule:<id>:<event_type>`, or the
`dedup_key` the event carries):

- After a dispatch, the same key is silent for `cooldown_minutes`.
- A rolling 1-hour window enforces `max_per_hour`. Excess events
  are counted in `NotificationState.suppressed_count` so the next
  allowed message can include a "(+N more suppressed)" footer in a
  future release.
- `NotificationState` is TTL-indexed — stale keys self-expire after
  24 hours of inactivity.

## Delivery semantics

Dispatch runs on a background thread with a bounded queue (1000
pending events). A slow Slack/SMTP endpoint never back-pressures
logins or cron ticks. Queue overflow is logged and dropped — tune
the queue size in `dispatcher.py` if your event rate is unusually
high.

## Troubleshooting

**Channel test succeeds but real events never arrive**  
Check that a matching rule is `enabled`, that its `priority` isn't
buried under a stricter rule with `continue_after_match=False`, and
that the event's `severity` is at least `severity_min`. Audit
events flow only when `audit_log` is also licensed.

**Events arrive but no mentions**  
`slack_mention` must be Slack-formatted. `@alice` works only in
the channel message body; for a group, use `<!subteam^Sxxx>`; for
channel-wide alerts, `<!here>` or `<!channel>`.

**Webhook receiver says the signature is wrong**  
Verify `webhook_secret_env` points to the same secret on both
sides. The signature is computed over the **raw body bytes**
(`data=body`), not a re-serialised JSON.
