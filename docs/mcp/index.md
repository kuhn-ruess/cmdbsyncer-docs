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

Same model as the REST API: a syncer **User** with the right `api_roles`
authenticates with HTTP Basic credentials. Pass credentials via either:

| Source | Variable / Flag |
|---|---|
| Environment | `CMDBSYNCER_API_USER` / `CMDBSYNCER_API_PASSWORD` |
| CLI flag    | `--user <name>` / `--password <pw>` |

CLI flags override env vars. Auth is checked once at startup; tool calls
then re-check the user's `api_roles` against a synthetic path, mirroring
the REST `/api/v1/<role>/...` gate.

| Tool group | Required role |
|---|---|
| `list_hosts`, `get_host`, `upsert_host`, `delete_host`, `update_host_inventory`, `list_accounts`, `get_account` | `objects` |
| `list_rule_types`, `export_rules`, `export_all_rules`, `create_rule`, `import_rules_bulk`, `run_autorules` | `rules` |
| `get_recent_logs`, `get_cron_status`, `trigger_cron_group`, `host_stats` | `syncer` |

A user with `api_roles = ['all']` can call every tool.

## Transports

The same server speaks two transports — pick whichever your client supports:

### stdio (default)

The MCP client launches `cmdbsyncer-mcp` as a local subprocess and exchanges
JSON-RPC over stdin/stdout. Best for desktop clients (Claude Desktop, Cursor,
Cline). No port exposed.

### sse — HTTP / Server-Sent Events

For remote clients or shared deployments, run the server as an HTTP service:

```bash
cmdbsyncer-mcp --transport sse --host 0.0.0.0 --port 8765
```

The SSE endpoint lives at `http://<host>:<port>/sse`. Auth is still bound at
startup from the same credentials; every session that connects inherits the
bound user. Reverse-proxy this through nginx/Apache for HTTPS.

| Flag | Env var | Default |
|---|---|---|
| `--transport` | `CMDBSYNCER_MCP_TRANSPORT` | `stdio` |
| `--host` | `CMDBSYNCER_MCP_HOST` | `127.0.0.1` |
| `--port` | `CMDBSYNCER_MCP_PORT` | `8765` |

The MCP server shares its tool implementations with the REST API (`/api/v1/*`):
both call the same `iter_rules_of_type`, `import_one_rule`, `import_json_bundle`,
etc., so a fix in one path applies to all three (CLI, REST, MCP).

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
