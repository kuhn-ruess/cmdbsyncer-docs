# LDAP Connections
<span class="since">Since 4.5</span>

Checkmk lets its users log in with their directory account through an LDAP
connection. The Syncer maintains these connections for you: you describe the
connection once and the export creates it on every Checkmk instance, keeps it up
to date and removes it again when asked.

Go to: _Modules → Checkmk → Manage LDAP Connections_

## Server and Credentials

The connection does not carry its own server or password. It points to an
account of type **LDAP** (_Accounts_), the same kind the LDAP import uses. That
way the bind password lives in one place only, and a changed password reaches
Checkmk with the next export.

| Account Field | Used as                                                                                                               |
| :------------ | :-------------------------------------------------------------------------------------------------------------------- |
| Address       | `ldaps://dc1.example.com` — `ldaps://` switches SSL on, a port in the address is used as TCP port (default 389 / 636) |
| Username      | Bind DN, e.g. `CN=checkmk-bind,OU=service,DC=example,DC=com`. Empty binds anonymously                                 |
| Password      | Password of the bind DN, also from an external secret store if the account uses one                                   |

!!! note "Password in Checkmk"
    By default the bind password is written into the connection in Checkmk. To keep
    it in Checkmk's password store instead, create a global entry in the
    [Secret Store](../basics/secret_store.md), set its name as **Bind Secret** and
    run `export_passwords` for the account before the LDAP export.

## Parameters

| Option                          | Description                                                                                                                                     |
| :------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------- |
| Connection ID                   | ID of the connection in Checkmk, e.g. `ldap_ad`. The export finds the connection by this ID                                                     |
| Description / Comment           | Shown in Checkmk's list of user connections                                                                                                     |
| LDAP Account                    | Syncer account of type LDAP. Server, port, SSL, bind DN and password are taken from it                                                          |
| Directory Type                  | Active Directory, OpenLDAP or 389 Directory Server                                                                                              |
| Failover Servers                | Servers Checkmk tries when the account's server is not reachable                                                                                |
| Bind Secret                     | Optional: name of a global Secret Store entry. Checkmk then binds with that entry out of its own password store instead of the account password |
| Connection Suffix               | Appended to the user IDs (`user@suffix`), needed when two connections may know the same user name                                               |
| User Base DN                    | All users that may log in are below this DN                                                                                                     |
| User Search Filter              | Optional LDAP filter for the users, e.g. `(&(objectclass=user)(objectcategory=person))`                                                         |
| Filter Group                    | Optional DN of a group: only its members may log in                                                                                             |
| User ID Attribute               | Attribute holding the login name. Empty uses Checkmk's default (`sAMAccountName` / `uid`)                                                       |
| Lower Case User IDs             | Convert the login names to lower case                                                                                                           |
| Create Users                    | Create the Checkmk user on the first login or already during the sync                                                                           |
| Group Base DN                   | All groups used for contact groups and roles are below this DN                                                                                  |
| Group Search Filter             | Optional LDAP filter for the groups                                                                                                             |
| Member Attribute                | Attribute listing the members of a group. Empty uses Checkmk's default                                                                          |
| Alias / Email / Pager Attribute | LDAP attribute synced into the user's alias, mail address or pager. Empty leaves it off                                                         |
| Sync Contact Groups             | Members of an LDAP group get the Checkmk contact group of the same name                                                                         |
| Groups to Roles                 | Checkmk role ID (`admin`, `user`, `guest`, ...) and the DN of the group whose members get it. The DN must be below the Group Base DN            |
| Handle Nested Groups            | Members of nested groups also get the contact groups and roles                                                                                  |
| Sync Interval (Minutes)         | How often Checkmk syncs the users from the directory                                                                                            |
| Deactivated                     | The connection stays in Checkmk, but is switched off                                                                                            |
| Remove if Found                 | The next export deletes the connection from Checkmk                                                                                             |

The Syncer manages exactly these settings. All others (timeouts, page size,
further sync plug-ins) stay at Checkmk's defaults; changing one of them by hand in
Checkmk is not undone by the export.

## Export

The export reads each connection from Checkmk and only writes when one of the
settings above differs, so a run without changes leaves Checkmk untouched.
Changes are not activated — run `activate_changes` afterwards or schedule both in
a cron group (_Checkmk: Export LDAP Connections_).

```bash
./cmdbsyncer checkmk export_ldap_connections ACCOUNTNAME
./cmdbsyncer checkmk activate_changes ACCOUNTNAME
```

Requires Checkmk 2.3 or newer, the first version with LDAP connections in its
REST API.
