# Config Variables
List of config Variables which can be overwritten in [local_config.py](../basics/lcl_config.md)


| Variable                              | Description                                                                       |
| ------------------------------------- | --------------------------------------------------------------------------------- |
| CMK_BULK_CREATE_HOSTS                 | Default True: Bulk Create Hosts                                                   |
| CMK_BULK_CREATE_OPERATIONS            | How many objects for each bulk request                                            |
| CMK_BULK_DELETE_HOSTS                 | Default: True: Bulk Delete Host                                                   |
| CMK_BULK_DELETE_OPERATIONS            | How many objects for each bulk request                                            |
| CMK_BULK_UPDATE_HOSTS                 | Default True: Bulk Update Hosts                                                   |
| CMK_BULK_UPDATE_OPERATIONS            | How many objects for each bulk request                                            |
| CMK_DONT_DELETE_HOSTS                 | Disable Deletion of hosts when syncing                                            |
| CMK_LOWERCASE_FOLDERNAMES             | Default: True, Folder names are lowercase                                         |
| CMK_COLLECT_BULK_OPERATIONS           | Default: False, Do bulk operations at the end                                     |
| CMK_GET_HOST_BY_FOLDER                | Default: False: Query Hosts by Folder, not with one call.                         |
| CMK_DETAILED_LOG                      | Log for every Host the Attribute Changes done                                     |
| CMK_JINJA_USE_REPLACERS               | Default: False, Configured Replacers are used for TAG Cleanup Jinja Functions     |
| CMK_JINJA_USE_REPLACERS_FOR_HOSTNAMES | Default: False, Configured Replacers are used for Hostname Cleanup Jinja Function |
