# Playbook Manifest

The Syncer surfaces playbooks in the [Run Playbook page](run_from_ui.md) and in the [Fire Rule dropdown](fire_rules.md) from a manifest file. Files not listed in the manifest stay invisible — that gives admins explicit control over what shows up in the UI.

Two files are read, in this order, and merged:

| File | Purpose | Tracked in git |
| :--- | :------ | :-------------: |
| `ansible/playbooks.yml` | Bundled catalog. Ships with the Syncer and seeds the four reference playbooks. | yes |
| `ansible/playbooks.local.yml` | Site-local additions and overrides. | **no** (gitignored) |

Local entries are merged on top of the bundled manifest. An entry with the same `file` overrides the bundled one — that is how you rename a shipped playbook for your users without diverging from the upstream catalog.

## Schema

```yaml
playbooks:
  - file: cmk_agent_mngmt.yml          # required, must exist in ansible/
    name: "Checkmk: Manage Host Agent" # required, shown in the UI
    description: "Install/update the Checkmk agent and register TLS / bakery."
```

| Key | Required | Notes |
| :-- | :------: | :---- |
| `file` | yes | Filename relative to the `ansible/` directory (or to `CMDBSYNCER_ANSIBLE_DIR`). Must exist on disk; missing files are dropped at load time with a warning. |
| `name` | yes | Friendly label shown in the Run Playbook list and as the SelectField label in Fire Rules. |
| `description` | no | Reserved for future detail rendering. |

## Adding a custom playbook

1. Drop your playbook into `ansible/`, e.g. `ansible/restart_haproxy.yml`.
2. Add an entry to `ansible/playbooks.local.yml` (create the file if it doesn't exist):

    ```yaml
    playbooks:
      - file: restart_haproxy.yml
        name: "HAProxy: Rolling Restart"
    ```

3. Reload the Syncer page — the new entry appears in the Run Playbook list and in the Fire Rule SelectField. No service restart required: the manifest is read on every form render.

## Renaming a bundled playbook

Override by `file` in the local manifest:

```yaml
# ansible/playbooks.local.yml
playbooks:
  - file: cmk_agent_mngmt.yml
    name: "Onboard Linux Host (Checkmk Agent)"
```

The bundled "Checkmk: Manage Host Agent" entry is replaced by the local one for everyone using this Syncer instance.
