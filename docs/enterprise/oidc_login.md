# OIDC Login

Requires the [Enterprise Edition](index.md).

## What it does

Native OpenID Connect (OIDC) client built into CMDBsyncer. Lets
users sign in directly against their corporate identity provider —
Azure AD / Entra ID, Okta, Keycloak, Google Workspace, Auth0, or
any OIDC-compliant IdP — **without** running `mod_auth_openidc` or
`mod_auth_mellon` on a reverse proxy in front.

Complements the two existing Enterprise auth features:

| Feature                 | When to use                                                                   |
| ----------------------- | ----------------------------------------------------------------------------- |
| [Remote User SSO](remote_user_sso.md) | Your reverse proxy already authenticates users and sets `REMOTE_USER`. |
| [LDAP Login](ldap_login.md)           | Direct bind against LDAP / Active Directory.                          |
| **OIDC Login**                        | Native OIDC against a cloud or on-prem IdP, no proxy needed.          |

Ideal for Docker / Kubernetes deployments, where the reverse-proxy
approach either isn't available or shouldn't be the auth boundary.

## Configuration

Everything except the group-to-role table is configured in the web UI —
no `local_config.py` editing needed.

### 1. Create the Account

**Accounts → New**, type **OIDC identity provider**:

| Field    | Value                                                        |
| -------- | ------------------------------------------------------------ |
| name     | `entra-id`                                                   |
| address  | `https://login.microsoftonline.com/<tenant>/v2.0` *(issuer)*  |
| username | `<app-registration-id>` *(client id)*                        |
| password | `<client-secret>`                                            |

The `address` is the **base** of the discovery document, not the
`/.well-known/openid-configuration` URL itself.

### 2. Apply the "OIDC / SSO login" preset

**Config → Local Config → Quick configurations → OIDC / SSO login**.
Fill in the fields and press *Apply preset*:

| Key                   | Meaning                                                                 |
| --------------------- | ----------------------------------------------------------------------- |
| `OIDC_LOGIN`          | Master toggle.                                                          |
| `OIDC_ACCOUNT`        | Name of the Account from step 1.                                        |
| `OIDC_SCOPES`         | Scopes to request, space separated. `openid` is always included.        |
| `OIDC_EMAIL_CLAIM`    | Claim holding the email — the local user is matched on it.              |
| `OIDC_NAME_CLAIM`     | Claim used for the display name on auto-create.                         |
| `OIDC_GROUPS_CLAIM`   | Claim carrying the user's groups.                                       |
| `OIDC_REQUIRED_GROUP` | Optional gate — only members of this group may log in.                  |
| `OIDC_AUTO_CREATE`    | Create a local user on first successful login.                          |
| `OIDC_ADMIN_GROUP`    | Members of this group become global admins.                             |
| `OIDC_DEFAULT_ROLES`  | Roles every accepted user receives, comma separated.                    |

The preset also shows the **redirect URI** of this installation.
Register it at the identity provider exactly as printed — a mismatch is
the single most common reason an OIDC login fails.

### 3. Restart and log in

The OIDC keys take effect after a service restart. The login page then
shows a **Sign in with SSO** button.

### Editing local_config.py directly

The same settings can be written by hand; the preset only produces this:

```python
config = {
    'OIDC_LOGIN': True,
    'OIDC_ACCOUNT': 'entra-id',

    'OIDC_SCOPES': 'openid email profile groups',

    # Which claim holds the user's email address and display name
    'OIDC_EMAIL_CLAIM': 'email',
    'OIDC_NAME_CLAIM': 'name',

    # Group-based authorisation
    'OIDC_GROUPS_CLAIM': 'groups',
    'OIDC_REQUIRED_GROUP': 'cmdbsyncer-users',   # optional gate
    'OIDC_AUTO_CREATE': True,
    'OIDC_ADMIN_GROUP': 'cmdbsyncer-admins',
    'OIDC_DEFAULT_ROLES': 'host, log',
}
```

For mappings that go beyond "admins" and "everyone", add the nested
`OIDC_ROLE_MAPPING` dict — it cannot be written from the UI:

```python
config = {
    'OIDC_ROLE_MAPPING': {
        'cmdbsyncer-admins': {'global_admin': True},
        'cmdbsyncer-ops':    {'roles': ['host', 'log']},
        'cmdbsyncer-api':    {'api_roles': ['all']},
    },
}
```

