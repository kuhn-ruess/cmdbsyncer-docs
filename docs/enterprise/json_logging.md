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
| `event.details.*`      | Structured key/value details (preserved from `log.log`). A key that occurs more than once — one `error` per failed host, for example — becomes an array |
| `affected_hosts`       | List of hostnames when the event references hosts            |

For exceptions you additionally get `error.type`, `error.message`, and
`error.stack_trace`. An entry the Syncer logged from inside an exception
handler carries its traceback in `error.stack_trace` as well.

Everything the **Log** view in the admin panel shows for a run is in the
JSON record too: the same message, source, affected hosts, every detail
row, and the traceback.

## Enabling it

Two steps, in this order.

### 1. Install the package and the license

Install the Enterprise package and ship a license that carries the
`json_logging` claim — see the [Enterprise Edition](index.md) page.

### 2. Switch the stream on

The stream is **off until you ask for it**, licence or not: an upgrade
must never change the log format of a running installation under its
operator.

There is one switch per thing that logs, and they are independent —
set the one whose output you want in the collector:

| Switch                 | What it puts on the stream                |
| ---------------------- | ----------------------------------------- |
| `JSON_LOGGING_ENABLED` | The web application and its workers       |
| `JSON_LOGGING_CLI`     | Command runs — imports, exports, cron     |

Easiest through the web interface: **Config → Local Config** carries a
**JSON log stream** preset with all five keys, their defaults and a
line each on what they do. Saving there writes `local_config.py` for
you.

By hand, for the web application:

```python
config = {
    'JSON_LOGGING_ENABLED': True,
}
```

Restart the application. A single marker line appears on startup,
confirming the pipeline is live:

```json
{"@timestamp":"2026-04-23T09:05:11.000Z","log":{"level":"info","logger":"debug"},"message":"ECS JSON logging active","service":{"name":"cmdbsyncer"}}
```

That covers the web application and its workers. The remaining
defaults — stdout, `INFO` — match what every cloud collector expects.

### Command runs (imports, exports, cron)

Imports, exports and cron runs are usually the events the pipeline is
actually after, and they have a switch of their own:

```python
config = {
    'JSON_LOGGING_CLI': True,        # imports, exports, cron
}
```

It does not need `JSON_LOGGING_ENABLED` beside it — wanting the
imports in your collector says nothing about wanting the web log there
too. Set both where you want both.

!!! note
    Command runs reach the stream from version 4.3 on. Earlier
    versions built the pipeline only for the web application and its
    workers and skipped it for every `cmdbsyncer <command>` run, so
    `JSON_LOGGING_CLI` has no effect there — imports, exports and cron
    stay plain text whatever it is set to. In 4.3.0 and 4.3.1 it also
    still needed `JSON_LOGGING_ENABLED` next to it.

**Not when you are watching.** A command whose output goes straight to
a terminal keeps its plain text, even with the setting on: one JSON
record can carry an entire stack trace on a single line, and no
collector is reading your terminal anyway. A cron run, a pipe or a
redirect is not a terminal, and that is where the stream is produced —
so the one setting serves both without a second switch.

```sh
cmdbsyncer csv import_hosts prod          # terminal → plain text
cmdbsyncer csv import_hosts prod | tee /dev/null   # pipe → JSON
```

**Everything the run reports becomes a record.** The progress of a run
— the retries, the timeouts, the result per host — is printed straight
to the console by the plugins. On such a run those lines go through the
pipeline as well, so each arrives as its own record with the colour
escapes stripped, under `event.source: command_output`:

```json
{"@timestamp":"…","log":{"level":"info"},"message":"Try 1 of 2 failed: HTTPConnectionPool(host='cmk.example.com', port=80): Max retries exceeded","event":{"source":"command_output","category":"app","outcome":"success"}}
```

Without it a collector would see that an export failed but not one of
the attempts leading there — only the closing summary record of the run
carries a source of its own.

Third-party chatter (mongoengine, urllib3, …) stays suppressed in
command runs either way — only the Syncer's own entries are emitted.

### Writing to a log file instead

