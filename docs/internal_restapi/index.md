# REST API

The CMDBsyncer provides REST API endpoints for various functions.
When `SWAGGER_ENABLED = True` is set in `local_config.py`, you can explore all endpoints interactively at `/api/v1`.

All endpoints live below `/api/v1` and always speak JSON. There is no session
or cookie login on the API — every single request carries its own credentials.

| Namespace | Base path | What it does |
|---|---|---|
| [Objects](objects.md) | `/api/v1/objects` | Read, create, update and delete hosts, their labels, inventory and relations |
| [Syncer](syncer.md) | `/api/v1/syncer` | Logs, cron status, host counters and the cron webhook trigger |
| [Rules](rules.md) | `/api/v1/rules` | Export and import the rule configuration, run autorules |
| [Ansible](ansible.md) | `/api/v1/ansible` | Dynamic inventory in Ansible JSON format |

---

## Authentication

API authentication uses the user accounts configured in the GUI (**Profile → Users**).
The user needs appropriate API roles assigned to access specific endpoints.

### Basic Auth

Send credentials using standard HTTP Basic Auth over HTTPS:

```bash
curl -u "username:password" https://cmdbsyncer.example.com/api/v1/syncer/logs
```

!!! warning
    All API authentication requires HTTPS (or a loopback connection). On plain HTTP the
    request is rejected with 401. When running behind Apache mod_wsgi, `WSGIPassAuthorization On`
    must be set in the Apache config, otherwise the `Authorization` header never reaches the
    application. See [Apache Setup](../installation/install_wsgi.md#key-directives-explained).

### Personal API tokens
<span class="since">Since 4.3</span>

Instead of sending a password on every call, a user can generate personal API tokens under
**Profile → API Tokens**. Each token:

* authenticates **as its owner**, so it carries exactly that user's API roles and
  [account scope](#restricting-a-user-to-accounts);
* is shown in plaintext **once** on creation (store it safely);
* can have a label and an optional expiry date, and can be revoked at any time.

Send it as a Bearer token in the `Authorization` header:

```bash
curl -H "Authorization: Bearer cmdb_pat_xxxxxxxx" \
     https://cmdbsyncer.example.com/api/v1/syncer/logs
```

The token is also accepted via the `x-login-token` header, and — for convenience with the
Swagger UI — the leading `Bearer ` is optional:

```bash
curl -H "x-login-token: cmdb_pat_xxxxxxxx" https://cmdbsyncer.example.com/api/v1/syncer/logs
curl -H "Authorization: cmdb_pat_xxxxxxxx"  https://cmdbsyncer.example.com/api/v1/syncer/logs
```

!!! note
    Admins can list and revoke a user's tokens from **Profile → Users**, but never see or
    generate a token's plaintext on the user's behalf.

### `x-login-user` Header (fallback)

As a fallback — for example when Basic Auth is not available in a client — you can pass
username/password via a custom header:

```bash
curl -H "x-login-user: username:password" https://cmdbsyncer.example.com/api/v1/syncer/logs
```

### Authenticating in the Swagger UI
<span class="since">Since 4.3</span>

On the `/api/v1` Swagger page, click **Authorize** and either fill in your username and
password (basic auth) **or** paste a personal API token into the *apiToken* field (with or
without a leading `Bearer `). Then use *Try it out* on any endpoint.

---

## API roles

Access is granted per namespace through the user's **API roles**
(**Profile → Users → API Roles**). A role matches when it is `all` or when it is
the beginning of the requested path — so the role `objects` opens every
`/api/v1/objects/*` endpoint:

| Role | Grants |
|---|---|
| `all` | Every endpoint |
| `objects` | `/api/v1/objects/*` |
| `syncer` | `/api/v1/syncer/*` |
| `rules` | `/api/v1/rules/*` |
| `ansible` | `/api/v1/ansible/*` |
| `metrics` | The Prometheus `/metrics` scrape URL (Enterprise) |
| `mcp` | The [MCP server](../mcp/index.md) |

A user without a matching role gets `401` — the same answer as a wrong password,
so a probing client cannot tell the two apart.

### Read-only users
<span class="since">Since 4.3</span>

A user marked **read only** keeps every `GET` their roles allow and is refused on
every writing call (`POST`, `DELETE`) with `403 read only account`. A personal API
token inherits the flag from its owner, so it is no way around the restriction.

### Restricting a user to accounts
<span class="since">Since 4.3</span>

A user can be limited to one or more accounts under **Profile → Users → Restrict to accounts**.
When set, every host-facing API call (read, create, bulk, delete, inventory, relations) only
sees and touches hosts bound to those accounts — and creates may only name an allowed account.
Leaving the field empty keeps full access. The same restriction also applies to the Host and
Objects lists in the web UI.

A user can additionally be restricted to CMDB templates; both restrictions apply
on top of each other. Hosts outside the scope are answered with `404` rather than
`403`, so a restricted user never learns that a host exists at all.

---

## Errors and rate limiting

Errors come back as JSON with the field `message` (Flask-RESTX default) or
`error`, depending on the endpoint:

| Code | Meaning |
|---|---|
| `400` | Payload invalid — unknown account, bad label/inventory key, non-numeric pagination |
| `401` | No, wrong or expired credentials; plain HTTP; missing API role |
| `403` | Credentials fine, operation not allowed — read-only user, account conflict, disabled webhook |
| `404` | Object does not exist, or is outside the caller's scope |
| `409` | Cron group is disabled and cannot be triggered |

Failed logins are rate limited per client IP (`API_RATE_LIMIT` in
`local_config.py`, default `30 per minute; 300 per hour`). **Only `401`
responses deduct from the budget**, so a monitoring client polling every few
seconds is never throttled — only credential guessing is.

Every failed authentication is written to the syncer log (**Log** in the web
interface) with source `API`, so brute-force attempts are visible.
