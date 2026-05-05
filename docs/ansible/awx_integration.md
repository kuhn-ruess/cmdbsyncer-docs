# AWX / Semaphore / Ansible Automation Platform

If your shop already runs AWX, Red Hat Ansible Automation Platform (AAP), or Semaphore, you can plug the Syncer in as a **dynamic inventory source** and keep using your existing job-template/template-survey workflow. The Syncer becomes the single source of truth for "which hosts exist and what attributes do they have" while AWX/AAP/Semaphore remain in charge of execution, RBAC, schedules, and notifications.

Under the hood the integration uses the Syncer's [inventory provider registry](inventory_providers.md) — the remote control node hits `/api/v1/inventory/ansible/<provider>` over HTTPS, and the same endpoint can serve any module's host catalogue (host inventory, Checkmk sites, …) by switching the `provider` option in the inventory YAML.

The integration relies on the [`cmdbsyncer-inventory`](cmdbsyncer_inventory.md) PyPI plugin — it speaks the Syncer REST API over HTTPS, so the AWX/Semaphore execution environment never needs filesystem access to the Syncer host.

## Common prerequisites

1. In the Syncer, create a [User](../installation/authentication.md) dedicated to the integration with the **`ansible`** API role and an API token.
2. From any AWX/AAP/Semaphore execution environment, verify the Syncer REST endpoint is reachable:

    ```bash
    curl -H "x-login-token: <TOKEN>" https://<syncer-host>/api/v1/inventory/ansible/
    ```

    A JSON inventory comes back if everything is wired up.

## AWX / Ansible Automation Platform

AWX (and its supported sibling AAP) treats inventories as objects you point at a script or plugin. With `cmdbsyncer-inventory` you have two options.

### Option A — execution-environment image with the plugin baked in

Recommended for production: build a custom EE image that has `cmdbsyncer-inventory` pre-installed.

```Dockerfile
# Dockerfile (custom EE)
FROM quay.io/ansible/awx-ee:latest
RUN pip install cmdbsyncer-inventory
```

In AWX:

1. **Settings → Execution Environments** → register the new image.
2. **Resources → Credentials** → create a credential of type **Custom Credential Type** (or use a Vault credential) holding the Syncer URL + token. Two custom fields suffice:

    | Custom field name | Source |
    | :---------------- | :----- |
    | `CMDBSYNCER_URL` | env, e.g. `https://syncer.example.com` |
    | `CMDBSYNCER_TOKEN` | env, marked as `secret = True` |

3. **Resources → Inventories → Add Inventory → Sources → Add Source**:
    - Source: *Sourced from a Project* with a small project containing the YAML below, **or** *Custom Inventory Plugin* and reference `cmdbsyncer.inventory`.
    - Credential: the one created above.
    - Update on launch: enabled, so every job template runs against fresh data.

    ```yaml
    # inventory.yml inside the AWX project
    plugin: cmdbsyncer.inventory
    url: "{{ lookup('env', 'CMDBSYNCER_URL') }}"
    token: "{{ lookup('env', 'CMDBSYNCER_TOKEN') }}"
    ```

4. Bind any of the bundled or local playbooks (e.g. `cmk_agent_mngmt.yml`) as a Job Template against the inventory. AWX will request hosts from the Syncer at launch time.

### Option B — virtualenv-based control node

For self-managed AWX runners (or AAP execution nodes you control), `pip install cmdbsyncer-inventory` into the same virtualenv that runs `ansible-playbook`. The same `inventory.yml` plugin spec applies.

### Notes

- The Syncer's [Run History](run_from_ui.md#run-history) only logs runs that go *through the Syncer* (UI / fire rule / CLI). Runs launched by AWX bypass it — observability lives in AWX/AAP. Use both: AWX for who-launched-what, the Syncer for inventory truth and onboarding-rule firings.
- If you need per-host vars at job time, the same dynamic inventory plugin call returns the full attribute payload, so AWX surveys can read CMDB attributes natively.

## Semaphore

[Semaphore](https://semaphoreui.com/) calls them "inventories" too, but expects an inventory file or script. Use either form:

### As a script

1. On the Semaphore host, install the inventory plugin:

    ```bash
    pip install cmdbsyncer-inventory
    ```

2. Create a wrapper script `/etc/semaphore/cmdbsyncer-inventory.sh`:

    ```bash
    #!/bin/sh
    export CMDBSYNCER_URL="https://syncer.example.com"
    export CMDBSYNCER_TOKEN="..."
    exec ansible-inventory -i cmdbsyncer.inventory --list "$@"
    ```

3. In Semaphore: **Project → Inventory → New** → type `Static`, paste the wrapper script's path or upload the resolved inventory YAML.

### As an `inventory.yml` plugin spec

If your Semaphore version supports the dynamic inventory plugin format directly, drop the same YAML used in AWX into the project's repository and reference it from the inventory definition:

```yaml
plugin: cmdbsyncer.inventory
url: "https://syncer.example.com"
token: "{{ lookup('env', 'CMDBSYNCER_TOKEN') }}"
```

Pass `CMDBSYNCER_TOKEN` as an environment variable from a Semaphore secret.

## Troubleshooting

| Symptom | Likely cause |
| :------ | :----------- |
| AWX inventory sync returns "no hosts" | The token's user has the wrong API role. The user needs the `ansible` role; `all` works too. |
| `403 Forbidden` from `/api/v1/inventory/ansible/` | Account locked or token revoked. Check **Settings → Users** in the Syncer. |
| Hosts appear but attributes are empty | The user is allowed to read inventory but the [filter rule](../basics/filter.md) ignores them. Run `ansible debug_filter` to confirm. |
| AWX project sync fails on TLS | Self-signed Syncer cert. Either add the cert to the AWX EE trust store or set `validate_certs: false` in the inventory.yml (not recommended). |

## See also

- [`cmdbsyncer-inventory` plugin reference](cmdbsyncer_inventory.md) — full list of plugin options.
- [Run Playbook UI](run_from_ui.md) — when AWX/AAP is too heavy and you just want a Run button.
