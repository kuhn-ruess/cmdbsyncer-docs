# LDAP

The Syncer can import and inventorize objects from LDAP — Active Directory, OpenLDAP, or any compatible directory service.

Create an [Account](../basics/accounts.md) of type _LDAP_ and configure the fields below. After saving, the account-specific fields appear automatically.

| Field            | Description                                                                |
| ---------------- | -------------------------------------------------------------------------- |
| `address`        | LDAP server URL, must start with `ldap://` or `ldaps://`                   |
| `username`       | Bind user DN                                                               |
| `password`       | Bind password                                                              |
| `base_dn`        | Search base, e.g. `DC=example,DC=com`                                      |
| `search_filter`  | LDAP filter, e.g. `(&(objectCategory=Person)(objectClass=user))`           |
| `attributes`     | Comma-separated list of attributes to fetch, e.g. `cn,mail,sAMAccountName` |
| `hostname_field` | Attribute to use as the host identifier                                    |
| `encoding`       | `utf-8` or `ascii`, depending on your LDAP server                          |

!!! tip
    If you are importing objects that are not hosts (contacts, groups, etc.), enable _Is Object_ on the account and select an appropriate Object Type. This makes it easier to filter them in rules and exports.

## Import vs. Inventorize

The LDAP plugin provides two commands with different behavior:

- **import_objects** — creates or updates hosts in the syncer database. The account becomes the master for those hosts.
- **inventorize_objects** — adds LDAP attributes as inventory data to hosts that already exist in the database. The hosts are not created or owned by this account.

## Running from the CLI

```bash
./cmdbsyncer ldap import_objects my-ldap-account
./cmdbsyncer ldap inventorize_objects my-ldap-account
```

Add `--debug` to see the LDAP query details and full attribute output:

```bash
./cmdbsyncer ldap import_objects my-ldap-account --debug
```

## Trying Out Queries and Search Filters

`debug_query` runs the query of an account and prints what comes back, without writing anything to the database. Every object is shown with the labels the import would create, objects without the `hostname_field` are marked as ignored, and a broken filter is reported as an LDAP error instead of a traceback.

```bash
./cmdbsyncer ldap debug_query my-ldap-account
```

The account settings can be overwritten for a single run, so a new filter can be tested before it is saved:

| Option                  | Description                                                        |
| ----------------------- | ------------------------------------------------------------------ |
| `-b`, `--base-dn`       | Search base to use instead of the one on the account               |
| `-f`, `--search-filter` | LDAP filter to use instead of the one on the account               |
| `-a`, `--attributes`    | Attributes to request, an empty string requests all of them        |
| `-l`, `--limit`         | Stop after this many objects (default 10, `0` prints all of them)  |

```bash
./cmdbsyncer ldap debug_query my-ldap-account -f "(&(objectClass=computer)(operatingSystem=*Server*))" -a "" -l 3
```

### Which Attributes Does a Result Have?

With `-A` / `--list-attributes` the command does not print the objects, but the attributes they carry: in how many of the found objects each attribute exists, whether it has more than one value (only the first one is imported), and an example value. The last line is the attribute list ready to be pasted into the `attributes` field of the account.

```bash
./cmdbsyncer ldap debug_query my-ldap-account -A
```

This asks the server for all attributes, so `attributes` on the account is ignored for that run. Operational attributes — for example `memberOf` on OpenLDAP — are not part of "all" and have to be requested by name, or with `-a "*,+"` if the directory supports it:

```bash
./cmdbsyncer ldap debug_query my-ldap-account -A -a "*,+"
```

## Searching in the Web Interface

_Modules_ → _LDAP_ → _Search Directory_ does the same thing from the browser: it runs one search against an account and shows the found objects with the labels the import would create. It only reads — neither the directory nor the objects of the Syncer are changed.

| Search for                     | What it does                                                                                       |
| ------------------------------ | -------------------------------------------------------------------------------------------------- |
| Hostname — with or without domain | Matches the `hostname_field` exactly and with any domain behind it: `srv01` also finds `srv01.example.com` |
| Hostname contains              | The `hostname_field` contains the term anywhere                                                     |
| Attribute contains             | The given attribute contains the term, e.g. `description`                                           |
| Own LDAP filter                | The term is used as the LDAP filter, e.g. `(&(objectClass=computer)(cn=srv*))`                      |

Base DN, the attributes to request and the encoding can be overwritten for a single search, and the search filter of the account can be switched off, so a filter can be tried out before it is saved on the account. Attributes are left empty by default, which asks the server for every attribute of the found objects.

Values that cannot be read with the encoding of the account are shown with a `�` instead of the character, together with a hint — the usual cause is `ascii` on an account whose directory answers in `utf-8`. Searching again with `utf-8` in the _Encoding_ field shows whether that is the right value before it is saved on the account; the import itself stops with a decoding error as long as the encoding is wrong.

Each result shows whether the import would create a host out of it — objects without the `hostname_field` are marked as skipped and list all of their attributes instead, so it is visible what is missing.

Users need the _LDAP_ right to open the page.

## Setting Up Automation

For production use, add the command as a [Cron job](../basics/cron.md).
