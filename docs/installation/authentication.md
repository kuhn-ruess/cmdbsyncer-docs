# Auth and Single Sign-On

## Local Users

To log in, you first need to create a local user. The command to create one is:

```bash
./cmdbsyncer sys create_user mail@example.com
```

You can manage users in the UI under **Syncer Config → Users**.

## Single Sign-On (SSO)

SSO support is available from version 3.12 onwards.

If you want to use Single Sign-On — for example with Keycloak — configure your Apache virtual host to authenticate the request before it reaches the Syncer:

```apache
<Location /cmdbsyncer>
    AuthType openid-connect
    Require valid-user
</Location>
```

Then enable remote user login in `local_config.py`:

```python
config = {
    'REMOTE_USER_LOGIN': True,
}
```

Now go to **Syncer Config → Users** and set the username of a user to exactly match the remote username provided by your authentication provider.

When that user logs in via SSO, the Syncer authenticates them automatically. If no matching user is found, the classical login form is still available as a fallback.

!!! note
    The `REMOTE_USER_LOGIN` setting only controls whether the Syncer trusts the remote user header set by the webserver. Make sure your webserver configuration is correctly restricting access — the Syncer itself does not validate the token.
