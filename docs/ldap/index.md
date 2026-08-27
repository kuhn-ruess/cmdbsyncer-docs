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

## Setting Up Automation

For production use, add the command as a [Cron job](../basics/cron.md).
