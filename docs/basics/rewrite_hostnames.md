# Rewrite Hostnames

Hostname rewrites must happen at import time. Most import plugins support this via a Jinja2 template configured on the account (available since version 3.4).

To set it up, open the account used for your import. A field named `rewrite_hostname` is available in the account's custom attributes section.

## Example

If a host has an attribute `dns`, a rewrite that appends the DNS suffix would look like this:

```jinja
{{HOSTNAME}}.{{dns}}
```

`{{HOSTNAME}}` is always the original hostname from the source. Any other host attribute can be used by name.

!!! warning
    If you change the rewrite template later, the previously imported hosts — with their old hostnames — will remain in the database. To the Syncer, a rewritten hostname is a completely new object. Remove the old hosts manually after changing the template.
