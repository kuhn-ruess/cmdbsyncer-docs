# Secret Store
<span class="since">Since 4.5</span>

The Secret Store keeps the passwords, tokens and certificates the Syncer needs,
encrypted, in one place for every module. An entry is either **global** or
**bound to a host**, and rules read it with a Jinja function instead of carrying
the secret themselves.

You find it under **Modules > Secret Store** (at the bottom of the Modules menu,
next to the [Lookup Tables](lookup_tables.md)).

!!! note "Formerly the Checkmk Password Store"
    Up to version 4.4 this was the Checkmk **Password Store** (_Modules > Checkmk >
    Manage Password Store_). It is the same data: every existing entry keeps its
    name, its value and its Checkmk ident `cmdbsyncer_<id>`, nothing is migrated.
    `{{ cmk_password("name") }}` and `checkmk export_passwords` work as before,
    and rule exports made with an older version still import (the rule type is
    still called `cmk_passwords`). The Checkmk side of the store is described in
    [Password Store](../checkmk/password_store.md).

## How values are stored

Values are encrypted in the database with the `CRYPTOGRAPHY_KEY` from your
`local_config.py`. If you change this key, the stored values have to be entered
again. The list and the host overview never show a value; showing one needs a
role of its own (see [Access](#access)).

## An entry

| Field | Description |
| :---- | :---------- |
| Name | Unique name of the entry. A global entry is reached by this name. For a host-bound entry it is set to `<hostname>:<key>` automatically |
| Documentation | Free text for your own notes |
| Enabled | Only enabled entries are exported to Checkmk |
| Kind | **Password**, **Token** or **Certificate** |
| Value | The secret. Leave it empty when editing to keep the stored value |
| Bound to host | Empty for a global entry. With a hostname the entry belongs to that host |
| Key | Name of the secret on the host, e.g. `api_token`. Required for a host-bound entry |
| Export to Checkmk | Write the entry into the Checkmk password store (see below) |
| Title, Comment, Documentation URL, Owner, Shared | How the entry is described in the Checkmk password store |

### Global entries

A global entry belongs to no host. Rules reach it by its **Name**, with
`{{ cmk_password("name") }}` or `{{ secret('name') }}`.

### Host-bound entries

A host-bound entry belongs to one host and is found by host and **Key**. Every
host can have its own `api_token`, and a rule rendered for a host gets the entry
of exactly that host. The usual way to create them is the
[host import](../cmdb/index.md#import-csv-yaml-and-manual-add), which can send
chosen columns into the Secret Store instead of turning them into labels.

The host overview (the detail page of a host) has a **Secrets** row listing the
entries bound to the host: key, kind, the reference to use in rules, the value
masked as `******`, a link to the entry and, with the matching role, a link to
show the value.

### Orphaned entries

When a host is archived or deleted, its entries are **not** removed. They are
flagged **orphaned** in the list (there is a filter for it) and are no longer
found by `secret()`. To reuse such an entry, edit it and put another hostname
into **Bound to host**: the entry is bound to that host and the flag is cleared.
When the archived host is restored, the flag goes away by itself.

### Certificates

An entry of the kind **Certificate** is not exported to Checkmk, because Checkmk
cannot create one in its password store over the REST API. Use the eye icon in
the list (**Show value**) to display it and copy it by hand. A value containing
a PEM block (`BEGIN CERTIFICATE`) that comes in through the host import is
stored as a certificate automatically.

## Using entries in rules

| Function | Result |
| :------- | :----- |
| `{{ secret('key') }}` | The Checkmk password store ident (`cmdbsyncer_<id>`) of the entry bound to the current host under `key`, or of the global entry named `key` if the host has none |
| `{{ secret_value('key') }}` | The plaintext value of the same entry |
| `{{ cmk_password("name") }}` | The Checkmk ident of the **global** entry `name`. Host-bound entries are never resolved by name |

The host always comes from the host the rule is rendered for. A template cannot
switch to another host's secret, not even by setting `HOSTNAME` itself.

A Checkmk Setup Rule that needs a per host token, e.g. in the value of a special
agent:

```python
{
    'url': 'https://{{ api }}',
    'token': ('cmk_postprocessed', 'stored_password', ('{{ secret("api_token") }}', '')),
}
```

`secret()` only gives the ident, so the token itself has to be in the Checkmk
password store: run `./cmdbsyncer checkmk export_passwords <account>` first, as
for global entries. See [Passwords in Setup Rules](../checkmk/passwords_in_rules.md).

`secret_value()` puts the plaintext into the result, use it only where a target
really needs the value itself. Inside the web interface and the API (previews,
host debug) the value is shown as `******` unless the user may show values of
that entry. Exports run from the command line or cron get the real value.

A key that has neither a host-bound nor a global entry is logged as an error.
`secret()` then gives the placeholder `cmdbsyncer_missing_<key>`, which Checkmk
rejects, `secret_value()` gives an empty string.

## Export to Checkmk

```bash
./cmdbsyncer checkmk export_passwords ACCOUNTNAME
```

writes every enabled entry with **Export to Checkmk** ticked into the Checkmk
password store of that account, global and host-bound entries alike.
Certificates are left out. Details in [Password Store](../checkmk/password_store.md).

## Access

Two roles under **Settings > User**:

| Role | Grants |
| :--- | :----- |
| Secret Store | List, create, edit and bind entries. The Checkmk role still opens the store as well, as it did for the Password Store |
| Secret Store: show plaintext values | Show the value of an entry (the eye icon in the list and on the host overview) |

A user [restricted to accounts or templates](../installation/authentication.md#restricting-a-user-to-accounts)
only reaches entries bound to hosts inside that limit, global admins included.
Such a user:

- sees, edits, switches, reveals and binds only entries of their own hosts,
- cannot create or see global entries,
- can only bind entries to hosts they can see,
- cannot export or import the Secret Store through the
  [rule export/import](rule_import_export.md), the REST API or the MCP server,
- only stores secrets for their own hosts through the host import.

Showing a value is written to the log with the user and the entry.
