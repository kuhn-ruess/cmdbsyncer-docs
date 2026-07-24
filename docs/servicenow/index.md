# ServiceNow

The ServiceNow plugin imports hosts (Configuration Items) from the ServiceNow
[Table API](https://docs.servicenow.com/bundle/latest-application-development/page/integrate/inbound-rest/concept/c_TableAPI.html)
into the Syncer. A typical source is the `cmdb_ci_server` table, but any table
works — you can point it at `cmdb_ci_linux_server`, `cmdb_ci_win_server`,
`cmdb_ci` or a custom table.

## How to Set it Up

1. In ServiceNow, create an API user with read access to the CMDB tables you
   want to import (e.g. the `cmdb_read` role).
2. Create an [Account](../basics/accounts.md) of type **ServiceNow**.
3. Import the data using a [Cron Job](../basics/cron.md) or from the command
   line:

   ```
   ./cmdbsyncer servicenow import_hosts --account ACCOUNTNAME
   ```

## The Account Settings

| Field | Description |
| :---- | :---------- |
| `address` | Instance base URL, e.g. `https://instance.service-now.com` |
| `username` / `password` | Credentials of the ServiceNow API user (Basic Auth) |
| `tables` | Comma-separated list of tables to import (default `cmdb_ci_server`) |
| `hostname_field` | Record field used as the Syncer hostname (default `name`) |
| `rewrite_hostname` | Optional Jinja template to rewrite the hostname |
| `sysparm_query` | Optional [encoded query](https://docs.servicenow.com/bundle/latest-platform-user-interface/page/use/using-lists/concept/c_EncodedQueryStrings.html) to filter records, e.g. `operational_status=1` |
| `sysparm_fields` | Optional comma-separated field list to limit the imported columns |
| `sysparm_display_value` | `true` (default) returns human-readable display values instead of sys_ids |
| `sysparm_limit` | Page size for paging through large tables (default `1000`) |

The plugin pages through each table with `sysparm_offset` / `sysparm_limit`,
so tables of any size are imported completely. Every record becomes a host
whose labels are the record's fields; reference fields are folded down to their
display value.

## Rewrite Fields

ServiceNow field names (like `install_status` or reference fields) can be
transformed for export with the [Rewrite Attributes](../basics/rewrite_attributes.md)
feature of the target module, exactly as with any other import source.
