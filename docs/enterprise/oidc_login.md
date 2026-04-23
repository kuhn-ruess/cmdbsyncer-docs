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

## Routes

| Route             | Purpose                                                          |
| ----------------- | ---------------------------------------------------------------- |
| `/oidc/login`     | Start the authorization-code flow (redirects to the IdP).        |
| `/oidc/callback`  | IdP redirects back here; CMDBsyncer exchanges the code for tokens and logs the user in. |

Register `https://<your-syncer>/oidc/callback` as the allowed redirect URI in the IdP.

## Configuration

In `local_config.py`:

```python
config = {
    'OIDC_LOGIN': True,

    # Discovery URL base (omit /.well-known/openid-configuration)
    'OIDC_ISSUER': 'https://login.microsoftonline.com/<tenant>/v2.0',
    'OIDC_CLIENT_ID': '<app-registration-id>',

    # Preferred: secret from an env var (not stored in the config file)
    'OIDC_CLIENT_SECRET_ENV': 'OIDC_CLIENT_SECRET',
    # Or inline (less preferred):
    # 'OIDC_CLIENT_SECRET': '<raw-secret>',

    'OIDC_SCOPES': ['openid', 'email', 'profile', 'groups'],

    # Which claim holds the user's email address and display name
    'OIDC_EMAIL_CLAIM': 'email',
    'OIDC_NAME_CLAIM': 'name',

    # Group-based authorisation
    'OIDC_GROUPS_CLAIM': 'groups',
    'OIDC_REQUIRED_GROUP': 'cmdbsyncer-users',   # optional gate
    'OIDC_AUTO_CREATE': True,
    'OIDC_ROLE_MAPPING': {
        'cmdbsyncer-admins': {'global_admin': True},
        'cmdbsyncer-ops':    {'roles': ['host', 'log']},
        'cmdbsyncer-api':    {'api_roles': ['all']},
    },
}
```

## Provider-specific notes

### Azure AD / Entra ID

- `OIDC_ISSUER`: `https://login.microsoftonline.com/<tenant>/v2.0`
- Create an **App Registration**, add a **Web** platform redirect
  URI `https://<syncer>/oidc/callback`, generate a client secret.
- To expose group claims, configure **Token configuration → Add
  groups claim**; with the v2 endpoint Azure emits group object IDs
  — use those IDs (not display names) as `OIDC_ROLE_MAPPING` keys.

### Keycloak

- `OIDC_ISSUER`: `https://keycloak.example.com/realms/<realm>`
- Create a client of type OpenID Connect, `confidential`, with the
  redirect URI set; copy the client secret.
- Map groups to a `groups` claim in **Client scopes → groups**.

### Okta

- `OIDC_ISSUER`: `https://<yourorg>.okta.com` or
  `https://<yourorg>.okta.com/oauth2/default`
- Configure a Web application, add the redirect URI, copy the
  client secret.
- Include `groups` in the ID token via the **Groups claim** setting.

### Google Workspace

- `OIDC_ISSUER`: `https://accounts.google.com`
- No group claim by default — `OIDC_ROLE_MAPPING` won't apply.
  Assign roles manually via the UI, or proxy through Okta/Auth0.

## Role mapping

Same union-of-groups semantics as [LDAP Login](ldap_login.md):

- The user's `groups` claim is intersected with the keys of
  `OIDC_ROLE_MAPPING`.
- For each match, `roles`, `api_roles`, and `global_admin` are
  **unioned**.
- The user's local `roles` / `api_roles` / `global_admin` are
  replaced by the computed union on every login.

So:

- Remove a user from `cmdbsyncer-admins` in your IdP → they lose
  admin on their next login. No manual sync needed.
- Do **not** grant ad-hoc permissions via the CMDBsyncer UI —
  they get reverted on next login.
- Leave `OIDC_ROLE_MAPPING = {}` to opt out of role sync; new
  users are then created with no roles and you grant manually.

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
cause: wrong `OIDC_ISSUER` URL (it must be the base of the
discovery document, not the discovery URL itself).

**`token_exchange_failed`**  
- Redirect URI mismatch — must match exactly in the IdP.
- Client secret wrong or not set in the env var.
- `OIDC_SCOPES` doesn't include `openid`.

**Groups are empty even though the user is in groups in Azure AD**  
Azure only emits groups in the ID token when configured — see the
Azure-specific notes above. Also verify the token isn't being
truncated (large groups → use `hasGroups` + Graph API lookup
instead; not yet built in, open an issue).

**Login works but user has no roles**  
`OIDC_ROLE_MAPPING` keys must exactly match the values emitted in
the `groups` claim (case-insensitive match is applied). For Azure
v2, these are **object IDs**, not display names.
