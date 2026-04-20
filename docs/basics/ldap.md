# LDAP Login

!!! note "Enterprise feature"
    LDAP login is part of the [Enterprise Edition](../installation/enterprise.md). Without the `cmdbsyncer-enterprise` package and a valid license that includes the `ldap_login` claim, the `LDAP_LOGIN` setting has no effect and the classical login form is used.

LDAP login authenticates users against an existing LDAP or Active Directory server. On successful bind, CMDBsyncer looks up a local user by email and logs that user in. If no local user exists, one is **auto-created** with the email and `cn` from LDAP.

Roles and the `global_admin` flag can be driven from LDAP group membership via `LDAP_ROLE_MAPPING` — see [Role Mapping](#role-mapping) below. When role mapping is configured, LDAP is the source of truth: permissions are recomputed on every login.

## How It Works

Two modes are supported. Pick the one that matches your directory setup:

### Direct-Bind Mode

CMDBsyncer builds the user's DN from a template and binds directly with the submitted password. Fast, no service account required, but only works when every user's DN follows the same pattern.

```python
config = {
    'LDAP_LOGIN': True,
    'LDAP_SERVER': 'ldaps://ldap.example.com',
    'LDAP_USER_DN_TEMPLATE': 'uid={username},ou=people,dc=example,dc=com',
}
```

The placeholder `{username}` expands to the local part of the email (everything before `@`). `{email}` is also available.

### Search-Bind Mode

CMDBsyncer binds first with a **service account**, searches for the user via a filter, then re-binds as the found DN with the submitted password. Use this when user DNs live in different sub-trees, or when your directory is Active Directory.

```python
config = {
    'LDAP_LOGIN': True,
    'LDAP_SERVER': 'ldaps://ad.example.com',
    'LDAP_BIND_USER': 'cn=syncer,ou=service,dc=example,dc=com',
    'LDAP_BIND_PASSWORD': 'the-service-password',
    'LDAP_SEARCH_BASE': 'ou=people,dc=example,dc=com',
    'LDAP_SEARCH_FILTER': '(mail={email})',
}
```

`LDAP_SEARCH_FILTER` supports the placeholders `{email}` and `{username}`. For Active Directory `(userPrincipalName={email})` or `(sAMAccountName={username})` are common choices.

## Configuration Reference

| Name                    | Default            | Description                                                                     |
| :---------------------- | :----------------- | :------------------------------------------------------------------------------ |
| `LDAP_LOGIN`            | `False`            | Master switch. Must be `True` to enable LDAP authentication.                    |
| `LDAP_SERVER`           | `''`               | Server URL, e.g. `ldaps://ldap.example.com` (use `ldaps://` in production).     |
| `LDAP_USER_DN_TEMPLATE` | `''`               | Direct-bind mode. Format string with `{username}` and/or `{email}` placeholder. |
| `LDAP_BIND_USER`        | `''`               | Search-bind mode. DN of a service account used to locate the user.              |
| `LDAP_BIND_PASSWORD`    | `''`               | Password for `LDAP_BIND_USER`.                                                  |
| `LDAP_SEARCH_BASE`      | `''`               | Base DN for the user search (search-bind only).                                 |
| `LDAP_SEARCH_FILTER`    | `'(mail={email})'` | Filter for the user search. Placeholders `{email}` and `{username}`.            |
| `LDAP_REQUIRED_GROUP`   | `''`               | Full DN of a group. If set, bound user must have it in `memberOf`.              |
| `LDAP_AUTO_CREATE`      | `True`             | Auto-create local user record on first successful login.                        |
| `LDAP_NAME_ATTR`        | `'cn'`             | LDAP attribute used for `User.name` on creation.                                |
| `LDAP_ROLE_MAPPING`     | `{}`               | Map group DN → permissions. When set, roles sync from LDAP on every login.      |

## Restricting Login to a Group

To allow only members of a specific group to sign in, set `LDAP_REQUIRED_GROUP` to the full DN of that group:

```python
config = {
    'LDAP_REQUIRED_GROUP': 'cn=syncer-users,ou=groups,dc=example,dc=com',
}
```

CMDBsyncer reads the `memberOf` attribute of the bound user and checks — case-insensitively and DN-normalized — whether the required group is present. Users whose `memberOf` does not contain the group are rejected with `"Wrong Password"` (the generic message prevents enumeration).

!!! tip "memberOf on OpenLDAP"
    `memberOf` is automatic in Active Directory. On OpenLDAP you have to enable the `memberof` overlay (`olcModuleLoad: memberof.la`) so this attribute is populated.

## User Provisioning

After a successful bind CMDBsyncer looks up the local user by email (`disabled__ne=True`):

- Existing, non-disabled user → login succeeds.
- No matching user and `LDAP_AUTO_CREATE = True` (default) → a new user record is created with `email` from the login form and `name` from the LDAP attribute `LDAP_NAME_ATTR` (default `cn`). Falls back to the email if the attribute is absent.
- No matching user and `LDAP_AUTO_CREATE = False` → login is rejected.

Disabled users are never auto-logged-in, even if the bind succeeds.

## Role Mapping

To drive roles and admin rights from LDAP groups, set `LDAP_ROLE_MAPPING`. Keys are full group DNs, values are dictionaries of permissions to grant:

```python
config = {
    'LDAP_ROLE_MAPPING': {
        'cn=admins,ou=groups,dc=example,dc=com': {
            'global_admin': True,
        },
        'cn=operators,ou=groups,dc=example,dc=com': {
            'roles': ['host', 'objects', 'log'],
        },
        'cn=api-clients,ou=groups,dc=example,dc=com': {
            'api_roles': ['all'],
        },
    },
}
```

Supported permission keys per group:

| Key            | Type         | Effect                                                      |
| :------------- | :----------- | :---------------------------------------------------------- |
| `global_admin` | bool         | Grants the global admin flag.                               |
| `roles`        | list of str  | Web UI roles (see `roles` in `application/models/user.py`). |
| `api_roles`    | list of str  | REST API roles (`all`, `ansible`, `objects`, `syncer`).     |

### Multiple Group Memberships

Group DNs are the outer dict keys and must be unique (standard Python dict semantics). When a user belongs to **several** mapped groups, CMDBsyncer takes the **union** of all matched permissions. You do not — and cannot — repeat the `roles` key within a single group's dict; just list one group per entry and let the union resolve the rest.

```python
config = {
    'LDAP_ROLE_MAPPING': {
        'cn=ops,ou=groups,dc=example,dc=com': {
            'roles': ['host', 'log'],
        },
        'cn=network,ou=groups,dc=example,dc=com': {
            'roles': ['host', 'objects'],
        },
        'cn=api-users,ou=groups,dc=example,dc=com': {
            'api_roles': ['objects'],
        },
        'cn=admins,ou=groups,dc=example,dc=com': {
            'global_admin': True,
            'roles': ['user'],
            'api_roles': ['all'],
        },
    },
}
```

Example resolutions for this mapping:

| `memberOf` contains               | Resulting permissions                                                        |
| :-------------------------------- | :--------------------------------------------------------------------------- |
| `cn=ops`                          | `roles=['host', 'log']`                                                      |
| `cn=ops` + `cn=network`           | `roles=['host', 'log', 'objects']` (duplicates removed)                      |
| `cn=network` + `cn=api-users`     | `roles=['host', 'objects']`, `api_roles=['objects']`                         |
| `cn=admins` + `cn=ops`            | `global_admin=True`, `roles=['host', 'log', 'user']`, `api_roles=['all']`    |
| No matched group                  | `roles=[]`, `api_roles=[]`, `global_admin=False`                             |

DNs are compared case-insensitively and normalized via `ldap3.utils.dn.safe_dn`, so whitespace or case differences between the LDAP server's response and the mapping keys do not break the match.

!!! warning "LDAP overwrites manual changes"
    While `LDAP_ROLE_MAPPING` is non-empty, roles and `global_admin` are **replaced** at each login — grant additional permissions through LDAP group membership, not via the web UI, or they get reverted on the next login. Leave `LDAP_ROLE_MAPPING = {}` (the default) to disable role sync entirely; new users are then created without roles and you assign them manually.

## Fallback to Local Password

If the LDAP bind fails (wrong password, user not in directory, server unreachable) and a local user with the same email exists with a local password set, that password is tried next. You can therefore mix LDAP users and local service accounts without additional configuration.

Connection errors (server unreachable, bad TLS, misconfigured service account) are surfaced to the user as `LDAP Error: <reason>` and the login is aborted — the flow does not fall through to the local password in that case, to avoid silently masking misconfiguration.

## Security Notes

!!! warning "Always use LDAPS"
    Plain `ldap://` sends the password in cleartext over the network. In production always use `ldaps://` (LDAP over TLS) or `ldap://` combined with StartTLS via a properly configured server.

!!! note "Service-account password"
    The `LDAP_BIND_PASSWORD` sits in `local_config.py` on disk. Restrict file permissions accordingly (`chmod 640`, owner = the user running CMDBsyncer). Prefer a read-only service account that can only search, never modify.

## Troubleshooting

### `LDAP Error: LDAP_SERVER not configured`

`LDAP_LOGIN` is `True` but `LDAP_SERVER` is empty. Set both.

### `LDAP Error: LDAP_USER_DN_TEMPLATE or LDAP_BIND_USER must be configured`

Neither direct-bind nor search-bind mode is fully configured. Set either `LDAP_USER_DN_TEMPLATE` **or** `LDAP_BIND_USER` + `LDAP_BIND_PASSWORD` + `LDAP_SEARCH_BASE`.

### Login says `Wrong Password` even though credentials are correct

Check in order:

1. The user's email in CMDBsyncer **exactly** matches the one used to log in (case is normalized to lowercase on submission).
1. A local user record exists and is not disabled.
1. If `LDAP_REQUIRED_GROUP` is set, the user is actually a member of that group (verify with `ldapsearch -b <user_dn> memberOf`).

### LDAP server is reachable but bind always fails

Test the credentials from the same host with `ldapsearch` before blaming CMDBsyncer:

```bash
ldapsearch -H ldaps://ldap.example.com -x \
    -D 'uid=alice,ou=people,dc=example,dc=com' -W
```
