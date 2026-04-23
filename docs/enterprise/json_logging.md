# JSON Logging

Requires the [Enterprise Edition](index.md).

## What it does

With the `json_logging` feature enabled, every log line coming out of
CMDBsyncer is a single-line JSON document shaped according to the
[Elastic Common Schema (ECS)](https://www.elastic.co/guide/en/ecs/current/).

That makes it drop-in for modern cloud log pipelines:

- **Kubernetes / Docker** — stdout is already captured by the
  container runtime; Fluent Bit, Vector or Promtail scrape it without
  any parser configuration.
- **Elastic / OpenSearch** — the ECS field names match the default
  Kibana / Discover dashboards out of the box.
- **Grafana Loki** — the JSON is line-addressable; use `| json` in
  LogQL to query fields like `event.source` or `service.environment`.
- **AWS CloudWatch / Datadog / Splunk / New Relic** — all ingest JSON
  lines natively and extract ECS fields without custom mapping.

!!! note
    The Mongo-backed log view inside the admin UI is unchanged — it
    still holds the structured application log for humans. JSON
    output is an *additional* stream for machines.

## What a log line looks like

```json
{
  "@timestamp": "2026-04-23T09:05:12.487Z",
  "log": {"level": "info", "logger": "debug"},
  "message": "Checkmk Host Export",
  "ecs": {"version": "8.11.0"},
  "service": {
    "name": "cmdbsyncer",
    "environment": "prod",
    "version": "3.12.14"
  },
  "host": {"name": "syncer-7f4b"},
  "process": {"pid": 17},
  "url": {"path": "/api/v1/syncer/cron/trigger/prod-cmk"},
  "http": {"request": {"method": "POST"}},
  "trace": {"id": "4bf92f3577b34da6a3ce929d0e0e4736"},
  "client": {"ip": "10.0.12.44"},
  "event": {
    "source": "Checkmk Host Export",
    "category": "app",
    "outcome": "success",
    "details": {"created": "3", "updated": "17", "deleted": "0"}
  },
  "affected_hosts": ["web-01", "web-02"]
}
```

Fields you can rely on:

| Field                  | Meaning                                                      |
| ---------------------- | ------------------------------------------------------------ |
| `@timestamp`           | ISO-8601 UTC, millisecond precision, trailing `Z`            |
| `log.level`            | `debug` / `info` / `warning` / `error` / `critical`          |
| `log.logger`           | Python logger name (usually `debug`)                         |
| `message`              | Human-readable summary                                       |
| `ecs.version`          | Always `"8.11.0"`                                            |
| `service.*`            | From `OTEL_SERVICE_NAME`, `DEPLOYMENT_ENVIRONMENT`, …        |
| `host.name`            | `socket.gethostname()` of the syncer process                 |
| `process.pid`          | OS PID                                                       |
| `url.path`             | Flask request path (only inside a request)                   |
| `http.request.method`  | HTTP verb (only inside a request)                            |
| `client.ip`            | Remote address (only inside a request)                       |
| `trace.id`             | First-match of `X-Request-ID`, `X-Cloud-Trace-Context`, `X-Amzn-Trace-Id`, `traceparent` |
| `event.source`         | Source string passed to `log.log(..., source=…)`             |
| `event.outcome`        | `success` / `failure`                                        |
| `event.details.*`      | Structured key/value details (preserved from `log.log`)      |
| `affected_hosts`       | List of hostnames when the event references hosts            |

For exceptions you additionally get `error.type`, `error.message`, and
`error.stack_trace`.

## Enabling it

Install the Enterprise package, ship a license that carries the
`json_logging` claim (see the [Enterprise Edition](index.md) page),
then restart the application.

A single marker line appears on startup, confirming the pipeline is
live:

```json
{"@timestamp":"2026-04-23T09:05:11.000Z","log":{"level":"info","logger":"debug"},"message":"ECS JSON logging active","service":{"name":"cmdbsyncer"}}
```

No extra config is required — defaults (stdout, `INFO`) match what
every cloud collector expects.

## Configuration knobs

All optional. Set in `local_config.py`:

| Key                    | Default   | Purpose                                       |
| ---------------------- | --------- | --------------------------------------------- |
| `JSON_LOGGING_ENABLED` | `True`    | Override to `False` to keep text output even when the license has `json_logging` (useful for local terminal runs) |
| `JSON_LOGGING_STREAM`  | `'stdout'`| `'stdout'` or `'stderr'`                      |
| `JSON_LOGGING_LEVEL`   | `'INFO'`  | Any standard Python level name                |

## Service identity

These environment variables are automatically mapped into the JSON
record without any code change — pass them through your container /
systemd unit to identify the instance:

| Env var                                              | ECS field             |
| ---------------------------------------------------- | --------------------- |
| `OTEL_SERVICE_NAME` (preferred), `SERVICE_NAME`      | `service.name`        |
| `DEPLOYMENT_ENVIRONMENT` (preferred), `ENV`          | `service.environment` |
| `CMDBSYNCER_VERSION` (preferred), `SERVICE_VERSION`  | `service.version`     |
| `AWS_REGION`, `CLOUD_REGION`                         | `cloud.region`        |

If `OTEL_SERVICE_NAME` is unset, `service.name` defaults to
`"cmdbsyncer"`.

## Cookbook

### Kubernetes

```yaml
env:
  - name: OTEL_SERVICE_NAME
    value: cmdbsyncer
  - name: DEPLOYMENT_ENVIRONMENT
    value: prod
  - name: CMDBSYNCER_VERSION
    valueFrom:
      fieldRef:
        fieldPath: metadata.labels['app.kubernetes.io/version']
```

Combine with a Fluent Bit / Vector DaemonSet — no parser needed; the
stream is already JSON.

### Docker Compose

```yaml
services:
  cmdbsyncer:
    environment:
      OTEL_SERVICE_NAME: cmdbsyncer
      DEPLOYMENT_ENVIRONMENT: prod
    logging:
      driver: json-file
      options:
        max-size: "50m"
        max-file: "5"
```

### Grafana Loki (LogQL)

```logql
{app="cmdbsyncer"} | json | event_outcome="failure" | line_format "{{.message}} ({{.event_source}})"
```

### Elastic / OpenSearch

No index template work needed for the fields above — they already
match the ECS datastream. Ingest with the default Filebeat
`container` / `docker` input.

## Troubleshooting

**I see both JSON and plain-text lines**  
A legacy handler is still installed. The configurator removes
handlers from the `debug` and root loggers at startup; if custom
code adds its own handler afterwards, that line keeps escaping. Grep
for `logging.StreamHandler()` in `local_config.py` or custom
plugins.

**`trace.id` is always missing**  
No upstream component is setting a trace header. Configure your
ingress / service mesh to forward one of the recognised headers, or
set `X-Request-ID` at the reverse proxy.

**Werkzeug request logs are gone**  
Expected. In production the reverse proxy access log is the right
place for that. Set `JSON_LOGGING_LEVEL = 'DEBUG'` if you want them
back.
