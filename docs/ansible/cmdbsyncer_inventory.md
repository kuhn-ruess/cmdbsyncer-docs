# cmdbsyncer-inventory Plugin

`cmdbsyncer-inventory` is a standalone Ansible dynamic inventory plugin that pulls hosts and host vars from the Syncer. As of **0.2.0** it speaks two transports:

| Mode | Backend | When to use |
| :--- | :------ | :---------- |
| `local` (default) | Shells out to the local `cmdbsyncer` CLI (`cmdbsyncer inventory ansible <provider> --list`) | Ansible runs on the **same host** as the Syncer (the bundled UI runner uses this). Fastest and credential-free. |
| `http` | GETs `/api/v1/inventory/ansible/<provider>` | Ansible control node is a **different host** than the Syncer. |

Both transports return identical data because they are backed by the same Syncer-side render function — see [Inventory Providers](inventory_providers.md) for the full picture.

Source: [kuhn-ruess/cmdbsyncer-inventory](https://github.com/kuhn-ruess/cmdbsyncer-inventory) · PyPI: [cmdbsyncer-inventory](https://pypi.org/project/cmdbsyncer-inventory/).

## Installation

```bash
pip install cmdbsyncer-inventory
python -m cmdbsyncer_inventory
```

The second command registers the plugin with your active Ansible installation so `ansible-inventory` and `ansible-playbook` can load it by name. Run it once per Python environment you use for Ansible.

## Local mode (default)

```yaml
# inventory.yml
plugin: cmdbsyncer_inventory
mode: local                      # default — can be omitted
provider: ansible                # default — names a registered provider
# cmdbsyncer_bin: /opt/cmdbsyncer/cmdbsyncer    # optional override
```

```bash
ansible-inventory -i inventory.yml --list
ansible-playbook  -i inventory.yml site.yml
```

The Syncer's [UI Runner](run_from_ui.md) sets `CMDBSYNCER_INVENTORY_PROVIDER` per-playbook based on the [manifest](playbook_manifest.md), so a single `inventory.yml` works for every dispatched playbook — no per-playbook YAML duplication.

## HTTP mode

Use this from a remote AWX, Semaphore, or any other Ansible control node that cannot run the Syncer CLI directly.

```yaml
# inventory.yml
plugin: cmdbsyncer_inventory
mode: http
provider: ansible
api_url: https://your-cmdbsyncer.example.com
verify_ssl: true        # set to false only for self-signed test instances
```

Credentials come from env vars (recommended, so they do not end up in git):

```bash
export CMDBSYNCER_APIUSER="apiuser"
export CMDBSYNCER_APIPASSWORD="apisecret"
```

…or from the YAML (`username:` / `password:`). Env vars take precedence.

The plugin must reach `https://<syncer>/api/v1/inventory/ansible/<provider>`. Before going live verify with:

```bash
curl -H "x-login-user: USER:SECRET" https://your-syncer/api/v1/inventory/ansible/ansible | head
```

## Selecting the provider

`provider` names a Syncer-side **inventory provider**. Bundled providers are `ansible` (host inventory) and `cmk_sites` (Checkmk site inventory used by `cmk_server_mngmt.yml`). Modules can register more — see [Inventory Providers](inventory_providers.md).

Two ways to set it:

- **YAML option `provider:`** — stable per-inventory selection.
- **Env var `CMDBSYNCER_INVENTORY_PROVIDER`** — wins over the YAML; how the Syncer's UI runner switches providers per playbook.

## Configuration reference

| Option | Mode | Default | Description |
| :----- | :--- | :------ | :---------- |
| `plugin` | both | — | Must be `cmdbsyncer_inventory`. |
| `mode` | both | `local` | `local` or `http`. Env var: `CMDBSYNCER_INVENTORY_MODE`. |
| `provider` | both | `ansible` | Registered provider name. Env var: `CMDBSYNCER_INVENTORY_PROVIDER`. |
| `cmdbsyncer_bin` | local | `cmdbsyncer` | Path / name of the cmdbsyncer CLI. |
| `api_url` | http | — | Syncer base URL. |
| `username` | http | — | API user. Env var: `CMDBSYNCER_APIUSER`. |
| `password` | http | — | API password. Env var: `CMDBSYNCER_APIPASSWORD`. |
| `verify_ssl` | http | `true` | TLS cert verification. |

## Troubleshooting

**`cmdbsyncer binary not found`** (local mode) — the `cmdbsyncer` CLI is not on PATH for the Ansible execution context. Either put it on PATH, set `cmdbsyncer_bin:` to the absolute path, or switch to `mode: http`.

**`cmdbsyncer CLI exited 1: Unknown provider: …`** — the provider is not registered in this Syncer build. List registered providers with `cmdbsyncer inventory list-providers`.

**`REST API returned 401`** (http mode) — Syncer rejected the credentials. Double-check `CMDBSYNCER_APIUSER` / `CMDBSYNCER_APIPASSWORD` and that the user has the **`ansible`** API role.

**Empty host list** — the provider returned no hosts. For the `ansible` provider this usually means no [filter rules](../basics/filter.md) match. Validate on the Syncer with `cmdbsyncer ansible debug_filter -l`.

**`plugin: cmdbsyncer_inventory` not recognised** — the plugin was not registered in the active Python environment. Re-run `python -m cmdbsyncer_inventory` inside the venv that Ansible uses.
