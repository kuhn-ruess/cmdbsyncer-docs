# REST API

The CMDBSyncer provides REST API endpoints for various functions.
When `SWAGGER_ENABLED = True` is set in `local_config.py`, you can explore all endpoints interactively at `/api/v1`.

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

### Restricting a user to accounts
<span class="since">Since 4.3</span>

A user can be limited to one or more accounts under **Profile → Users → Restrict to accounts**.
When set, every host-facing API call (read, create, bulk, delete, inventory, relations) only
sees and touches hosts bound to those accounts — and creates may only name an allowed account.
Leaving the field empty keeps full access. The same restriction also applies to the Host and
Objects lists in the web UI.

---

## Ansible Endpoints

These endpoints expose the Ansible inventory of the CMDBSyncer so it can be used directly as a dynamic inventory source from other servers.
See the Ansible subfolder for an example of how to use it with `ansible-playbook`.

---

## Syncer Endpoints

These endpoints are used to monitor Syncer operations.
The official Checkmk Syncer monitoring plugins use them to check job status and last run times.

---

## Objects Endpoints

The `GET` / `POST` / `DELETE` endpoints allow you to read, create, update, and delete hosts or objects inside the Syncer from external systems.

There is no `PUT` method — the Syncer automatically gets or creates the host object from its database, so you do not need to check for existence before updating.
