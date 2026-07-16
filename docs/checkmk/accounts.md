# Checkmk Account Settings

These extra settings are available on Checkmk accounts in addition to the standard address, username, and password fields.

| Field                                | Description                                                                              |
| :----------------------------------- | :--------------------------------------------------------------------------------------- |
| `limit_by_accounts`                  | Comma-separated list of account names — only export hosts imported by those accounts. Prefix a name with `!` to exclude it instead (e.g. `!ldap` exports everything except hosts from the `ldap` account) |
| `limit_by_hostnames`                 | Comma-separated list of hostnames — only export these specific hosts                     |
| `limit_by_folders`                   | Only export hosts (and Setup rules) whose target folder is within the given folders — see [Limit Host Export to Folders](limit_host_export_folders.md) |
| `list_disabled_hosts`                | Print a list of disabled hosts at the end of the export run                              |
| `dont_delete_hosts_if_more_then`     | Do not delete any hosts if the total number of hosts to delete exceeds this number       |
| `dont_activate_changes_if_more_then` | Do not activate changes if the number of pending changes exceeds this number             |
| `import_filter`                      | Hosts whose names start with any of the given strings (comma-separated) are not imported |
| `bakery_key_id` / `bakery_passphrase` | Signing key for `bake_and_sign_agents` — see [Bake and Sign Agents](bake_sign.md)       |

Generic account options like `request_timeout` or the SSL certificate fields
apply to Checkmk accounts too — see [Accounts](../basics/accounts.md).

## Safety Thresholds

The `dont_delete_hosts_if_more_then` and `dont_activate_changes_if_more_then` settings act as safety guards. They prevent bulk deletions or large change activations from happening automatically — for example if an import source is temporarily unavailable and returns an empty dataset.

Set these to a value that represents an unexpected number of changes for your environment.

## Object Type Limiting

For large environments with many different object types in the Syncer database, you can limit which object types are considered during an export. This filtering happens directly at the database level and is faster than using standard filter rules.

Go to the Checkmk account, add a Plugin Setting, select the operation, and choose the object types to include.

See also: [Large Environments](big_environments.md)
