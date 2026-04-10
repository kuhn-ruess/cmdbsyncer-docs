# Manage Checkmk Users

The Syncer can create, update, disable, or delete users in Checkmk based on your host and object data.

Go to: _Modules → Checkmk → Manage Checkmk Users_

Each rule entry controls one user. The available fields map directly to the Checkmk user configuration. For each user, you can:

- **Create or update** the user with the configured attributes
- **Overwrite the password** (if a password value is set)
- **Disable the login** (if the disable flag is set)
- **Delete the user** if they are found in Checkmk and the delete flag is set

Use the standard [Conditions](../basics/conditions.md) to control which hosts or objects trigger a user entry. This allows dynamic user management driven by your CMDB data.

## Command Line

```bash
./cmdbsyncer checkmk export_users ACCOUNTNAME
```
