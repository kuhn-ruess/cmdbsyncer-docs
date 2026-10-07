# Rewrite Hostnames

Hostname rewrites must happen at import time. Most import plugins support this via a Jinja2 template configured on the account (available since version 3.4).

To set it up, open the account used for your import. A field named `rewrite_hostname` is available in the account's custom attributes section.

## Example

If a host has an attribute `dns`, a rewrite that appends the DNS suffix would look like this:

```jinja
{{HOSTNAME}}.{{dns}}
```

`{{HOSTNAME}}` is always the original hostname from the source. Any other host attribute can be used by name.

## One record, several hosts

<span class="since">Since 4.4</span>

A template that renders a **list** imports one host per entry. Each of them gets all attributes of the record, belongs to the importing account and is marked as seen on every run, so an entry that disappears from the list ages out through the normal [maintenance](maintenance.md) like any host that is no longer imported.

Example: every server record of a site (`SITE7-SRV01`) should also bring the router and the switch of that site:

```jinja
{{ [HOSTNAME, HOSTNAME | replace('SRV01', 'RTR01'), HOSTNAME | replace('SRV01', 'SW01')] }}
```

This creates `SITE7-SRV01`, `SITE7-RTR01` and `SITE7-SW01`. All three carry the same attributes, so give the devices their own settings (the IP address, for example) with a hostname condition in your rules, such as hostname ends with `RTR01`.

The rendered result counts as a list only when it is a list literal: square brackets around quoted entries, which is what Jinja writes for a list. A loop works too:

```jinja
[{% for device in devices.split(',') %}'{{ HOSTNAME }}-{{ device }}',{% endfor %}]
```

* A result without the brackets is one hostname, exactly as before. A comma alone never splits a name.
* Empty entries are skipped, an entry that occurs twice is imported once. An empty list imports nothing for that record.
* A host another master account owns is left alone, like with a single name.
* The split only applies to the rendered template. A hostname that arrives from the source as `['a', 'b']` without a rewrite stays one name.

Every importer applies `rewrite_hostname` the same way, and inventorize runs land on the same hosts. Importers whose account does not offer the field yet apply it too when you add a custom field named `rewrite_hostname`.

!!! warning
    If you change the rewrite template later, the previously imported hosts — with their old hostnames — will remain in the database. To the Syncer, a rewritten hostname is a completely new object. Remove the old hosts manually after changing the template.
