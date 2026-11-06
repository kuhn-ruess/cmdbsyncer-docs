# Update Notes

<!-- NOTICES -->

Before every update, check this page for breaking changes that require manual action.

After every update, always run:

    ./cmdbsyncer sys self_configure

This automatically adapts configuration changes and adds missing default values to `local_config.py` — for example, the `CRYPTOGRAPHY_KEY`.

---

## Upgrading to 4.5

These changes can affect a running installation. Check them before you update.

**Rules and exports**

- Tag Match `equal` ignores upper and lower case again. Rules whose attribute name differs only in case did not match since 3.12.12 and match after the update, so exports can change.
- A Hostname Match regex with `\D`, `\S` or `\W` now means what it says. It was turned into `\d`, `\s` or `\w` before, so such a rule now hits other hosts.
- `{{ FIRST_MATCHING_TAG }}` and `{{ FIRST_MATCHING_VALUE }}` now hold real values, which can change attributes and exports.
- A host set to Ignore is now also left out when a rule works with a timestamp. It drops out of the export and can be deleted from Checkmk.
- i-doit: an object with the same title and another type counts as existing and is no longer created.

**Imports**

- CSV and NetBox imports with `delete_host_if_not_found_on_import` no longer archive anything after errors or an empty result.

**Cron**

- Cron groups can turn red and send notifications. A failed task stops the group unless Continue on error is set.
- Container image: cron runs again, as user `app` instead of root. Own jobs with root paths can fail.

**Logins and permissions**

- Everyone with a local password has to log in once after the update.
- A password reset no longer logs in. Set `PUBLIC_URL`, otherwise the link in the mail depends on the Host header of the request.
- The Archive needs the Hosts, Objects or hard delete permission, and restoring a host needs a POST request.

**REST API and MCP**

- Accounts and users can only be exported and imported on the command line. `include_users` and `include_accounts` answer 403, so adapt backup scripts to `rules export_all_rules` and `rules import_rules`.
- MCP: read-only and scope limits now apply, and only a global admin without a limit can read an account with its password.
- MCP over SSE only answers to localhost by default. A remote client or a reverse proxy that passes on its own host name needs that name in `MCP_ALLOWED_HOSTS`.

**Ansible and Jinja**

- Ansible goes from 10.5 to 14.6. The server needs Python 3.12 or newer, the target hosts Python 3.9 or newer. In own playbooks a `when` must give a real true or false, a plain string or number stops the task.
- Jinja: `datetime` only offers the classes of the module. `datetime.datetime.now()` keeps working.

---

## Upgrading from 3.x to 4.x: `CRYPTOGRAPHY_KEY` recovery

In versions before 3.12.4, `application/config.py` shipped with a hardcoded
default `CRYPTOGRAPHY_KEY`. If your `local_config.py` did **not** define
`CRYPTOGRAPHY_KEY` (or defined it under a typo'd name, e.g.
`CRYPTO__GRAPHY_KEY`), your account passwords were silently encrypted
using that built-in default.

Starting with 3.12.4 the default is `None`. After the upgrade, decrypting
existing account passwords fails with:

    cryptography.fernet.InvalidToken

To recover your existing passwords, add the **old default key** to your
`local_config.py` (note the `b''` prefix — it must be `bytes`, not `str`):

```python
config = {
    ...
    'CRYPTOGRAPHY_KEY': b'nto4ioGgQDlJ-r5jqvyEtTpUQC2fkOAG4Df-E8OlVm8=',
    ...
}
```

After that, the syncer can decrypt all stored passwords again.

### Rotating to your own key afterwards

If you want to replace the well-known default with your own fresh key,
write the **current** key as a plain string (no `b''` prefix) into
`local_config.py`:

```python
'CRYPTOGRAPHY_KEY': 'nto4ioGgQDlJ-r5jqvyEtTpUQC2fkOAG4Df-E8OlVm8=',
```

Back up MongoDB, then run:

    ./cmdbsyncer sys self_configure

`self_configure` detects the string form, generates a new key,
re-encrypts every account password with it, and writes the new key back
to `local_config.py` in the proper `bytes` form.

---

## MongoDB

The MongoDB used by CMDBsyncer also needs updates from time to time.

If you are using the Docker Compose files provided by us and do not skip Syncer versions, no action is required.

If you manage your own installation or your own Docker config, keeping MongoDB up to date is your responsibility. CMDBsyncer has no hard requirement for a specific MongoDB version, but updates fix bugs and improve performance.
