# Custom Jinja Functions the Syncer Offers

## {{ACCOUNT:name:attribute}} Placeholder

Since Version 3.12.2, the `{{ACCOUNT:name:attribute}}` placeholder is globally available in every Jinja field throughout the Syncer — not just in specific modules.

Use it to reference any field from a configured account:

```
{{ACCOUNT:my_account:password}}
{{ACCOUNT:my_account:address}}
```

The syntax is `ACCOUNT:ACCOUNTNAME:FIELDNAME`. This allows you to keep credentials centrally in accounts and reference them from rules, rewrites, or any other Jinja-enabled field.

## merge_list_of_dicts()

If you have, for example in your attributes, a list of dictionaries like this:

```
location = [{"site":""},{"section":""},{"level":""},{"room":""},{"description":""},{"note":""}]
```


Then you can use this Jinja Syntax to pick given values in the rewrite

```
{{ merge_list_of_dicts(location)['room'] }}
```


## get_list()

This helper converts an attribute or a given list into a Python list, which is used in some of the Syncer's functions. See [Host Tags](../checkmk/create_hosttags.md) for an example.

## cmk_cleanup_tag_id()

Cleans a string so that it can serve as a Checkmk Host Tag ID. Invalid characters are replaced by underscores.

## get_ip4_network()

Access to a Python function from the `ipaddress` module. When called, `ipaddress.ip_interface()` is invoked.
