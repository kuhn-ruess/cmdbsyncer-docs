# Filter

Every module has a filter section that controls which hosts and which attributes are exported. Filters are configured per module and per account.

Go to the filter section of the module you want to configure, for example: _Modules → Checkmk → Filter_

!!! tip
    The Syncer can hold hundreds of attributes per host. By default, none of them are exported to a target system such as Checkmk. You need to explicitly whitelist the attributes you want to export.

## Filter Actions

| Action                         | Description                                                                                        |
| :----------------------------- | :------------------------------------------------------------------------------------------------- |
| Whitelist Attribute            | Only export attributes whose name matches. Use `NAME*` to match all attributes starting with NAME. |
| Whitelist Attribute with Value | Only export attributes whose value matches. Wildcard `*` supported at the end.                     |
| Ignore Matching Hosts          | Hosts matching this rule are excluded from the export entirely.                                    |

Filter rules support the same [Conditions](conditions.md) as all other rules — you can restrict which hosts a filter applies to.

## Whitelist Attribute

Use this action to select which attributes are exported by name. The attribute name can be an exact match or a prefix with a wildcard:

- `ipaddress` — exports only the attribute named `ipaddress`
- `cmk__*` — exports all attributes whose name starts with `cmk__`

## Whitelist Attribute with Value

Use this action to export only attributes whose _value_ matches. Useful for exporting only label values that meet a certain pattern, regardless of the attribute name.

## Ignore Matching Hosts

Use this action to exclude entire hosts from the export. Hosts matching the rule condition are skipped completely.

## Account Filter Negation

Since version 3.12.2, filter values can be negated by prefixing the value with `!`. This allows you to exclude specific values instead of whitelisting:

```text
!test-*
```

This exports everything _except_ attributes or hosts matching `test-*`.
