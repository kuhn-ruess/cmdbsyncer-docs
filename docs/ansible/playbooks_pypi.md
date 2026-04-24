# Default Playbooks with a PyPI Install

The [PyPI installation](../installation/setup_pip.md) ships only the Python application — not the reference Ansible playbooks (`cmk_agent_mngmt.yml`, `cmk_server_mngmt.yml`, `cmk_omd_cleanup.yml`, the `cmk_host_agent` / `cmk_server_mngmt` / `server_mngmt` roles and the `inventory` / `docker_inventory` / `rest_inventory` wrappers). They live in the [Git repository](https://github.com/kuhn-ruess/cmdbsyncer) under `ansible/` because they are meant to be copied, adapted and versioned alongside your own automation.

## One command

After `pip install cmdbsyncer`, run:

```bash
cd /opt/cmdbsyncer    # your working directory
cmdbsyncer sys install_playbooks ./ansible
```

This downloads the playbook set matching your installed Syncer version from GitHub and drops it at `./ansible/`. No repo clone or sparse-checkout gymnastics required. The command accepts `--version <ref>` (to pin a different git ref), `--repo <url>` (fork / mirror), and `--force` (to overwrite an existing folder).

Install the Ansible Python dependencies once:

```bash
pip install -r requirements-ansible.txt
```

Then run playbooks from `/opt/cmdbsyncer/ansible/` as normal:

```bash
cd /opt/cmdbsyncer/ansible
ansible-playbook -i inventory cmk_agent_mngmt.yml
```

Updating the playbooks later: rerun with `--force`:

```bash
cmdbsyncer sys install_playbooks ./ansible --force
```

## Remote Ansible control node

If the Ansible control node is a **different host** than the Syncer, skip the playbook copy and use the dedicated dynamic-inventory plugin on that control node instead:

```bash
pip install cmdbsyncer-inventory
python -m cmdbsyncer_inventory
```

See [cmdbsyncer-inventory Plugin](cmdbsyncer_inventory.md) for the inventory file, credentials and usage.
