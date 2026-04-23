# Prometheus Metrics

Requires the [Enterprise Edition](index.md).

## What it does

Exposes a `/metrics` endpoint in the standard Prometheus text format.
Third observability pillar next to [JSON Logging](json_logging.md)
(logs) and the [Audit Log](audit_log.md) (events) — numeric
dashboards, SLO timers, and freshness alerts.

Designed to drop straight into any modern monitoring stack:

- **Prometheus / VictoriaMetrics / Grafana Cloud** — add a scrape job
- **OpenMetrics-compatible agents** (Datadog, New Relic, Dynatrace)
  — configure an OpenMetrics endpoint
- **Alertmanager** — build alerts on the freshness gauges below

## Scrape config

```yaml
scrape_configs:
  - job_name: cmdbsyncer
    metrics_path: /metrics
    scheme: https
    static_configs:
      - targets: ['syncer.example.com']
    authorization:
      type: Bearer
      credentials: ${PROM_TOKEN}      # matches the env-var below
```

## Authentication

```python
# local_config.py
PROMETHEUS_METRICS_TOKEN_ENV = 'PROM_TOKEN'   # env var with the bearer token
```

When `PROMETHEUS_METRICS_TOKEN_ENV` is set:

- The env var must be present on the syncer host.
- Callers must present `Authorization: Bearer <value of env var>`.
- Mismatches → `401`. Missing env var with the key set → `503`
  (fail-closed so a misconfigured deployment doesn't silently
  expose metrics).

If `PROMETHEUS_METRICS_TOKEN_ENV` is left unset the endpoint is
open — intended for scraping from the same pod / node / internal
VPC where network-level isolation is enough.

## Metrics

### Info

| Name                 | Labels                           | Meaning                                      |
| -------------------- | -------------------------------- | -------------------------------------------- |
| `cmdbsyncer_info`    | `customer`, `license_id`, `exp`  | Constant 1 carrying license metadata         |

### Cron groups

One time-series per CronGroup:

| Name                                                      | Meaning                                                  |
| --------------------------------------------------------- | -------------------------------------------------------- |
| `cmdbsyncer_cron_group_enabled`                           | `1` if enabled in UI, else `0`                           |
| `cmdbsyncer_cron_group_running`                           | `1` while a run is in flight                             |
| `cmdbsyncer_cron_group_failure`                           | `1` if the last completed run failed                     |
| `cmdbsyncer_cron_group_last_start_timestamp_seconds`      | Unix timestamp of the last start                          |
| `cmdbsyncer_cron_group_last_end_timestamp_seconds`        | Unix timestamp of the last end                            |
| `cmdbsyncer_cron_group_last_success_timestamp_seconds`    | Unix timestamp of the last **successful** end             |
| `cmdbsyncer_cron_group_last_duration_seconds`             | Duration of the last completed run                        |
| `cmdbsyncer_cron_group_next_run_timestamp_seconds`        | Unix timestamp when the group is next eligible to run     |

### Hosts

| Name                              | Labels | Meaning                                          |
| --------------------------------- | ------ | ------------------------------------------------ |
| `cmdbsyncer_hosts_total`          | —      | Total host documents (excluding object-mode)     |
| `cmdbsyncer_hosts_stale_24h_total`| —      | Hosts not seen by any importer in the last 24 h  |

### Self

| Name                                           | Meaning                                  |
| ---------------------------------------------- | ---------------------------------------- |
| `cmdbsyncer_metrics_scrape_duration_seconds`   | Time this scrape spent building the body |
| `cmdbsyncer_scrape_error`                      | `1` if the scrape failed (only emitted then) |

## Example alerts

**Sync hasn't succeeded in 90 minutes** — combines `last_success_timestamp_seconds`
with wall clock:

```yaml
- alert: CmdbSyncerCronStale
  expr: time() - cmdbsyncer_cron_group_last_success_timestamp_seconds > 5400
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: 'CMDBsyncer cron group {{ $labels.group }} has not succeeded for 90 min'
```

**Last run failed**:

```yaml
- alert: CmdbSyncerCronFailure
  expr: cmdbsyncer_cron_group_failure == 1
  for: 1m
  labels:
    severity: error
  annotations:
    summary: 'CMDBsyncer cron group {{ $labels.group }} failed its last run'
```

**Hosts rotting** (importer is silent):

```yaml
- alert: CmdbSyncerStaleHosts
  expr: cmdbsyncer_hosts_stale_24h_total > 10
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: '{{ $value }} hosts have not been seen by any importer in the last 24h'
```

## Design notes

- Metrics are built **on scrape** from the Mongo state. No
  in-process counters to persist; HA-safe across replicas.
- Scrape cost scales linearly with the number of CronGroups
  (one query + one loop). At typical sizes (< 1000 groups) a
  single scrape is well under 100 ms.
- Counters for "events since start" (audit, notifications, webhook
  triggers) are deliberately **not** exposed here — they depend
  on in-process state that doesn't survive a restart and would
  diverge between replicas. Use the [Audit Log](audit_log.md)
  CSV export or your JSON-log aggregator for that axis.
