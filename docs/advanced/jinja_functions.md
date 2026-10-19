# Custom Jinja Functions

The Syncer extends Jinja with the following custom functions and helpers.
They are available in every Jinja-enabled field throughout the UI (rewrite rules, export rules, conditions, etc.).

In the forms of Custom Attributes, Rewrite Attributes and (since 4.5) Checkmk Setup Rules, the **Jinja help** button below a template field lists these functions, the variables of the rule and your [Lookup Tables](../basics/lookup_tables.md). A click on an entry inserts it at the cursor. In a Setup Rule it sits below the Value Template and the Folder and also lists `{{ HOST_FOLDER }}` (see [Checkmk Setup Rules](../checkmk/rules_management.md#the-folder-of-the-host-host_folder)).

---

## `{{ACCOUNT:name:attribute}}` Placeholder

Since version 3.12.2 the `{{ACCOUNT:...}}` placeholder is globally available in every Jinja field.
Use it to reference any field from a configured account without hardcoding credentials:

```jinja
{{ACCOUNT:my_account:password}}
{{ACCOUNT:my_account:address}}
```

Syntax: `ACCOUNT:ACCOUNTNAME:FIELDNAME`

---

## `lookup(table, key, column=None, default='')`

Reads a value from a [Lookup Table](../basics/lookup_tables.md): the line whose first column is `key`, and of it the second column, or the column named by `column`.

```jinja
{{ lookup('datacenters', location) }}
{{ lookup('datacenters', location, 'owner', default='unknown') }}
```

An unknown table, key or column, or an empty cell, gives `default`.

---

## `secret(key)`, `secret_value(key)` and `cmk_password(name)`
<span class="since">Since 4.5</span>

Read an entry of the [Secret Store](../basics/secret_store.md):

```jinja
{{ secret('api_token') }}        {# Checkmk ident, e.g. cmdbsyncer_<id> #}
{{ secret_value('api_token') }}  {# the plaintext value #}
{{ cmk_password('my-api') }}     {# Checkmk ident of a global entry #}
```

`secret()` and `secret_value()` take the entry bound to the host the template is rendered for under that key, and fall back to the global entry of that name. `cmk_password()` only resolves global entries. Inside the web interface and the API `secret_value()` shows `******` to users who may not show that entry. Details in [Secret Store](../basics/secret_store.md#using-entries-in-rules).

---

## `merge_list_of_dicts(input_list)`

Merges a list of single-key dicts into one flat dict. Useful when attributes arrive as a list of `{key: value}` objects.

```jinja
{# input: [{"site": "dc1"}, {"room": "42"}, {"level": ""}] #}
{{ merge_list_of_dicts(location)['room'] }}
{# result: "42" #}
```

Empty values are dropped from the result. If the input is a string representation of a list, it is parsed automatically.

---

## `get_list(input_list)`

Converts an attribute value into a proper Python list. Handles strings, comma-separated values, and string representations of lists.

```jinja
{% for item in get_list(tags) %}
  {{ item }}
{% endfor %}
```

Useful when an attribute may come in as `"a,b,c"` or `"['a', 'b', 'c']"` depending on the source. See also [Host Tags](../checkmk/create_hosttags.md).

---

## `eval(string, default=None)`

Parses a string as a Python literal (via `ast.literal_eval`). Returns the parsed object, or `default` if parsing fails.
If the input is already not a string, it is returned as-is.

```jinja
{# input: "['tag1', 'tag2']" #}
{% for tag in eval(raw_tags) %}{{ tag }}{% endfor %}
```

---

## `defined(string, default="")`

Returns the value if it is a non-empty, non-false string — otherwise returns `default`.
Treats `"false"` and `"none"` (case-insensitive) as falsy.

```jinja
{{ defined(optional_field, "unknown") }}
```

Useful to provide fallback values for optional attributes that may be missing or set to `"None"`.

---

## `cmk_cleanup_tag_id(value)`

Cleans a string so it can be used as a Checkmk Host Tag ID. Replaces invalid characters with underscores.

```jinja
{{ cmk_cleanup_tag_id(location) }}
{# "Server Room / A-1" → "Server_Room___A_1" #}
```

---

## `cmk_cleanup_hostname(value)`

Cleans a string so it can be used as a valid Checkmk hostname. Replaces or removes characters that Checkmk does not accept in hostnames.

```jinja
{{ cmk_cleanup_hostname(raw_name) }}
```

---

## `get_ip_network(ip_string)`

Converts an IP address with a subnet mask into CIDR network notation (host bits zeroed out).

```jinja
{{ get_ip_network("192.168.2.55/255.255.255.0") }}
{# result: "192.168.2.0/255.255.255.0" #}
```

---

## `get_ip_interface(ip_string)` / `get_ip4_interface(ip_string)`

Converts an IP address with a subnet mask into prefix-length notation using Python's `ipaddress.ip_interface()`.
Both names refer to the same function.

```jinja
{{ get_ip_interface("192.168.2.55/255.255.255.0") }}
{# result: "192.168.2.55/24" #}
```

---

## `datetime`

The Python `datetime` module is available directly in Jinja templates.

```jinja
{{ datetime.datetime.now().strftime("%Y-%m-%d") }}
```

Useful for adding timestamps to attributes or for date-based conditions.
See [Custom Attributes](../basics/custom_attributes.md) for an example that flags hosts which have not been seen by an import for a given number of days.
