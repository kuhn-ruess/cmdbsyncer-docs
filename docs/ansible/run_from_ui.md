# Run Playbooks from the Syncer UI

For users who don't want to SSH into the control node every time, the Syncer can dispatch the bundled playbooks (and any of your own that you register) directly from the web UI. Every invocation is captured with full log output so the history view doubles as an audit trail.

The relevant menu entries live under **Modules → Ansible**:

| Menu | Purpose |
| :--- | :------ |
| Run Playbook | Pick a playbook from the catalog and dispatch it. |
| Run History | Read-only audit of every UI / rule / CLI run, with the captured `ansible-playbook` log. |

Access requires the **`ansible`** permission on the user account — the same role that gates the rule editors.

## Run Playbook page

Each playbook from the [manifest](playbook_manifest.md) shows up as a card with two optional inputs and two buttons:

| Field | Effect |
| :---- | :----- |
| **Inventory Provider** | The rule source feeding this run. Defaults to the playbook's manifest `inventory:` field; override to point at a different [project](projects.md) without editing the manifest. |
| **Limit** | Maps to `--limit` — restrict the run to a host or group, e.g. `webserver01` or `windows`. Empty means "all hosts in the inventory". |
| **Extra Vars** | Maps to `-e`. Free-form, e.g. `cmk_install_agent=true cmk_main_site=main`. |
| **Preview** | Runs `ansible-playbook --check --diff`. No changes are applied; the rendered diff lands in the run log so you can review it before clicking Run. |
| **Run** | Runs the playbook for real. |

After clicking, the page redirects to the freshly created run record. Status is `Running` while the daemon thread executes; refresh to see it transition to `Success` / `Failure`. The full stdout/stderr is rendered inline as a scrollable log block.

## Run History

The history table sorts by `started_at` descending and offers filters for **playbook**, **host**, **status**, **mode** (run / preview), and **source** (UI / rule / CLI). Use it to:

- Investigate a failed run — open the row to see the captured log.
- Distinguish dry-runs from real changes via the **Mode** column.
- Force a re-fire of a [rule-driven](fire_rules.md) playbook by deleting its history row (the dedup key is `playbook + host + rule_id`).

Exports are available in xlsx / csv via the Export button at the top of the table.

## CLI parity

Everything the UI can dispatch is also reachable from the shell. Each CLI run becomes a Run History row with `source = cli`:

```bash
./cmdbsyncer ansible fire_playbook_rules
```

(other subcommands behave the same way they always have — only the recording is new.)

## Requirements

- `ansible-playbook` must be on the Syncer's `PATH`. Override via the `CMDBSYNCER_ANSIBLE_PLAYBOOK_BIN` env var or the `ANSIBLE_PLAYBOOK_BIN` Flask config key.
- The playbook directory defaults to `<repo>/ansible/`. Override via `CMDBSYNCER_ANSIBLE_DIR` / `ANSIBLE_DIR` if you ship playbooks from a non-default location.
