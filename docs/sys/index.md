# SYS Module
The sys Module contains Internal Functions. It can only be used in the CLI. You reach it with _./cmdbsyncer sys_

| Option             | Description                                                                                |
| ------------------ | ------------------------------------------------------------------------------------------ |
| create_user        | Create a New User, or reset Password/ 2FA Code                                             |
| delete_all_hosts   | Delete all Hosts, add a Account name to filter                                             |
| delete_cache       | Delete Hosts Cache                                                                         |
| delete_inventory   | Delete Hosts Inventory Information                                                         |
| maintenance        | Run Cleanup of Hosts, use best with Account <br>Will delete Hosts not found any more       |
| reset_folder_pools | Reset Usage of Checkmk Folder Pools.                                                       |
| self_configure     | Seed default configurations if needed                                                      |
| show_accounts      | Nice Table with list of all configured Accounts.<br>Comes in Handy when working on the CLI |