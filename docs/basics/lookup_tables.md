# Lookup Tables

A lookup table answers the question "attribute A has the value x, which
value does attribute B get?" from a list, instead of one rule per value.
It is meant for long lists: thousands of entries are fine.

You find them under **Modules > Lookup Tables**.

## The table

Give the table a **Name** (templates refer to it by that name) and paste the
list into **Table**, for example a block copied out of a spreadsheet:

```text
location;datacenter;owner
site-a;DC1;team-a
site-b;DC2;team-b
site-c;DC3;team-c
```

- The **first line names the columns**, the same way as for a
  [pasted list](list_source.md): lower cased, everything that is not a letter,
  digit or underscore becomes `_`.
- The **first column is the key**, every other column is a value.
- The separator is detected from the first line: tab, semicolon, comma or `|`.
- Empty lines are skipped. A key that appears twice, or a table with fewer
  than two columns, cannot be saved.
- Up to 100000 entries per table.

The list view shows how many keys a table has and its columns.

## Using it: `lookup()`

`lookup()` works in every Jinja field (Custom Attributes, Rewrite Attributes,
export rules, ...). In Custom Attributes and Rewrite Attributes the
**Jinja help** button below the value field lists your tables and their
columns and inserts the `lookup()` call for you.

```jinja
{{ lookup('datacenters', location) }}
{# the second column (datacenter) of the line whose key is the value of location #}

{{ lookup('datacenters', location, 'owner') }}
{# the column owner instead #}

{{ lookup('datacenters', location, default='unknown') }}
{# 'unknown' when there is nothing to find #}
```

Signature: `lookup(table, key, column=None, default='')`.
The key is compared exactly (surrounding spaces are ignored). An unknown
table, key or column, an empty cell or a host without the key attribute all
give `default`.

## Example: set the datacenter of a location

Hosts carry a `location`, and their `datacenter` attribute is `unknown` for
some of them. Those should get the datacenter of their location from the list
above.

Create a [Global Custom Attribute](custom_attributes.md) rule:

- **Condition**: attribute `datacenter` is `unknown`
- **Outcome**: attribute name `datacenter`, value
  `{{ lookup('datacenters', location, default='unknown') }}`

Hosts with another datacenter are not touched. The same can be done without a
condition in a single template:

```jinja
{% if datacenter == 'unknown' %}{{ lookup('datacenters', location) }}{% else %}{{ datacenter }}{% endif %}
```

## Changes

Saving or deleting a table resets the cached rule outcomes of the hosts, as
a rule change does, so the next export uses the new values. A process that is
already running (the web interface, a long export) reads a changed table
again within a minute.

Lookup tables are part of the [Rule Import/Export](rule_import_export.md).
