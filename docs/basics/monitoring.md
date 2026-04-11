# Monitor the Syncer with Checkmk

The Syncer exposes a small REST API which reports the state of every cron
group and of every configured source. With the **CMDB Syncer Monitoring**
special agent from the Checkmk Exchange you can turn these endpoints into real
Checkmk services and get paged as soon as an import fails or a cronjob does
not run anymore.

The plugin is maintained by us and lives in the
[Checkmk-Checks](https://github.com/kuhn-ruess/Checkmk-Checks) repository
under `cmdb_syncer/`. Packaged `.mkp` files are published with every release.

## What is Monitored

The special agent queries two API endpoints on the Syncer:

- `/api/v1/syncer/services/<service_name>` — the latest log entry for a given
  source/service. A Checkmk service is created for every source name you list
  and turns CRIT as soon as the log entry has `has_error=true`.
- `/api/v1/syncer/cron/` — one service per configured cron group with
  `last_start`, `next_run`, `is_running` and the last error message. Useful to
  detect stalled or skipped cron runs.

The source names are the same ones you see in the log viewer of the Syncer
(_Modules → Log_). Pick the name of each import/export you want to watch.

## Install the MKP

1. Download the latest `cmdb_syncer-*.mkp` from the
   [Checkmk-Checks repository](https://github.com/kuhn-ruess/Checkmk-Checks/tree/main/cmdb_syncer).
2. Upload it in Checkmk via _Setup → Extension packages → Upload package_ and
   activate it.
3. The new rule **CMDB Syncer Monitoring** appears under
   _Setup → Agents → Other integrations → Special agents_.

The plugin ships with rulesets for Checkmk 2.3 and newer.

## Prepare the Syncer

The special agent authenticates against the Syncer's REST API with a regular
user account. Create (or reuse) a user that has permission to read the log and
cron data, and remember the password. 

Make sure the Syncer is reachable from the Checkmk site over HTTPS. For
production setups it is strongly recommended to terminate TLS in front of the
Syncer — the API enforces HTTPS for password-based authentication since
3.12.4.

## Create the Special Agent Rule

Go to _Setup → Agents → Other integrations → Special agents →
CMDB Syncer Monitoring_ and create a new rule with the following parameters:

| Field            | Description                                                                                  |
|------------------|----------------------------------------------------------------------------------------------|
| `API URL`        | Base URL of the Syncer, e.g. `https://syncer.example.com` (no trailing slash, no `/api/v1`). |
| `Username`       | Syncer user used for API access.                                                             |
| `Password`       | Password of that user (stored in the Checkmk password store).                                |
| `Timeout`        | Request timeout in seconds, default `2.5`.                                                   |
| `Services`       | List of source names that should be monitored as individual services.                        |
| `Fetch Cronjobs` | Enable to also create services for every cron group.                                         |

Assign the rule to the host that represents your Syncer instance. Typically
this is the Checkmk host of the Syncer VM itself; any host will work as long
as the special agent can reach the Syncer URL from the Checkmk site.

## Discover the Services

After saving the rule, run a service discovery on the host. You should see one
service per entry in `Services` (named after the source) and, if enabled, one
service per cron group. Accept the new services and activate the changes.

From now on Checkmk polls the Syncer on every check cycle. A source turns
CRIT when its last log entry has `has_error=true` — the message that is shown
in the service output is exactly the message Checkmk received from the API,
so you can triage the problem without opening the Syncer UI.

## Troubleshooting

- **`invalid_login` in the service output** — the user/password combination
  is wrong, or the user does not have the required permissions. Verify by
  calling `curl -H 'x-login-user: USER:PASS' https://syncer.example.com/api/v1/syncer/cron/`.
- **`Object not Found` / 404** — the source name in the rule does not match
  any log entry. Source names are case sensitive and must match what the
  Syncer writes to the log.
- **Timeouts** — increase the `Timeout` field. A busy Syncer that is doing a
  large import can take a few seconds to answer.
- **HTTP 400 / redirect loops** — the API rejects password authentication
  over plain HTTP. Use an `https://` URL for `API URL`.

## See also

- [Logging](logging.md) — where the monitored log entries come from.
- [Cronjobs](cron.md) — how cron groups are defined in the Syncer.
- [Rest API](../internal_restapi/index.md) — full reference of the REST API.
