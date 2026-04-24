# Notifications

Active alerts for CMDBsyncer events. The **channels** (where alerts
land) and **rules** (which events go where) are part of the Community
Edition — you configure them under **Settings → Notifications** in the
admin UI.

Out of the box the syncer can deliver alerts via **email** (using the
same SMTP settings as the rest of the app). Slack, MS Teams and generic
HTTPS webhooks need the [Enterprise notifications
feature](../enterprise/notifications.md), which plugs its extra
dispatchers into the same channel table — the UI layout and fields are
identical, only the delivery adapters live in the enterprise package.

## Channels

One row per destination, reusable across rules.

### Email

Reuses the SMTP settings from `local_config.py` (`MAIL_SERVER`,
`MAIL_PORT`, `MAIL_USERNAME`, …):

| Field                   | Value                                |
| ----------------------- | ------------------------------------ |
| name                    | `ops-mail`                           |
| type                    | `email`                              |
| email_recipients        | `alice@example.com, ops@example.com` *(empty = deliver to each matched contact's own address)* |
| email_subject_prefix    | `[CMDBsyncer]` *(optional)*          |

### Slack, MS Teams, Generic webhook

Entries for those types only appear in the **type** dropdown when the
enterprise package is installed and licensed. Full field reference and
examples live in [Enterprise →
Notifications](../enterprise/notifications.md#channels).

## Rules

Under **Settings → Notifications → Rules**. Each rule matches an
incoming event and names one or more channels to dispatch it through.

| Field                 | Meaning                                                         |
| --------------------- | --------------------------------------------------------------- |
| `name`                | Human identifier                                                |
| `priority`            | Lower numbers evaluate first                                    |
| `continue_after_match`| If off (default), the first matched rule stops evaluation       |
| `event_type_match`    | Regex on `event_type` (empty = any)                             |
| `severity_min`        | Only events at or above this severity fire the rule             |
| `source_match`        | Regex on the `source` (`cron`, `audit`, `test`, …)              |
| `target_match`        | Regex on the target name (e.g. account name, group name)        |
| `outcome_match`       | `failure` to restrict to failures                               |
| `channels`            | List of channels to dispatch through                            |
| `title_template`      | Jinja; has access to the full event dict *(Enterprise)*         |
| `message_template`    | Jinja; same *(Enterprise)*                                      |
| `cooldown_minutes`    | Same dedup key is silent for this long after firing *(Enterprise)* |
| `max_per_hour`        | Hard cap per rule per hour *(Enterprise)*                       |

Rules always store every field above, so installing the enterprise
package later picks up templates and rate limits configured in advance
without any migration.

## Delivery

The community edition fires matching rules directly via the **email**
channel dispatcher. Channels of any other type are stored as
configuration but only dispatch when the [Enterprise notifications
feature](../enterprise/notifications.md) is active — the enterprise
dispatcher is what renders Jinja templates, applies cooldown/rate
limits, and sends to Slack / Teams / generic webhook endpoints.

See the enterprise page for the event-source table, troubleshooting
tips, and the detailed payload shapes for each channel type.
