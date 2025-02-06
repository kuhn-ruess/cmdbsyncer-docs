# LDAP

The Syncer has the options to import all kind of objects from LDAP.

To use that, you need to create an [Account](../basics/accounts.md) of the Type 'LDAP'.
After saving it, the Account will provide you with some necessary fields you need to set.


| Field            | Description                                              |
| ---------------- | -------------------------------------------------------- |
| `base_dn`        | Base for Import, Example: DC=Domain, DC=Domain           |
| `search_filter`  | Example: (&objectCategory=Person)(objectClass=user))     |
| `attributes`     | Fields to read, like cn                                  |
| `hostname_field` | Field which the syncer should use to identify the object |
| `encoding`       | utf-8 or ascii, depending on your server                 |

Some tipsabout the Account Setting: If you import a certain type of objects, which are not hosts, mark the account as `is_object` and choose an Object Type. This way, you later can better filter the input for operations.

## Testing the Import
You can test the Import using the commandline.

Command: _./cmdbsyncer ldap import_objects ACCOUNTNAME_

## Setting the Process
For Production Use, setup the Job as a [cron](../basics/cron.md)








