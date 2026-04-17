# Single Sign-On (SSO)

!!! note "Enterprise feature"
    Trusted-header SSO is part of the [Enterprise Edition](../installation/enterprise.md). Without the `cmdbsyncer-enterprise` package and a valid license, the `REMOTE_USER_LOGIN` setting has no effect and the classical login form is used.

SSO support is available from version 3.12 onwards.

## How It Works

CMDBsyncer does not implement an OpenID Connect or SAML client itself. Instead, it trusts the `REMOTE_USER` header set by the reverse proxy in front of it. The proxy is responsible for authenticating the request; CMDBsyncer then logs the matching local user in automatically.

## Configuration

Configure your reverse proxy to authenticate the request before it reaches CMDBsyncer. Example with `mod_auth_openidc` for Keycloak:

```apache
<Location /cmdbsyncer>
    AuthType openid-connect
    Require valid-user
</Location>
```

When running CMDBsyncer behind Apache with `mod_wsgi`, add `WSGIPassAuthorization On` to your virtual host. Without it, Apache strips the `Authorization` header before the request reaches CMDBsyncer — SSO modules that rely on it (or API clients that send bearer tokens) will fail silently.

```apache
WSGIPassAuthorization On
```

Enable the trusted-header login in `local_config.py`:

```python
config = {
    'REMOTE_USER_LOGIN': True,
}
```

Then go to **Profile → Users** and set the `name` of each user to match exactly the remote username provided by your identity provider. When that user logs in via SSO, CMDBsyncer authenticates them automatically.

## Fallback

If no matching user exists for the remote username, the classical login form is still available. The two mechanisms coexist.

## Security Notes

!!! warning "Harden the webserver"
    `REMOTE_USER_LOGIN` makes CMDBsyncer trust the `REMOTE_USER` header set by the webserver. Make sure your reverse proxy strips that header on unauthenticated paths — otherwise the login becomes trivially forgeable by clients setting the header themselves.

!!! note
    The `REMOTE_USER_LOGIN` setting only controls whether CMDBsyncer trusts the remote user header. The actual authentication (token validation, session handling, etc.) must be done by the webserver.
