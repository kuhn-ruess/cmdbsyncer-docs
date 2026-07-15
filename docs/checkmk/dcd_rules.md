# DCD Rules

You can manage Checkmk DCD (Dynamic Configuration Daemon) connections through the
Syncer. Unlike most other Checkmk modules, the DCD API supports creating and
deleting connections but not updating them in place — so this module creates and
deletes rules rather than syncing them.

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

## Targeting the right site — `{{ cmk_site }}`

A DCD connection is bound to a Checkmk **site**. When you deploy the same rule to
more than one Checkmk (for example a test and a production instance) the site
names usually differ. Set the rule's **Site** field to:

```jinja
{{ cmk_site }}
```

It resolves to the **exporting account's** Checkmk site — taken from the account
address (which ends in `/<site>`). So `export_dcd_rules test-cmk` uses the test
site and `export_dcd_rules prod-cmk` uses the prod site, from one rule. The Site
field shows this as a placeholder hint.

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

DCD rules can be assigned to a [Setup Rule Project](rule_projects.md). They then
show up on the project overview, follow the project's account filter on export
(only exported to the accounts the project allows), and are included in the
project's JSON export/import.

## Command line

```bash
./cmdbsyncer checkmk export_dcd_rules ACCOUNTNAME
```
