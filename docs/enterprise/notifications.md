# Notification Routing

Requires the [Enterprise Edition](index.md).

## What it does

The channel table and the rule table [live in the community
edition](../advanced/notifications.md) — OSS ships the UI plus email
delivery. The **Enterprise notifications feature** adds the missing
pieces so rules turn CMDBsyncer's internal events into **active
alerts** on the channels your team already uses:

- Extra channel types: **Slack**, **MS Teams**, and a **generic HTTPS
  webhook** (with optional HMAC-SHA256 signing).
- The dispatcher that actually fires rules: Jinja template rendering,
  dedup, cooldown and rate limits, plus a bounded background queue so
  slow Slack/SMTP endpoints never back-pressure logins or cron ticks.
- Audit-event relay: every entry the audit recorder persists is
  forwarded into the dispatcher, so rules can match login failures
  or webhook rejections without a code change.

Complements [JSON Logging](json_logging.md) (passive: logs flow into
your aggregator) by pushing the **important** events — a failed cron
group, a rejected webhook attempt, a missing secret — directly at a
human, in real time.

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
[`audit_log`](audit_log.md) feature is co-licensed** — the audit
recorder forwards persisted entries into the dispatcher without any
plugin change.

## Channels

Configured under **Settings → Notifications → Channels** — the same
screen OSS provides. With the enterprise package installed, the `type`
dropdown gains the non-email options below.

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

Email delivery works without the enterprise package — see
[community Notifications](../advanced/notifications.md#email). When
both packages are active, the enterprise dispatcher uses the same
channel row so Jinja templates and cooldown apply to email too.

### Generic HTTPS webhook

Raw JSON POST to your own endpoint. Optional HMAC-SHA256 signing
(GitHub-/Stripe-style) with the secret drawn from an Account's
password (authoritative credential store, not env vars):

| Field                      | Value                                                        |
| -------------------------- | ------------------------------------------------------------ |
| name                       | `pagerduty-primary`                                          |
| type                       | `webhook`                                                    |
| webhook_url                | `https://events.pagerduty.com/v2/enqueue`                    |
| signing_secret_account     | `pagerduty-hmac` *(Account name; its password is the HMAC secret)* |
| extra_headers              | `{"Authorization": "Bearer ..."}` *(dict, optional)*         |

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

When a signing Account is set, an `X-Signature-SHA256: sha256=<hex>`
header is added — the receiver verifies with HMAC-SHA256 over the
request body. Existing installs that stored an env-var name in
`webhook_secret_env` still work for backwards compatibility.

### Testing a channel

Select one or more channels in the list view and pick the
**"Send test notification"** bulk action. A minimal message is
dispatched immediately, and any per-channel failure surfaces as a
flash message so you know which endpoint is misconfigured *before*
a real incident.

## Rules

The full field reference is on the [OSS Notifications
page](../advanced/notifications.md#rules). The enterprise dispatcher
is what gives the Jinja templates and rate-limit fields their meaning:

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
that the event's `severity` is at least `severity_min`. Audit events
flow only when `audit_log` is also licensed.

**Events arrive but no mentions**  
`slack_mention` must be Slack-formatted. `@alice` works only in
the channel message body; for a group, use `<!subteam^Sxxx>`; for
channel-wide alerts, `<!here>` or `<!channel>`.

**Webhook receiver says the signature is wrong**  
Verify `signing_secret_account` points to an Account whose password
matches the receiver's secret. The signature is computed over the
**raw body bytes** (`data=body`), not a re-serialised JSON.

**Slack / Teams / Webhook type doesn't appear in the channel dropdown**  
The enterprise package is either not installed or its license is
invalid/expired. The OSS channel UI only exposes `email` on its own.
