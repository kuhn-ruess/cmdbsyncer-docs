# Hosts, Labels and Inventory

CMDBsyncer works with three types of data: Hosts, Labels, and Inventory.

## Hosts

A host is any kind of device or object. It is identified by its hostname, bound to a source account, and carries Labels and Inventory data.

Hosts can have different **object types** — for example `host`, `application`, `contact`, `group`, or `cmk_site`. The object type controls which rules and exports apply to it.

## Labels and Inventory

Labels and Inventory are both key:value pairs. They can be used in all rules, rewritten, and filtered. The difference lies in how they are managed.

**Labels** are imported and fully controlled by the import plugin. When the source changes or removes a label, the Syncer reflects that change.

**Inventory** data can come from multiple sources simultaneously. Each source identifies its keys with a namespace prefix on the attribute name.

Example:

```text
csv__ipaddress: 127.0.0.1
csv__alias: Test Server
srctest__service_name: Test Service
```

Here, the `csv` plugin controls all keys starting with `csv__`, and the `srctest` plugin controls its own namespace. This prevents conflicts when multiple sources provide data for the same host.

## Account Options for Inventorize

Every module provides an inventorize endpoint that enriches host data with additional attributes. The behavior is configured via the account settings.

| Option                               | Description                                                                                                                                                                   |
| :----------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `inventorize_key`                    | Namespace prefix used for all attribute names from this source                                                                                                                |
| `inventorize_match_by_domain`        | If enabled, matches inventory data by domain name (not available in all modules)                                                                                              |
| `inventorize_match_attribute`        | Restrict inventory to hosts that have a specific attribute value. Example: `application=dns` only adds inventory data to hosts where `application` contains `dns`             |
| `inventorize_collect_by_key`         | If an attribute on the host contains the name of another host, that other host receives the attribute added to its inventory (numerated), containing the originating hostname |
| `inventorize_rewrite_collect_by_key` | Rewrite the `collect_by_key` value using a Jinja template before using it as a lookup key                                                                                     |

## CMDB Mode

CMDBsyncer can also act as a lightweight CMDB itself — without requiring an external source system. In this mode, you create and maintain objects and hosts directly in the UI, assign them to templates, and manage custom fields.

See [Use as CMDB](../cmdb/index.md) for full documentation on CMDB mode, templates, and the `cmdb_match` automatic assignment feature.
