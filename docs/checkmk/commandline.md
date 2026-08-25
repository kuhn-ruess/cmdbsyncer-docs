# Commandline Parameters

Access all Checkmk commands with `./cmdbsyncer checkmk <command> <account>`.

| Command                | Description                                                                    |
| :--------------------- | :----------------------------------------------------------------------------- |
| export_hosts           | Export hosts to the Checkmk instance                                           |
| export_groups          | Create Checkmk groups based on your rules                                      |
| export_rules           | Export Checkmk setup rules to the instance                                     |
| export_tags            | Export host tag group configuration to Checkmk                                 |
| export_users           | Create, update, or disable users in Checkmk                                    |
| export_downtimes       | Export scheduled downtimes to Checkmk                                          |
| export_notifications   | Export notification rules to Checkmk (2.4 / 2.5 only)                          |
| export_dcd_rules       | Export DCD (Dynamic Configuration) rules to Checkmk                            |
| export_bi_aggregations | Export BI aggregation rules to Checkmk                                         |
| export_bi_rules        | Export BI rules to Checkmk                                                     |
| activate_changes       | Activate pending changes on the Checkmk instance                               |
| bake_and_sign_agents   | Bake agents — requires bakery_key_id and bakery_passphrase in account settings |
| import_v2              | Import hosts from Checkmk 2.x into the Syncer                                  |
| import_v1              | Import hosts from Checkmk 1.x into the Syncer                                  |
| inventorize_hosts      | Run inventory to fetch attributes from Checkmk into the Syncer                 |
| show_hosts             | Print all hosts that would be exported to Checkmk                              |
| show_labels            | List all labels that would be set in Checkmk after the sync                    |
| show_missing_hosts     | Show hosts present in Checkmk but not in the Syncer                            |
| assign_template        | Assign a CMDB template to every host of a Checkmk folder (see below)           |
| analyse_rules          | Find Setup Rules whose export lists hundreds of hostnames and suggest a host label (account optional) |

## Improve Setup Rules that name every host individually
<span class="since">Since 4.3</span>

`analyse_rules` finds the Setup Rules whose export ends up listing hundreds of
hostnames in one condition, and the host attribute that could replace that list.
It can apply the change for you. See
[Rule Optimization](rule_optimization.md) for the full description.

```bash
./cmdbsyncer checkmk analyse_rules --min-hosts 50
```

| Option | Description |
| :----- | :---------- |
| `--min-hosts` | Only report rules built from at least this many hosts (default: 10). |
| `--top` | How many of the largest rules to report (default: 20). |
| `--apply` | Make the change instead of only reporting it. |
| `--hash-labels` | With `--apply`: match on a hash instead of letting raw attribute values through as Checkmk labels. |

The account argument is optional, and nothing is ever sent to Checkmk.

## Assign a CMDB template from a Checkmk folder
<span class="since">Since 4.3</span>

Unlike the commands above, `assign_template` takes extra arguments — the Checkmk
folder and the template name:

```bash
./cmdbsyncer checkmk assign_template <account> <folder> <template> [--dry-run]
```

It reads the hosts of the given Checkmk folder and assigns the named CMDB template to
each host that exists in the Syncer. Use `--dry-run` to preview which hosts would be
changed without writing anything.

## Debugging

Add `--debug` to any command to raise exceptions and enable verbose logging. Add `--debug-rules=hostname` to inspect rule outcomes for a specific host. See [Debugging](../basics/debug_rules.md) for details.

Add `--dry-run` to simulate an export without making any changes. Add `--save-requests` to write all planned API requests to a file for review.