`OIDC_ADMIN_GROUP` and `OIDC_DEFAULT_ROLES` are merged into that dict,
so both forms can be used together.

## Provider-specific notes

### Azure AD / Entra ID

- Account `address` (issuer): `https://login.microsoftonline.com/<tenant>/v2.0`
- Create an **App Registration**, add a **Web** platform redirect
  URI `https://<syncer>/oidc/callback`, generate a client secret.
- To expose group claims, configure **Token configuration → Add
  groups claim**; with the v2 endpoint Azure emits group object IDs
  — use those IDs (not display names) as `OIDC_ROLE_MAPPING` keys.

### Keycloak

- Account `address` (issuer): `https://keycloak.example.com/realms/<realm>`
- Create a client of type OpenID Connect, `confidential`, with the
  redirect URI set; copy the client secret.
- Map groups to a `groups` claim in **Client scopes → groups**.

### Okta

- Account `address` (issuer): `https://<yourorg>.okta.com` or
  `https://<yourorg>.okta.com/oauth2/default`
- Configure a Web application, add the redirect URI, copy the
  client secret.
- Include `groups` in the ID token via the **Groups claim** setting.

### Google Workspace

- Account `address` (issuer): `https://accounts.google.com`
- No group claim by default — `OIDC_ROLE_MAPPING` won't apply.
  Assign roles manually via the UI, or proxy through Okta/Auth0.

## Role mapping

Same union-of-groups semantics as [LDAP Login](ldap_login.md):

- The user's `groups` claim is intersected with the keys of
  `OIDC_ROLE_MAPPING` — `OIDC_ADMIN_GROUP` counts as an entry of that
  table granting `global_admin`.
- For each match, `roles`, `api_roles`, and `global_admin` are
  **unioned**, plus everything in `OIDC_DEFAULT_ROLES`.
- The user's local `roles` / `api_roles` / `global_admin` are
  replaced by the computed union on every login.

So:

- Remove a user from `cmdbsyncer-admins` in your IdP → they lose
  admin on their next login. No manual sync needed.
- Do **not** grant ad-hoc permissions via the CMDBsyncer UI —
  they get reverted on next login.
- Leave `OIDC_ROLE_MAPPING`, `OIDC_ADMIN_GROUP` and
  `OIDC_DEFAULT_ROLES` all empty to opt out of role sync; new users
  are then created with no roles and you grant them manually.

## Routes

| Route             | Purpose                                                          |
| ----------------- | ---------------------------------------------------------------- |
| `/oidc/login`     | Start the authorization-code flow (redirects to the IdP).        |
| `/oidc/callback`  | IdP redirects back here; CMDBsyncer exchanges the code for tokens and logs the user in. |

Register `https://<your-syncer>/oidc/callback` as the allowed redirect URI in the IdP.

## Audit trail

Every OIDC login attempt is recorded in the [Audit Log](audit_log.md)
(when co-licensed), with `metadata.method = 'oidc'` and these
failure reasons:

- `setup_error` — bad issuer / discovery failed
- `token_exchange_failed` — code exchange rejected by the IdP
- `no_userinfo` — IdP accepted the token but returned no profile
- `no_email_claim` — token has no email in the configured claim
- `required_group_missing` — user not in `OIDC_REQUIRED_GROUP`
- `no_local_user_and_autocreate_off` — first-time user but
  `OIDC_AUTO_CREATE = False`

## Troubleshooting

**Loop back to `/login` with no flash message**  
Check the Flask logs for `OIDC client setup failed`. Most common
cause: wrong issuer URL on the Account (`address` must be the base of the
discovery document, not the discovery URL itself).

**`token_exchange_failed`**  
- Redirect URI mismatch — must match exactly in the IdP.
- Client secret wrong or missing in the Account's password field.
- Wrong Account named in `OIDC_ACCOUNT`, or the Account is disabled.

**Groups are empty even though the user is in groups in Azure AD**  
Azure only emits groups in the ID token when configured — see the
Azure-specific notes above. Also verify the token isn't being
truncated (large groups → use `hasGroups` + Graph API lookup
instead; not yet built in, open an issue).

**Login works but user has no roles**  
`OIDC_ROLE_MAPPING` keys must exactly match the values emitted in
the `groups` claim (case-insensitive match is applied). For Azure
v2, these are **object IDs**, not display names.
