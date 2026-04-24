# cmdbsyncer-inventory Plugin

`cmdbsyncer-inventory` is a standalone Ansible dynamic inventory plugin that talks to the Syncer REST API and returns hosts and host variables directly to Ansible. Unlike the shell-script wrappers shipped in the Syncer's `ansible/` folder (`inventory`, `docker_inventory`, `rest_inventory`, …), this plugin is a proper Ansible inventory plugin and does not require the Syncer checkout on the control host.

Use it when:

- your Ansible control node is separate from the Syncer and you cannot run the Syncer CLI there,
- you want a first-class Ansible inventory plugin instead of a shell wrapper,
- you want to install the integration via `pip` on the control node.

Source: [kuhn-ruess/cmdbsyncer-inventory](https://github.com/kuhn-ruess/cmdbsyncer-inventory) · PyPI: [cmdbsyncer-inventory](https://pypi.org/project/cmdbsyncer-inventory/).

## Installation

```bash
pip install cmdbsyncer-inventory
python -m cmdbsyncer_inventory
```

The second command registers the plugin with your active Ansible installation so `ansible-inventory` and `ansible-playbook` can load it by name. Run it once per Python environment you use for Ansible.

If installing with a venv per project, activate it before running the two commands above.

## Syncer-side Requirements

The plugin reaches the Syncer through the Ansible REST endpoint. Before it works, the Syncer must have:

- At least one **API user** with `ansible` permissions (Users → Details → API access).
- Ansible **rules** (filter, rewrite, actions) configured so the endpoint returns the hosts you care about. This is the same rule set used by the `cmdbsyncer ansible source` CLI.

Verify on the Syncer host that `GET /api/v1/ansible/` returns JSON for your API user:

```bash
curl -H "x-login-user: USER:SECRET" https://your-syncer/api/v1/ansible/ | head
```

## Inventory Configuration

Create an inventory file named with the `.yml` or `.yaml` suffix — the filename suffix is how Ansible dispatches to the plugin:

```yaml
# inventory.yml
plugin: cmdbsyncer_inventory
api_url: https://your-cmdbsyncer.example.com
username: apiuser       # optional if env vars are set
password: apisecret     # optional if env vars are set
verify_ssl: true        # set to false only for self-signed test instances
```

Credentials can also come from environment variables (recommended, so they do not end up in git):

```bash
export CMDBSYNCER_APIUSER="apiuser"
export CMDBSYNCER_APIPASSWORD="apisecret"
```

Environment variables take precedence over the values in the YAML file.

## Using the Plugin

```bash
# List all hosts and groups the Syncer returns
ansible-inventory -i inventory.yml --list

# Details for one host
ansible-inventory -i inventory.yml --host web1.example.com

# Run a playbook against it
ansible-playbook -i inventory.yml site.yml
```

Host variables in the Syncer (set via labels, attributes or rules) are returned as Ansible host vars and are available inside the playbook as `{{ var_name }}`.

## Troubleshooting

**`REST API responded with status 401`** — the Syncer rejected the credentials. Double-check `CMDBSYNCER_APIUSER`/`CMDBSYNCER_APIPASSWORD` (or `username`/`password` in the YAML), and that the user has API/Ansible permission in the Syncer.

**Empty host list** — the Syncer has no rules that match, or the matched rules don't emit Ansible output. Validate on the Syncer with `cmdbsyncer ansible debug_filter -l` and `cmdbsyncer ansible source --list`.

**`plugin: cmdbsyncer_inventory` not recognised** — the plugin was not registered in this Python environment. Re-run `python -m cmdbsyncer_inventory` inside the venv that Ansible uses.

**SSL verify errors against a test Syncer** — set `verify_ssl: false` in the YAML file. Do not do this in production; use a proper certificate instead.

## When to Use Which Integration

| Use case | Recommended |
|:---------|:-----------|
| Ansible on the same host as the Syncer | Shell wrappers in `ansible/` (`inventory`, `inventory_single`) |
| Ansible on a remote control node, Syncer reachable via HTTPS | `cmdbsyncer-inventory` (this plugin) |
| Ansible running inside the Syncer Docker stack | `docker_inventory` shell wrapper |
| One-off shell script without Python on the control node | `rest_inventory` shell wrapper |
