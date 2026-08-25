# Rewrite Attributes

Different target systems have different requirements for attribute names and values. Rewrite rules let you rename, transform, or derive new attributes for each module independently.

Go to the Rewrite Attributes section of the module you want to configure (for example, _Modules → Checkmk → Rewrite Attributes_).

**Example:** An import from CSV gives you `csv__ipaddress`. With a rewrite rule, you can rename it to `ipaddress` before it is exported to Checkmk.

## Operations for Attribute Names

| Function                      | Description                                                                           |
| :---------------------------- | :------------------------------------------------------------------------------------ |
| Don't Use                     | Keep the original attribute name. Use with a new attribute name to create a copy.     |
| Overwrite with fixed String   | The value in New Attribute Name replaces the original attribute name                  |
| Overwrite with Jinja Template | Build the new attribute name with Jinja — access all host attributes and {{HOSTNAME}} |
| Convert List of Strings       | Create multiple new attributes from a list — one attribute per list item              |

### Convert List of Strings

This function creates multiple new attributes from a list, one attribute per list item. The list can come from an existing attribute or be built with Jinja.

Set _Old Attribute Name_ to the source attribute. Use `{{result}}` in _New Attribute Name_ to reference the current list item.

If the attribute already contains a Python list such as `['one_service', 'another_service']`, it works directly. If not, use Jinja to produce a list:

```jinja
[{% for label in get_list(result) %}'my_prefix/{{label}}',{% endfor %}]
```

Note the surrounding brackets and the quoted values with commas — this builds a string that looks like a Python list.

Set _Value_ to `To String` and the _New Value_ to `yes`, and you get:

```text
one_service: yes
another_service: yes
```

## Operations for Attribute Values

| Function            | Description                                                              |
| :------------------ | :----------------------------------------------------------------------- |
| To String           | Set the attribute value to a fixed string                                |
| With Split          | Split the value using SEPARATOR:INDEX syntax, e.g. `/:0`                 |
| With Jinja Template | Build the value with Jinja — access all host attributes and {{HOSTNAME}} |

### Split

Provide a pattern as `SEPARATOR:INDEX`. The value is split at the separator, and the item at the given index is used as the new value.

Example: `/:0`

Applied to `127.0.0.1/24`: splits at `/` → `['127.0.0.1', '24']` → index 0 → `127.0.0.1`

## Creating New Attributes

If you specify an attribute name in _Old Attribute Name_ that does not exist on the host, it will be created as a new attribute. All value operations can be used, so you can compose a new attribute from multiple existing ones using Jinja.

## Special Jinja Variables

When using conditions with `regex`, `swith`, `ewith`, and similar types, you may not know in advance which attribute triggered the match. Two special placeholders are available in Jinja value rewrites:

- `{{FIRST_MATCHING_TAG}}` — the name of the attribute that caused the condition to match
- `{{FIRST_MATCHING_VALUE}}` — the value of that attribute

## Hashing a value

Some values cannot be used as a Checkmk label or rule condition: a comma-separated
list, a value with spaces, a service pattern. The `hash` filter turns them into a
short, stable value that can:

```text
{{ roles | hash }}          ->  3ae68845
{{ roles | hash(16) }}      ->  3ae688450e83a1b7
{{ hash_value(roles) }}     ->  3ae68845
```

The same input always gives the same result, on every run and every installation
— it is a sha256 digest, not Python's `hash()`. A list is sorted first, so the
order its entries happen to have does not change the result.

Typical use: create a hashed copy of an attribute so a rule can match on it,
without losing the original.

| Field | Value |
| :---- | :---- |
| Old attribute name | `roles_hash` |
| Overwrite name | *(leave empty)* |
| Overwrite value | With Jinja Template |
| New value | `{{ roles | hash }}` |

This adds `roles_hash` and leaves `roles` untouched. A host without `roles` gets
nothing. `checkmk analyse_rules --apply` writes exactly this rule when it needs a
hashed label.
