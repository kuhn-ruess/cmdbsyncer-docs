# Playbook Fire Rules

A rule-driven way to dispatch playbooks against matching hosts — useful for onboarding workflows where every freshly imported Linux host should get the Checkmk agent rolled out without an admin clicking a button.

The editor lives under **Modules → Ansible → Playbook Fire Rules**.

## How it works

1. You define a rule with the standard condition engine (match on hostname, attribute, anyway, …).
2. Each rule has one or more outcomes selected from the [playbook manifest](playbook_manifest.md). Outcomes are picked from a dropdown that pulls the same list as the [Run Playbook page](run_from_ui.md), so you cannot typo a filename into a no-op. Each outcome also has an **Inventory** dropdown that overrides the playbook's manifest-default provider — useful when one rule needs to fire a playbook against a different rule source than the playbook normally uses.
3. The `ansible fire_playbook_rules` CLI / cron command iterates all available hosts, evaluates the enabled rules, and dispatches one playbook run per matching `(rule, host, playbook)` triple — **once**.

Dedup is enforced by looking at [Run History](run_from_ui.md#run-history): if there is already a row with `source = rule`, matching `playbook` + `target_host` + `rule_id`, the rule will not fire again. To re-fire, delete the run record.

> **Important**: fire-rule evaluation is intentionally kept out of the inventory hot path. Read-only `ansible-inventory --list` calls and `cmdbsyncer ansible inventory <provider> --list` will **not** start playbook runs. Firing happens only from the dedicated CLI/cron command, which keeps inventory queries cheap and side-effect-free.

## CLI

```bash
./cmdbsyncer ansible fire_playbook_rules
```

Prints the number of dispatched runs. Each dispatch is recorded in the Run History with `source = rule` and `triggered_by = rule:<rule_id>`.

## Cronjob

The command is registered as **"Ansible: Fire Playbook Rules"** so you can attach it to a [Cronjob Group](../basics/cron.md). A common setup:

| Group | Interval | Why |
| :---- | :------- | :-- |
| Hourly | `Every hour` | Picks up newly imported hosts within an hour of CMDB import. |

## Re-firing

Because dedup is based on a Run History row, the way to re-trigger a fire-rule for a host is to delete the corresponding row from the Run History and run the cron command again. This is by design — re-running a successful onboarding playbook needs an explicit human action, not a default.

## Example

Goal: roll the Checkmk agent out automatically to every newly imported Linux host.

| Rule field | Value |
| :--------- | :---- |
| Condition | `match_type = tag`, tag `os` equals `Linux` |
| Outcome | playbook `cmk_agent_mngmt.yml`, extra_vars `cmk_install_agent=true cmk_register_tls=true` |

After enabling the rule and running `ansible fire_playbook_rules` (or letting cron pick it up), each matching host gets one Run History entry. Subsequent runs of the cron command skip already-fired hosts.
