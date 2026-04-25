# Inventory Providers

Inventory in the Syncer is **module-pluggable**: each module that has a host (or site, or device, …) catalogue can register a *provider*. The same data is then reachable through one CLI command and one HTTP endpoint, in the format the consumer expects — currently the standard Ansible JSON shape, with room for additional formats next to it.

The architecture is what lets the bundled UI runner, the [`cmdbsyncer-inventory`](cmdbsyncer_inventory.md) plugin, and a remote AWX execution environment all see identical data without any of them caring which module produced it.

## Concepts

```
                         ┌─────────────────────────┐
                         │   Modules (plugins)     │
                         │                         │
                         │  Ansible host inventory │  ← provider 'ansible'
                         │  Checkmk Sites          │  ← provider 'cmk_sites'
                         │  …future modules        │  ← provider '…'
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │  Inventory Registry      │
                         │  application.modules.    │
                         │  inventory               │
                         └────────────┬────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
       ┌───────────┐           ┌───────────┐           ┌────────────┐
       │   CLI     │           │   HTTP    │           │  Future    │
       │  inventory│           │  /api/v1/ │           │  formats   │
       │  ansible  │           │  inventory│           │  (DCD,…)   │
       └─────┬─────┘           └─────┬─────┘           └────────────┘
             │                       │
             ▼                       ▼
   shared render function: render_ansible_inventory(provider, host=…)
```

A **provider** is any object with two methods:

```python
class MyProvider:
    def get_full_inventory(self) -> dict: ...
    def get_host_inventory(self, hostname: str) -> dict | False: ...
```

The shape returned matches the Ansible script contract:

```json
{
  "_meta": {"hostvars": {"<host>": {"ansible_host": "10.0.0.1", ...}}},
  "all":  {"hosts":   ["<host>", ...]}
}
```

A **format adapter** consumes the registry. Today the only adapter renders Ansible JSON — both for the CLI (`cmdbsyncer inventory ansible <provider>`) and for the HTTP endpoint (`/api/v1/inventory/ansible/<provider>`). Both call the same `render_ansible_inventory(provider, host=…)` function, so changing one cannot drift from the other.

## Bundled providers

| Name | Source | Used by |
| :--- | :----- | :------ |
| `ansible` | `application/plugins/ansible/inventory.py:AnsibleInventory` — the host catalogue rendered by the [Ansible filter / rewrite / custom-attribute rules](index.md) **without a project assignment**. | The default for every playbook in the [manifest](playbook_manifest.md) unless overridden. |
| `cmk_sites` | `application/plugins/ansible/site_syncer.py:SyncSites` — the Checkmk site catalogue. | `cmk_server_mngmt.yml` and `cmk_omd_cleanup.yml` (declared in the bundled manifest). |
| `<project-name>` | Each enabled [Ansible Project](projects.md) becomes its own provider, rendered through the rules assigned to that project (strict isolation). | Set the manifest's `inventory:` field to the project name. |

List what your installation has registered:

```bash
cmdbsyncer inventory list-providers
```

Or via HTTP:

```bash
curl -H "x-login-user: USER:SECRET" https://syncer/api/v1/inventory/ansible
```

## Reaching a provider

### CLI (local Syncer)

Honors the standard Ansible inventory-script contract:

```bash
cmdbsyncer inventory ansible <provider> --list
cmdbsyncer inventory ansible <provider> --host=<hostname>
```

This is what the [`cmdbsyncer-inventory`](cmdbsyncer_inventory.md) plugin runs in local mode.

### HTTP (remote Syncer)

```bash
GET /api/v1/inventory/ansible/<provider>
GET /api/v1/inventory/ansible/<provider>?host=<hostname>
GET /api/v1/inventory/ansible          # list registered providers
```

Auth: `x-login-user: USER:SECRET` header (or basic auth). The user needs the `ansible` API role.

### Per-playbook selection (UI runner)

The [`Run Playbook`](run_from_ui.md) runner picks the provider from the manifest entry's `inventory:` field and exports `CMDBSYNCER_INVENTORY_PROVIDER` into the spawned `ansible-playbook`. The `cmdbsyncer-inventory` plugin reads that env var and serves the matching provider — so the same `ansible/syncer.inventory.yml` works for every playbook.

```yaml
# ansible/playbooks.yml
playbooks:
  - file: cmk_server_mngmt.yml
    name: "Checkmk: Manage OMD Server"
    inventory: cmk_sites          # ← picks the cmk_sites provider for this run
```

## Registering a provider in your own module

```python
# application/plugins/yourmodule/__init__.py
from application.modules.inventory import register_inventory_provider


def _build_provider():
    return YourCatalogProvider()        # any object with the two methods


register_inventory_provider('yourmodule', _build_provider)
```

That's it — the new provider is now reachable via:

```bash
cmdbsyncer inventory ansible yourmodule --list
curl https://syncer/api/v1/inventory/ansible/yourmodule
```

…and selectable from the [playbook manifest](playbook_manifest.md) `inventory:` field, the [`cmdbsyncer-inventory`](cmdbsyncer_inventory.md) plugin's `provider:` option, or the `CMDBSYNCER_INVENTORY_PROVIDER` env var.

## Why a registry instead of one endpoint per module?

The previous design shipped a per-module shell wrapper (`ansible/inventory`, `ansible/cmk_server_inventory`, `ansible/rest_inventory`, …) that each shelled `cmdbsyncer ansible source` or its sibling commands. That worked, but:

- It coupled "what data to serve" with "what filename to point Ansible at", so adding a new module meant adding a new shell file in the repo.
- The wrappers required the Syncer checkout to be the working directory.
- Per-format additions (a Checkmk-DCD endpoint, etc.) would have meant duplicating the dispatch in every module.

With the registry, modules expose data; format adapters expose endpoints. Adding a module touches one plugin; adding a format touches one adapter. The two axes don't multiply.
