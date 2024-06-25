# Commandline Options

The Checkmk System has the following Command Line Options.
You can access them with _./cmdbsyncer checkmk_

| Parameter              | Description                                                                                                       |
| :--------------------- | :---------------------------------------------------------------------------------------------------------------- |
| debug_host             | Show all Matching Rules and Variable Outcomes                                                                     |
| export_hosts           | [Send Hosts to Given Checkmk Instance](export_rules.md)                                                           |
| export_groups          | [Create Checkmk Groups (based on your rules)](groups_management.md)                                               |
| export_rules           | [Export your Checkmk rules to the Checkmk Instance](export_rules.md)                                              |
| activate_changes       | Activate Checkmk Changes on given Instance                                                                        |
| bake_and_sign_agents   | Bake the Agents in given Instance, You have to set bakery_key_id and bakery_passphrase as Custom Account Settings |
| show_hosts             | Just print out all Host which would be exported to Checkmk                                                        |
| inventorize_hosts      | Run Inventory for attributes, used mainly for Ansible                                                             |
| export_bi_aggregations | Export Checkmk BI Aggregation Rules                                                                               |
| export_bi_rules        | Export Checkmk BI Rules                                                                                           |
| export_downtimes       | Export Downtimes to Checkmk                                                                                       |
| export_tags            | Export Tag Group Config to Checkmk                                                                                |
| export_users           | Export/ Manage Users in Checkmk                                                                                   |
| import_v1              | Import Hosts from Checkmk 1.x                                                                                     |
| import_v2              | Import Hosts from Checkmk 2.x                                                                                     |
| show_hosts             | Print all Hosts which would be exported to Checkmk                                                                |
| show_labels            | List all Labels which later will exist in Checmk                                                                  |
| show_missing_hosts     | Show Hosts which are in Checkmk, but not in Syncer                                                                |

