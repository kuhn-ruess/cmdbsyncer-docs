# MCP Server

CMDBsyncer ships an [MCP](https://modelcontextprotocol.io) server that lets
LLM-based clients (Claude Desktop, Cursor, Cline, …) read and write syncer
state. The server runs as a stdio subprocess started by the MCP client; it
boots in CLI mode (no Flask web stack) so cold start stays under ~250 ms.

## Installation

The MCP SDK is an optional dependency:

```bash
pip install -r requirements-extras.txt
```

After install, the entry point `cmdbsyncer-mcp` is on your `PATH`.

## Authentication

Same model as the REST API: a syncer **User** with the `mcp` (or `all`)
`api_role` authenticates via HTTP Basic. The role is a single umbrella
grant — having it opts a user into MCP entirely; granular per-tool
restrictions are not layered on top, so only grant `mcp` to users you
trust to operate the syncer.

Grant the role from **Profile → Users** in the admin UI by adding `mcp`
to the user's API roles list.

### stdio transport

The parent process owns the pipe — there is nobody else to authenticate
— so credentials are bound **once at startup**:

| Source | Variable / Flag |
|---|---|
| Environment | `CMDBSYNCER_API_USER` / `CMDBSYNCER_API_PASSWORD` |
| CLI flag    | `--user <name>` / `--password <pw>` |

CLI flags override env vars. The resolved User is verified to hold the
`mcp` (or `all`) role before the server starts; missing role aborts.

### sse / HTTP transport

Credentials are checked **per request** by a Starlette middleware:

* every connection (`GET /sse`, `POST /messages/...`) must carry
  `Authorization: Basic <base64>`;
* the resolved User is checked for `mcp` / `all` and bound to a
  per-request contextvar — no global state, no "leftover login";
* HTTPS is **required** (mirrors `application.api.require_token`).
  Plain HTTP is rejected with 401 unless the client is on
  `127.0.0.1`/`::1` or `ALLOW_INSECURE_API_AUTH = True` is set in
  `local_config.py`. Behind a trusted reverse-proxy, set
  `TRUSTED_PROXIES > 0` so the `X-Forwarded-Proto` header is honored.

A misconfigured deployment fails closed: invalid credentials, missing
`mcp` role, or plain HTTP all return 401 with a `WWW-Authenticate:
Basic realm="cmdbsyncer"` challenge.

## Transports

The same server speaks two transports — pick whichever your client supports:

### stdio (default)

The MCP client launches `cmdbsyncer-mcp` as a local subprocess and exchanges
JSON-RPC over stdin/stdout. Best for desktop clients (Claude Desktop, Cursor,
Cline). No port exposed.

### sse — HTTP / Server-Sent Events

For remote clients or shared deployments, run the server as an HTTP service.
**Do not pass `--user`/`--password`** in this mode — the server authenticates
each request individually:

```bash
cmdbsyncer-mcp --transport sse --host 0.0.0.0 --port 8765
```

The SSE endpoint lives at `http://<host>:<port>/sse`. Each connecting client
sends Basic credentials and is gated by the `mcp` (or `all`) role. Put the
service behind nginx/Apache for HTTPS termination — direct plain HTTP from
non-localhost is refused with 401.

| Flag | Env var | Default |
|---|---|---|
| `--transport` | `CMDBSYNCER_MCP_TRANSPORT` | `stdio` |
| `--host` | `CMDBSYNCER_MCP_HOST` | `127.0.0.1` |
| `--port` | `CMDBSYNCER_MCP_PORT` | `8765` |

The MCP server shares its tool implementations with the REST API (`/api/v1/*`):
both call the same `iter_rules_of_type`, `import_one_rule`, `import_json_bundle`,
etc., so a fix in one path applies to all three (CLI, REST, MCP).

## Running inside Docker

The shipped Docker image already bundles the MCP server (it lives in
`requirements-extras.txt` which is installed at build time). To start
it automatically alongside gunicorn, set two environment variables in
your `docker-compose.yml`:

```yaml
services:
  api:
    environment:
      MCPSERVER_ENABLED: "1"
      MCPSERVER_PORT: "8765"   # optional, default 8765
    ports:
      - "8765:8765"            # expose the MCP port to the host
```

The container's `entrypoint.sh` reads `MCPSERVER_ENABLED` after
self-configure and starts `cmdbsyncer-mcp --transport sse` in the
background as the unprivileged `app` user. There is no separate `--user`
/ `--password` — the server still authenticates **per request**, so each
connecting MCP client must present its own Basic credentials.

If you reverse-proxy through nginx/Apache for TLS:

```yaml
services:
  api:
    environment:
      MCPSERVER_ENABLED: "1"
      # Tell the app it sits behind a trusted proxy so X-Forwarded-Proto
      # = "https" is honored by the HTTPS gate. Same flag the REST API
      # already uses.
      # Set this in local_config.py: TRUSTED_PROXIES = 1
```

For development / internal networks where you really do not want HTTPS,
set `ALLOW_INSECURE_API_AUTH = True` in `local_config.py`. The MCP
server uses the same gate as the REST API.

## Client configuration

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cmdbsyncer": {
      "command": "cmdbsyncer-mcp",
      "env": {
        "CMDBSYNCER_API_USER": "admin@your-domain.com",
        "CMDBSYNCER_API_PASSWORD": "****"
      }
    }
  }
}
```

### Cursor / Cline / generic stdio clients

Most clients accept the same shape — a command + env. Point them at the
`cmdbsyncer-mcp` binary in your venv (`/path/to/venv/bin/cmdbsyncer-mcp`)
or a globally installed copy.

## Tools

### Hosts and accounts

| Tool | Description |
|---|---|
| `list_hosts(start, limit)` | Paginated listing of host objects. |
| `get_host(hostname)` | Resolved labels + inventory + last-seen timestamps. |
| `upsert_host(hostname, account, labels)` | Create or update a host, bind it to an account. Returns `account_conflict` if the host already belongs to a different account. |
| `delete_host(hostname)` | Delete a host; frees a Checkmk folder pool seat if held. |
| `update_host_inventory(hostname, key, inventory)` | Replace one inventory section. Never auto-creates a host. |
| `list_accounts()` | All accounts with name, type, enabled flag. |
| `get_account(name)` | Full resolved account record (cleartext password — handle with care). |

### Rules

| Tool | Description |
|---|---|
| `list_rule_types()` | Catalog of supported `rule_type` idents. |
| `export_rules(rule_type)` | Every rule of one type. |
| `export_all_rules(include_hosts, include_accounts, include_users)` | Bulk export grouped by type. |
| `create_rule(rule_type, rule)` | Persist one rule (same shape as the export). |
| `import_rules_bulk(payload)` | Replay an export back into the DB. |
| `run_autorules(debug)` | Trigger the autorules pass that builds rules from current host data. |

### Syncer / cron / logs

| Tool | Description |
|---|---|
| `get_recent_logs(limit)` | Last N log entries, newest first. |
| `get_cron_status()` | Status of every CronGroup. |
| `trigger_cron_group(group_name)` | Schedule a one-off run on the next cron pass. |
| `host_stats()` | Aggregate counters: total hosts, objects, stale-24h. |

## Resources

The server also exposes data as MCP resources, so the client's "attach
file" workflow can pull live syncer state without a tool call:

| URI template | Description |
|---|---|
| `cmdbsyncer://hosts/{hostname}` | Single host record as JSON. |
| `cmdbsyncer://rules/{rule_type}` | Every rule of one type as JSON. |
| `cmdbsyncer://cron/status` | Cron-group status snapshot. |

## Troubleshooting

**`MCP SDK not installed`** — run `pip install -r requirements-extras.txt`
or `pip install 'mcp>=1.10'`.

**`Authentication failed`** — verify the credentials work against the REST
API first: `curl -u user:pw https://your-syncer/api/v1/syncer/logs`. If
that returns 200, the same credentials work for MCP.

**`User has no api_role granting '<path>'`** — assign the right role from
**Profile → Users** in the GUI, or grant `all` for full access.

**No tools show up in the client** — most MCP clients log to a file you
can tail. Check that `cmdbsyncer-mcp` runs cleanly outside the client
first (`echo '{}' | cmdbsyncer-mcp --user … --password …` should print a
JSON-RPC error, not a Python traceback).
