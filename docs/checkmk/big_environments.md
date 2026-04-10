# Large Environments (100k+ Hosts)

The Syncer can manage Checkmk environments with more than 100,000 hosts. Several configuration switches are available to prevent timeouts and reduce memory pressure in these scenarios.

Set all of these in `local_config.py`.

## Timeout Prevention

| Variable                      | Description                                                                                                                                   |
| :---------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------- |
| `CMK_COLLECT_BULK_OPERATIONS` | Separates DB and Checkmk API operations into two phases. Prevents DB cursor timeouts when Checkmk API calls take too long. Requires more RAM. |
| `CMK_GET_HOST_BY_FOLDER`      | Queries hosts from Checkmk folder by folder instead of in one request. Prevents request timeouts caused by retrieving too many hosts at once. |

## Object Type Limiting

If you have multiple object types in the Syncer database (hosts, applications, contacts, etc.), operations that only need to process hosts do not need to iterate over all other objects. Limiting by object type happens at the database level and is significantly faster than using standard filter rules.

To configure it:

1. Open the Checkmk account in the Syncer
2. Add a **Plugin Setting**
3. Select the **operation** you want to limit (e.g. `export_hosts`)
4. Select the **object types** to include

This setting applies to all commands using that account.

## Checkmk Version Compatibility

For Checkmk 2.2 environments, set:

```python
config = {
    'CMK_SUPPORT': '2.2',
}
```

See [Local Config Variables](config_vars.md) for all Checkmk-specific config options.
