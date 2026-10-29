# OP5 Monitor

The Syncer imports hosts from [OP5 Monitor](https://www.itrsgroup.com/products/op5-monitor),
together with the host groups and contacts they belong to.

## How to Set it Up

1. Create an [Account](../basics/accounts.md) of type OP5 Monitor
2. Import the hosts using a [Cron Job](../basics/cron.md) or from the command line:
   `./cmdbsyncer op5 import_hosts ACCOUNTNAME`

Instead of importing, `./cmdbsyncer op5 inventorize_hosts ACCOUNTNAME` adds the
OP5 data as inventory to hosts that already exist in the Syncer.

## The Account Settings

| Field    | Content                                                      |
| -------- | ------------------------------------------------------------ |
| Address  | URL of the OP5 server, for example `https://op5.example.com` |
| Username | OP5 user with access to the API                              |
| Password | Password of that user                                        |

The user needs the permission to read hosts through the OP5 API.

| Custom Field       | Content                                                         |
| ------------------ | --------------------------------------------------------------- |
| `columns`          | Comma separated list of host columns to read, empty for default |
| `rewrite_hostname` | Optional Jinja template to change the hostname                  |

## Imported Attributes

Without `columns` the Syncer reads the following attributes of every host:

| Attribute                | Content                                           |
| ------------------------ | ------------------------------------------------- |
| `name`                   | Hostname in OP5, used as hostname in the Syncer   |
| `alias`                  | Alias of the host                                 |
| `display_name`           | Display name of the host                          |
| `address`                | IP address or DNS name                            |
| `groups`                 | List of the host groups the host is member of     |
| `contacts`               | List of the contacts of the host                  |
| `contact_groups`         | List of the contact groups of the host            |
| `parents`                | List of the parent hosts                          |
| `notes`                  | Notes of the host                                 |
| `custom_variable_<name>` | One attribute per custom variable, name lowercase |

`groups`, `contacts`, `contact_groups` and `parents` are lists. To use them as
single values, rewrite them with the
[Jinja helpers](../advanced/jinja_functions.md) in the rewrite rules of the
module you export with.
