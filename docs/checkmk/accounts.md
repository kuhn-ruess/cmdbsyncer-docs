# Checkmk Account Settings

The Following Extra Configuration is possible for Checkmk Accounts

| Field                                | Description                                                                                    |
| :----------------------------------- | :--------------------------------------------------------------------------------------------- |
| `limit_by_accounts`                  | Comma seperated list of Account names to only export hosts with matching account               |
| `limit_by_hostnames`                 | Comma seperated list of Hosts to Export                                                        |
| `list_disabled_hosts `               | Print a list of Hosts at the end of the export proccess                                        |
| `dont_delete_hosts_if_more_then`     | Do not delete any host, if the total number of hosts to delete is higher then the given number |
| `dont_activate_changes_if_more_then` | Do not activate changes if the used user created more then the given number of changes         |
| `import_filter` | Simple Filter: Hosts starting with string are not imported |
