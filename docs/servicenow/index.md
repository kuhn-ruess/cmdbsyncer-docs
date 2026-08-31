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
   ./cmdbsyncer service_now import_hosts ACCOUNTNAME
   ```

## The Account Settings

| Field | Description |
| :---- | :---------- |
| `address` | Instance base URL, e.g. `https://instance.service-now.com` |
| `api_path` | Path in front of `/table/<name>`, `/api/now` for a plain instance. Set it to the context path of an API gateway that sits in front of ServiceNow, or leave it empty if the gateway publishes the tables directly under the address |
| `username` / `password` | Credentials of the ServiceNow API user (Basic Auth) |
| `tables` | Comma-separated list of tables to import (default `cmdb_ci_server`) |
| `hostname_field` | Record field used as the Syncer hostname (default `name`) |
| `rewrite_hostname` | Optional Jinja template to rewrite the hostname |
| `sysparm_query` | Optional [encoded query](https://docs.servicenow.com/bundle/latest-platform-user-interface/page/use/using-lists/concept/c_EncodedQueryStrings.html) to filter records, e.g. `operational_status=1` |
| `sysparm_fields` | Optional comma-separated field list to limit the imported columns |
| `sysparm_display_value` | `true` (default) returns human-readable display values instead of sys_ids |
| `sysparm_limit` | Page size for paging through large tables (default `1000`) |
| `inventorize_key` | Prefix of the inventory attributes the child tables are stored under (e.g. `snow`) |
| `inventorize_tables` | Tables attached to an existing host instead of imported as hosts, as `table:matcher` pairs — the matcher being the record field that names the server (`cmdb_ci_network_adapter:cmdb_ci`) or `rel` to look the host up in the relationship table (`cmdb_ci_cluster:rel`) |
| `inventorize_relation_types` | Relation types followed for the `rel` matcher, comma separated, e.g. `Contains::Contained by`. Empty reads every relation |
| `inventorize_host_label` | Host label holding the ServiceNow name, used to find the host a record references (default `name`). Empty matches the hostname directly |
| `inventorize_rewrite_parent` | Optional Jinja template that adapts the server name a child record references, the way `rewrite_hostname` adapts an imported one |
| `custom_headers` | Extra headers for every request, as `Name: value` pairs separated by a pipe — an API key or tenant header a gateway in front of the instance wants, see [Accounts](../basics/accounts.md#custom-request-headers) |

The plugin pages through each table with `sysparm_offset` / `sysparm_limit`,
so tables of any size are imported completely. Every record becomes a host
whose labels are the record's fields; reference fields are folded down to their
display value.

## Behind an API Gateway

Not every installation talks to the instance directly — an API gateway in
front of it publishes the same tables under its own context path, for
example `https://gateway.example.com/servicenow/table/cmdb_ci_unix_server`
instead of `https://instance.service-now.com/api/now/table/cmdb_ci_unix_server`.

If the gateway also wants a key or tenant header of its own, put it into the account's `custom_headers` field.

Put the part in front of `/table/<name>` into `api_path`: `/servicenow` for
the example above, or an empty value if the gateway offers the tables
straight behind the address. The account keeps working as before when the
field is not set at all — then `/api/now` of a plain instance is used.

## Network Adapters and Databases of a Server

Tables like `cmdb_ci_network_adapter` or `cmdb_ci_db_instance` do not hold servers — their records belong *to* a server. Importing them as hosts of their own would fill the Syncer with objects that are not hosts. Put them into `inventorize_tables` instead, together with the field that names the server they belong to:

```
inventorize_key            = snow
inventorize_tables         = cmdb_ci_network_adapter:cmdb_ci, cmdb_ci_cluster:rel
inventorize_relation_types = Contains::Contained by
```

Every entry is one table and the way its records find their host, and the list grows the same way for every further table you want to read.

### The two matchers

`table:<field>` — the named field of the record holds the name of the host. `cmdb_ci_network_adapter` carries a `cmdb_ci` reference to its server that way. **Query Table** shows every field of a record, so you can see which one holds the server name; with `sysparm_display_value=true` it contains the name itself, not the sys_id.

`table:rel` — the host is looked up in ServiceNow's relationship table `cmdb_rel_ci`. Use it for the many CI classes that carry no reference of their own — a cluster, an application or a database is linked to its server there, not through a field. Both directions are searched, so it does not matter whether your host stands in `parent` or in `child`.

Reading the whole relationship table would be slow, so narrow it to the types you care about:

```
inventorize_relation_types = Contains::Contained by
```

Several types are separated by commas, an empty value reads them all. The types are the ones ServiceNow shows on the relationship, e.g. `Contains::Contained by`, `Runs on::Runs`, `Owns::Owned by`. The table is read once per run, however many tables use `rel`.

Then run:

```
./cmdbsyncer service_now inventorize_data ACCOUNTNAME
```

### Finding the host

A relation and a reference field name the CI — `ldom-s02` — while the import may have created the host under another name, with the domain appended: `ldom-s02.munich-airport.de`. The name ServiceNow uses is on the host as a label, so `inventorize_host_label` (default `name`) says which label identifies it. The account's hosts are read once per run and looked up from memory. A CI no host carries falls back to `inventorize_rewrite_parent`, and is otherwise reported as an unknown host.

### One key, several tables

All tables share the single `inventorize_key`; the table name is appended to it, so `snow` becomes `snow_cmdb_ci_cluster` and `snow_cmdb_ci_network_adapter`. Each table therefore owns its own attributes and only ever replaces its own on the next run — reading more tables never overwrites what another one delivered.

Every record becomes a numbered group of inventory attributes under `<inventorize_key>_<table>`, so a server with three network cards keeps all three:

```
snow_cmdb_ci_network_adapter__0_name        eth0
snow_cmdb_ci_network_adapter__0_ip_address  10.0.0.1
snow_cmdb_ci_network_adapter__1_name        eth1
snow_cmdb_ci_network_adapter__1_ip_address  10.0.0.2
```

A record that is related to several servers lands on each of them. Records that find no host are counted in the job log and skipped. Hosts are never created here; a record referencing a server the Syncer does not know is reported and ignored.

If the import writes the hosts under a different name than the child records reference — the import appends a domain, the reference names the short server — `inventorize_rewrite_parent` adapts the referenced name the same way, e.g. `{{HOSTNAME}}.example.com`.

## Query a Table

**Modules → ServiceNow → Query Table** queries one table read only, exactly
the way the import reads it. Pick the account and its settings — table,
API path, query, field list, display values and hostname field — are filled
in and can be changed for the single query without touching the account.

The result shows the request that was sent and, for every record, all the
fields it really has plus the name it would be imported under, or that it
would be skipped because the hostname field is empty. Use it to check a new
account before the first import: a wrong login, a wrong path or the wrong
hostname field are visible right away. Nothing is written — neither in
ServiceNow nor in the Syncer.

The page needs the `servicenow` role (or a global admin).

## Rewrite Fields

ServiceNow field names (like `install_status` or reference fields) can be
transformed for export with the [Rewrite Attributes](../basics/rewrite_attributes.md)
feature of the target module, exactly as with any other import source.