Everything above puts the records on a stream, which is what a
container collector reads. A run started from *outside* the container
— `docker exec` out of a host cron, for instance — has no such reader:
its output goes to that exec session and never to the container log
(see [Troubleshooting](#troubleshooting)). `JSON_LOGGING_FILE` sends
the records to a file instead:

```python
config = {
    'JSON_LOGGING_ENABLED': True,
    'JSON_LOGGING_CLI': True,
    'JSON_LOGGING_FILE': '/var/log/syncer/cmdbsyncer.jsonl',
}
```

The directory has to exist and be writable for the user the Syncer runs
as — in a container that means mounting it in. If the path cannot be
opened the run says so on stderr and keeps writing to the stream, so a
typo never costs you an import.

A file is not a terminal, so this is the one target that also works
while you watch a run: the records go to the file, your terminal keeps
the readable output. Log rotation is supported — the file is reopened
when it is rotated away, no restart needed.

!!! note
    Available in the current 4.3 release line, with the matching
    Enterprise package. Before that the records only go to a stream —
    see the cookbook entry [Host cron calling `docker exec`](#host-cron-calling-docker-exec)
    for how to catch them in a file from the outside.

## The five keys

Set in `local_config.py`, or through the **JSON log stream** preset
under **Config → Local Config**. The defaults below apply when a key is
absent:

| Key                    | Default   | Purpose                                       |
| ---------------------- | --------- | --------------------------------------------- |
| `JSON_LOGGING_ENABLED` | `False`   | The web application and its workers write records. Independent of the key below |
| `JSON_LOGGING_CLI`     | `False`   | `cmdbsyncer <command>` runs — imports, exports, cron — write records. Stands on its own; the key above is not needed for it. Runs printing to a terminal keep their plain text, unless the records go to `JSON_LOGGING_FILE`. Needs version 4.3 or newer |
| `JSON_LOGGING_FILE`    | unset     | Write the records into this file instead of the stream — for runs nobody collects the output of, started from outside the container for example. Falls back to the stream when the path cannot be opened |
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

### Host cron calling `docker exec`

A cron job on the host that runs the Syncer inside the container needs
two things: no TTY, and somewhere for the records to go that outlives
the container.

```sh
docker compose exec -T cmdbsyncer \
    cmdbsyncer checkmk export_hosts prod
```

`docker compose exec` allocates a TTY by default and a run on a
terminal keeps its plain text, so `-T` is what turns the output into
records (plain `docker exec` allocates none). A pipe or a redirect on
the *host* side does not do it: it sits behind that TTY, and the
command inside the container still sees a terminal. With `-T` in place
it works as usual.

For the destination, redirect the run into a file on a mounted path:

```sh
docker compose exec -T cmdbsyncer \
    cmdbsyncer checkmk export_hosts prod \
    >> /var/log/syncer/cmdbsyncer.jsonl 2>> /var/log/syncer/cmdbsyncer.err
```

`JSON_LOGGING_FILE` does that for you from the current 4.3 release on.

Either way the records stay on the host, where they survive the
container and where Filebeat / Vector / the Elastic Agent already tail
files, and `mk-job` or whatever wraps the job keeps its own output.

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

**An import or export produces no JSON at all**  
Command runs need `JSON_LOGGING_CLI = True` (see above). Without it
only the web application and its workers write to the JSON stream. On
4.3.0 and 4.3.1 the key also needed `JSON_LOGGING_ENABLED` beside it.
Check as well that the Enterprise package is really installed in the
container you are running in — without it none of these keys do
anything.

**I set `JSON_LOGGING_CLI` and still see plain text**  
You are running the command on a terminal, where it stays readable on
purpose. Pipe or redirect it — `cmdbsyncer … | cat` — to see what the
collector will get.

**The JSON is in my terminal but not in `docker logs`**  
`docker logs` shows the stream of the container's main process only. A
run started with `docker exec` writes to that exec session, which is
your terminal — it never reaches the container log, and a collector
scraping the container never sees it. That is Docker behaviour, not a
setting. Cron runs inside the container do reach the container log:
`run_cron.sh` writes to the main process's streams, because the cron
daemon itself would hand job output to sendmail instead. Everything the
run reports arrives on stdout as records; stderr keeps whatever escapes
the pipeline, an interpreter-level traceback for instance.

For runs that come in from the host — a cron job calling `docker exec`
— point `JSON_LOGGING_FILE` at a mounted path instead of chasing the
container log; see [Host cron calling `docker exec`](#host-cron-calling-docker-exec).

**Werkzeug request logs are gone**  
Expected. In production the reverse proxy access log is the right
place for that. Set `JSON_LOGGING_LEVEL = 'DEBUG'` if you want them
back.
