# Generate Checkmk Users

<span class="since">Since 4.4</span>

Your hosts usually already know who is responsible for them: an attribute holds the
name of an LDAP group, imported from the directory or written by a rule. This feature
turns those group names into Checkmk users — one user per group — and fills them with
the data the group object itself carries in the directory, such as the shared mailbox
of the team.

Go to: _Modules → Checkmk → Generate Checkmk Users_

The result is an entry in [Manage Checkmk Users](users.md), so the export to Checkmk
stays the same command as for a user you typed in by hand.

## How a Group becomes a User

1. The rule collects the group names out of your host attributes, for example
   `ldap_group: grp-dba`.
2. **Rewrite Group Name** may shape that value first, for hosts that carry the name
   differently than the directory does.
3. It searches those groups in the directory, below the base DN and with the filter
   the rule configures — all names of a rule go into **one** query.
4. Every attribute of the found group object becomes a Jinja variable.
5. User ID, full name, mail address and pager are rendered from those variables and
   written into the Checkmk user list.

## Rewriting the Group Name

Hosts do not always carry the group the way the directory spells it. **Rewrite Group
Name** runs before the search and `{{name}}` is the value the attribute delivered:

| Hosts carry       | Rewrite                         | Searched for |
| :---------------- | :------------------------------ | :----------- |
| `grp-dba`         | `{{name\|replace("grp-", "")}}` | `dba`        |
| `dba@example.com` | `{{name.split("@")[0]}}`        | `dba`        |
| `dba`             | `CN-{{name}}`                   | `CN-dba`     |

A rewrite that renders to nothing skips that value: no group is searched and no user
is created for it. That is the way to drop values an attribute carries that are not
groups at all — an empty name would otherwise be searched as whatever the group filter
alone matches. `--debug` names every value that was dropped this way.

The LDAP account contributes the address and the credentials, nothing else. Where the
groups are and how they are read belongs to the rule, so one account can serve several
rules that look into different parts of the directory.

## Rule Parameters

| Option               | Description                                                                                                      |
| :------------------- | :--------------------------------------------------------------------------------------------------------------- |
| Foreach Type         | Where the group names sit: by attribute name, by attribute value, or split out of a comma separated list         |
| Foreach              | Name of that attribute. Use `*` at the end as a wildcard (e.g. `ldap_group*`)                                    |
| Rewrite Group Name   | Jinja, optional. Shapes the value into the name the directory uses. Empty result skips that value                |
| LDAP Account         | The account used to reach the directory. It supplies address and credentials only                                |
| Group Base DN        | Subtree the groups live in, e.g. `ou=groups,dc=example,dc=com`. Empty falls back to the account's base DN        |
| Group Search Filter  | Filter picking the group objects, e.g. `(objectClass=group)`. The account's own search filter is never used here |
| Group Name Attribute | Attribute the host attribute values are matched against. `cn` in most directories                                |
| Attributes to Read   | Comma separated. Empty reads every attribute the group has                                                       |
| Checkmk User ID      | Jinja. `{{name}}` is the group name                                                                              |
| Full Name            | Jinja. What Checkmk shows in its user list                                                                       |
| Mail Address         | Jinja, usually `{{mail}}`                                                                                        |
| Pager Address        | Jinja, for a second contact route                                                                                |
| Checkmk Roles        | Roles every generated user is given                                                                              |
| Contact Groups       | Contact groups every generated user is put into                                                                  |
| No Login             | Generated users are notification contacts, not people logging in                                                 |

Every Jinja field sees the same variables: `{{name}}` for the group name, plus every
attribute the group carries — `{{mail}}`, `{{description}}`, `{{dn}}` and so on.
They support all custom [Syncer Jinja Functions](../advanced/jinja_functions.md).

!!! note "The group name wins"
    If a group happens to carry an attribute called `name`, `{{name}}` still resolves
    to the group name the host attribute delivered, not to that attribute.

## Example

Your hosts carry `ldap_group` with values like `grp-dba` and `grp-linux`, and each of
those groups has a shared mailbox in its `mail` attribute.

1. Set **Foreach Type** to _Foreach Attribute Name_
2. Set **Foreach** to `ldap_group`
3. Pick your **LDAP Account**
4. Set **Group Base DN** to `ou=groups,dc=example,dc=com`
5. Set **Group Search Filter** to `(objectClass=group)`
6. Leave **Checkmk User ID** at `{{name}}` and **Mail Address** at `{{mail}}`
7. Set **Contact Groups** to the groups these contacts belong to

This creates the Checkmk users `grp-dba` and `grp-linux`, each with the mail address
of its group.

## Command Line

```bash
./cmdbsyncer checkmk generate_users
./cmdbsyncer checkmk export_users ACCOUNTNAME
```

The first command fills the user list, the second ships it to Checkmk. As a cron job
the two steps are _Checkmk: Generate Users_ and _Checkmk: Export Users_.

## When no Group is found

`--debug` prints what the lookup really asked the directory — base DN, group search
filter, name attribute, the finished LDAP filter and the attributes requested — and
afterwards the group names the directory did not return.

```bash
./cmdbsyncer checkmk generate_users --debug
```

`--search-filter` overwrites the group search filter of every rule for that one run,
so a filter can be tried out before it goes into a rule.

```bash
./cmdbsyncer checkmk generate_users --debug --search-filter '(objectClass=posixGroup)'
```

!!! warning "The run still writes"
    Both options only change the lookup, they do not stop the generation. A filter
    matching the wrong objects writes the wrong user data.

The usual reasons a group is not found:

- The **Group Name Attribute** does not hold what the host attribute delivers. It is
  `cn` in most directories and `sAMAccountName` in some Active Directories.
- The **Group Base DN** points at the host subtree instead of the group subtree.
- The **Group Search Filter** names a class the groups do not have. Active Directory
  uses `(objectClass=group)`, OpenLDAP usually `(objectClass=posixGroup)` or
  `(objectClass=groupOfNames)`.
- The group really is spelled differently in the directory. _Modules → LDAP → Search
  Directory_ with the mode **Group by name** shows how it is stored.

## What a Group carries

To find out which attributes you can use, go to _Modules → LDAP → Search Directory_,
pick the mode **Group by name**, enter the base DN and the group's name, and leave
**Attributes** empty. The result lists everything the group has — those are exactly
the variables available in the rule.

## Users are updated, never removed

- A user that a former run created is updated when the group data changes.
- A user someone created by hand is never touched — the generation only owns the
  entries it made itself.
- A group that disappears leaves its user standing, so nobody silently loses their
  notifications. Remove such a user in _Manage Checkmk Users_.
- A Jinja field that renders to nothing leaves the value as it is instead of emptying
  it, so a group missing an attribute does not wipe what is already there.
- If the directory cannot be reached, the affected rules are skipped instead of
  creating users without their data.
