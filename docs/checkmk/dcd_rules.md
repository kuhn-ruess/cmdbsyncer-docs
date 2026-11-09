# DCD Rules

You can manage Checkmk DCD (Dynamic Configuration Daemon) connections through the
Syncer. The DCD API can create and delete connections but not change them, so
the export replaces a connection that no longer matches its rule: it deletes it
and creates it again. See [Correcting existing connections](#correcting-existing-connections).

Go to: _Modules → Checkmk → Manage DCD Rules_

DCD rules use the same rule system as all other modules. You can use Jinja
templates in almost every field; the options mirror what you would configure in
the Checkmk DCD UI.

!!! note "Edition & versions"
    DCD is part of the Checkmk **Enterprise / Cloud / (2.5) Pro** editions — it is
    not available in the Raw edition. The export is tested against the **last
    three Checkmk versions (2.3, 2.4 and 2.5)**; the connector payload adapts to
    the version automatically (Checkmk 2.4 changed the REST structure), so the
    same rule works everywhere.

## Static rules

A DCD connection rarely depends on a single host — it is usually a global
connector configuration. Tick **static** on the rule to render it **once**
(host-independent), instead of once per host and de-duplicated. On large
inventories this is much faster. A static rule ignores its match conditions and
is always created. Use it only when the outcome templates reference no host
attributes.

This mirrors the *static* flag on [Setup Rules](rules_management.md).

## Connections from a pasted list

Many DCD connections that only differ in a few values (an ID, a title, a
site) do not need one rule each. Set **Rule source** of the DCD rule to
**From a pasted list** and paste a table whose first line names the
columns, for example:

```text
id;title;site
piggyback_dc1;Datacenter 1;site_a
piggyback_dc2;Datacenter 2;site_b
```

Every row creates the connections of the rule's outcomes, with the columns
as variables: `{{ id }}`, `{{ title }}`, `{{ site }}`. `{{ cmk_site }}` and
`{{ account.<field> }}` are available in every row as well. A row whose
**DCD ID** renders empty creates no connection, identical connections are
created once. A list rule is always host-independent: the host conditions
and the static flag do not apply.

Column names, separators, the preview while you paste and the checks on
save are described in [Rules from a Pasted List](../basics/list_source.md).

## Targeting the right site

A DCD connection is bound to a Checkmk **site**. Set the rule's **Site** field
to:

```jinja
{{ HOST_SITE }}
```

It gives the site the host export puts the host on, with or without Site
Pools. The Syncer takes it from, in this order:

1. a `site` attribute the export rules send as it is,
2. a `site` custom attribute, also the one a Site Pool sets,
3. the `site` in the options of the host's folder, the deepest level first.

Without any of them, and in a static rule or a rule from a list, it is the site
of the exporting account. A site that is only set on the folder in Checkmk
itself is not known to the Syncer. The Site field shows this as a placeholder
hint.

| Variable               | Value                                                                |
| ---------------------- | -------------------------------------------------------------------- |
| `{{ HOST_SITE }}`      | the site the host export gives the host, else the account's site     |
| `{{ cmk_site }}`       | the site of the **exporting account**, from its address (`/<site>`)  |
| `{{ HOST_POOL_SITE }}` | only the site a [Site Pool](site_pools.md) gave the host, else empty |

`{{ cmk_site }}` is the same for every host: it is the site the account talks
to, usually the central site. Its use is one rule for a test and a production
instance with different site names: `export_dcd_rules test-cmk` uses the test
site and `export_dcd_rules prod-cmk` the prod site.

Give a per host rule a **DCD ID** that differs per site too, for example
`piggyback_{{ HOST_SITE }}`. Of several hosts rendering one DCD ID differently
only the first is used, and the export reports it.

## Correcting existing connections

The export compares every connection Checkmk already has with the one the rule
renders. When the **site**, **title**, **comment** or **disabled** state differs,
the connection is deleted and created again with the same DCD ID; the output
shows `Replace Rule <id>, changed: site`. The hosts the connection created stay
in Checkmk, only the connection is replaced.

The connector settings (interval, creation rules, cache times) are not
compared. To change one of them on an existing connection, delete the
connection in Checkmk, the next export creates it with the new settings.

A rule that names a site Checkmk does not know leaves the existing connection
as it is and reports an error, so a typo in the Site field never removes a
working connection.

## Using account attributes — `{{ account.<field> }}`

Any (non-secret) attribute of the **exporting account** is available in every DCD
rule field as `{{ account.<field> }}` — its standard fields (`name`, `address`,
`username`, …) **and any custom field** you configure on the account. This lets a
single rule adapt its values per account without duplicating the rule:

```jinja
{{ account.name }}          # the account name
{{ account.my_custom_field }}   # a custom field you set on the account
```

Configure a custom field on the account (_Modules → Config → Accounts_), then
reference it here. For the test/prod split, give the test and prod accounts the
same custom-field name with different values.

Secrets (`password`, bakery passphrase, CA certificates) and internal ids are
**never** exposed to the template.

## Rule Projects

DCD rules can be assigned to a [Project](../basics/projects.md). They then
show up on the project overview, follow the project's account filter on export
(only exported to the accounts the project allows), and are included in the
project's JSON export/import.

## Command line

```bash
./cmdbsyncer checkmk export_dcd_rules ACCOUNTNAME
```
