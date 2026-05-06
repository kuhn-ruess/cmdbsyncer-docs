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

## Debugging

Add `--debug` to any command to raise exceptions and enable verbose logging. Add `--debug-rules=hostname` to inspect rule outcomes for a specific host. See [Debugging](../basics/debug_rules.md) for details.

Add `--dry-run` to simulate an export without making any changes. Add `--save-requests` to write all planned API requests to a file for review.
