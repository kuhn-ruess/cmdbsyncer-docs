# Syncer Endpoints

Base path: `/api/v1/syncer` — needs the API role `syncer` or `all`.

These endpoints monitor syncer operations and trigger cron groups from the
outside. The official Checkmk syncer monitoring plugins use them to check job
status and last run times, see [Monitor the Syncer](../basics/monitoring.md).

---

## `GET /api/v1/syncer/logs`

The latest 100 log messages, newest first.

```bash
curl -u "user:password" \
     https://cmdbsyncer.example.com/api/v1/syncer/logs
```

```json
{
  "result": [
    {
      "entry_id": "6620f1c2a3b4c5d6e7f80912",
      "time": "2026-04-26 17:55:00",
      "message": "Checkmk Export finished",
      "source": "checkmk",
      "details": [{"name": "info", "message": "Updated 42 hosts"}],
      "has_error": false
    }
  ]
}
```

`has_error` is true as soon as one detail line is on error level — that is the
field to alert on.

---

## `GET /api/v1/syncer/services/<service_name>`

The most recent log entry of one component. `service_name` is the source ident
written to the log, e.g. `checkmk`, `netbox` or `API`.

```bash
curl -u "user:password" \
     https://cmdbsyncer.example.com/api/v1/syncer/services/checkmk
```

The answer is a single entry in the same shape as above, below `result`. A
component that has never logged anything answers `404`.

---

## `GET /api/v1/syncer/cron/`

Status of every cron group. Mind the trailing slash.

```bash
curl -u "user:password" \
     https://cmdbsyncer.example.com/api/v1/syncer/cron/
```

```json
{
  "result": [
    {
      "name": "Import Nightly",
      "last_start": "2026-04-26 17:50:00",
      "next_run": "2026-04-26 18:00:00",
      "is_running": false,
      "last_message": "Done in 42s",
      "has_error": false
    }
  ]
}
```

---

## `POST /api/v1/syncer/cron/`

Schedule one extra run of a cron group on the next cron pass, outside its normal
interval.

| Field | Required | Description |
|---|---|---|
| `job_name` | yes | Name of the cron group |
| `run_once_next` | yes | `true` schedules the extra run, `false` clears the flag |

```bash
curl -u "user:password" \
     -H "Content-Type: application/json" \
     -d '{"job_name": "Import Nightly", "run_once_next": true}' \
     https://cmdbsyncer.example.com/api/v1/syncer/cron/
```

```json
{"status": "saved"}
```

An unknown group name answers `404`.

---

## `POST /api/v1/syncer/cron/trigger/<group_name>`

Webhook that schedules a cron group to run on the next pass. This is the
endpoint for external systems (GitHub, Jenkins, Netbox hooks, …) that should
fire a sync when something changed on their side.

Three ways to authenticate, in this order:

1. an **Enterprise webhook signature policy**, when one is attached to the group
   (see [Webhook Signatures](../enterprise/webhook_signatures.md));
2. a per-group **`X-Webhook-Token`** header — the token is generated on the cron
   group and needs no user account;
3. normal **user credentials**, checked against the caller's API roles.

```bash
curl -X POST \
     -H "X-Webhook-Token: <token of the cron group>" \
     https://cmdbsyncer.example.com/api/v1/syncer/cron/trigger/Import%20Nightly
```

```json
{
  "status": "triggered",
  "group": "Import Nightly",
  "note": "Group will run on the next cron pass."
}
```

The answer is `202` — the run is scheduled, not executed while you wait.

| Code | Reason |
|---|---|
| `401` | Token does not match, or no valid credentials |
| `403` | The webhook is not enabled for this cron group |
| `404` | No cron group with that name |
| `409` | The cron group is disabled and cannot run |

Every trigger and every rejection is written to the log with source `API`.

---

## `GET /api/v1/syncer/hosts`

Aggregate counters, the usual base for a monitoring check.

```bash
curl -u "user:password" \
     https://cmdbsyncer.example.com/api/v1/syncer/hosts
```

```json
{
  "24h_checkpoint": "2026-04-25 17:55:00",
  "num_hosts": 12043,
  "num_objects": 512,
  "not_updated_last_24h": 7
}
```

`not_updated_last_24h` counts hosts no import has seen for 24 hours — a rising
number means an importer stopped delivering. For a user
[restricted to accounts](index.md#restricting-a-user-to-accounts) the counters
only cover the hosts that user may reach.

---

## `GET /api/v1/syncer/eda`

Events of [Event Driven Ansible](../ansible/eda.md#repeated-events) that are
sent again and again without effect. Made for a monitoring check: the
counters work with plain thresholds, the list names the hosts.

| Parameter | Meaning |
| :-------- | :------ |
| `account` | Only this EDA account |
| `min_sends` | Count a streak as repeating from this many sends on, instead of the `repeat_threshold` of each account (at least 1) |
| `limit` | Most entries in `offenders` (default 100, `0` returns only the counters) |

```bash
curl -u "user:password" \
     https://cmdbsyncer.example.com/api/v1/syncer/eda
```

```json
{
  "result": {
    "events_24h": 14,
    "failed_24h": 2,
    "pending": 3,
    "repeating": 2,
    "repeating_hosts": 1,
    "failing": 1,
    "max_sends": 5,
    "min_sends": null,
    "accounts": [
      {
        "account": "eda",
        "events_24h": 14,
        "failed_24h": 2,
        "pending": 3,
        "repeating": 2,
        "repeating_hosts": 1,
        "failing": 1,
        "max_sends": 5
      }
    ],
    "offenders": [
      {
        "account": "eda",
        "hostname": "srv01",
        "event": "register_agent_tls",
        "rule": "Register TLS",
        "rule_id": "6720f1c2a3b4c5d6e7f80912",
        "sends": 5,
        "failures": 0,
        "threshold": 3,
        "first_sent": "2026-10-09 06:00:00",
        "last_sent": "2026-10-13 06:00:00",
        "last_status": "success",
        "last_http_status": 200
      }
    ],
    "offenders_truncated": false
  }
}
```

| Field | Meaning |
| :---- | :------ |
| `events_24h`, `failed_24h` | Events sent in the last 24 hours, and how many of them the event stream did not accept |
| `pending` | Open streaks below the threshold: the event went out, the host still matches |
| `repeating` | Open streaks at or above the threshold: the event went out again and again, the host still matches |
| `repeating_hosts` | Hosts with at least one repeating event |
| `failing` | Open streaks whose last send failed (event stream down, token wrong) |
| `max_sends` | Most sends of one open streak |
| `accounts` | The same counters per EDA account |
| `offenders` | The repeating streaks, most sends first |

Times are local time of the Syncer. For a user
[restricted to accounts](index.md#restricting-a-user-to-accounts) the
counters and the list only cover the hosts that user may reach.
