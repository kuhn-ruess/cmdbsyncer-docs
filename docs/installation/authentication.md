# Auth and Single Sign On
(Works from Version 3.12 on)

In general, to log in, you need to create a user as already described in the docs. The command to do so is _./cmdbsycer sys create_user mail@test.de_

If you want to use Single Sign-On, like with Keycloak, you need to set that in Apache first:

```
<Location /cmdbsyncer>
	AuthType openid-connect
    Require valid-user
</Location>
```

Then in your local config, set **REMOTE_USER_LOGIN** to True.

Now you may update your users in __Syncer Config -> Users__ and set their name like the remote username provided by your authentication provider.

That is it. Now if that user is found, the Syncer will authenticate you. If not, you can still use the classical login.