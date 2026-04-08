# Custom Jinja Functions

The Syncer extends Jinja with the following custom functions and helpers.
They are available in every Jinja-enabled field throughout the UI (rewrite rules, export rules, conditions, etc.).

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
