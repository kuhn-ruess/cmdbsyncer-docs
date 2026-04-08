# REST API

The CMDBSyncer provides REST API endpoints for various functions.
When `SWAGGER_ENABLED = True` is set in `local_config.py`, you can explore all endpoints interactively at `/api/v1`.

---

## Authentication

API authentication uses the user accounts configured in the GUI (**Profile → Users**).
The user needs appropriate API roles assigned to access specific endpoints.

### Basic Auth (recommended)

Send credentials using standard HTTP Basic Auth over HTTPS:

```bash
curl -u "username:password" https://cmdbsyncer.example.com/api/v1/syncer/logs
```

!!! warning
    Basic Auth requires HTTPS. On plain HTTP the request will be rejected with 401.
    When running behind Apache mod_wsgi, `WSGIPassAuthorization On` must be set in the Apache config,
    otherwise the `Authorization` header never reaches the application.
    See [Apache Setup](../installation/install_wsgi.md#key-directives-explained).

### `x-login-user` Header (fallback)

As a fallback — for example when Basic Auth is not available in a client — you can pass credentials via a custom header:

```bash
curl -H "x-login-user: username:password" https://cmdbsyncer.example.com/api/v1/syncer/logs
```

!!! note
    The `x-login-user` header is a legacy fallback. Basic Auth is the preferred method.
    The old `x-login-token` header has been removed.

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
