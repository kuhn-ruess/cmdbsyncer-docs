# SYS Module

The `sys` module contains internal maintenance and administration commands.
It is only available via the CLI:

```bash
./cmdbsyncer sys <command>
```

---

## Commands

| Command | Arguments | Description |
| --- | --- | --- |
| `create_user` | `EMAIL` | Create a new user or reset an existing user's password and disable 2FA. The generated password is printed to the console. The user is created as a global admin. |
| `delete_all_hosts` | `[ACCOUNT]` | Delete all hosts from the database. Prompts for confirmation. Pass an account name to limit deletion to hosts imported by that account. Hosts with `no_autodelete` set and templates are never deleted. |
| `delete_cache` | `[CACHE_NAME]` | Clear the attribute cache of all hosts. Pass a prefix to only clear cache keys starting with that string (e.g. `checkmk`). Without argument, the entire cache is cleared. |
| `delete_inventory` | `[PREFIX]` | Delete inventory data from all hosts. Pass a prefix to only remove inventory keys starting with that string (e.g. `myplugin`). Without argument, all inventory data is cleared. |
| `maintenance` | `[DAYS]` | Delete hosts that have not been seen for more than `DAYS` days (default: 7). Also available as a schedulable cronjob. |
| `reset_folder_pools` | — | Reset the usage counters of all Checkmk folder pools and clear the assigned folder from all hosts. Prompts for confirmation. Run a full re-sync afterwards. |
| `self_configure` | — | Seed required default configuration. Creates `local_config.py` if missing, generates `SECRET_KEY` and `CRYPTOGRAPHY_KEY` if not yet set, and runs any pending database migrations. **Run this after every update.** |
| `show_accounts` | — | Print a table of all enabled accounts (name, type, address). Useful when working on the CLI without access to the GUI. |
| `update_cmdb` | — | Re-apply CMDB templates to all hosts in the database. Use after changing template matching rules. |

---

## Notes

**`maintenance`** is also registered as a cronjob ("Syncer: Maintenance") and can be scheduled from the GUI.
When called via cronjob, pass an account name instead of days — the number of days is then read from the account's `delete_hosts_after_days` setting.

**`delete_all_hosts`** and **`reset_folder_pools`** both require interactive confirmation (`y`).
They cannot be run non-interactively.

**`self_configure`** must be run after the initial setup and after every update.
It is safe to run multiple times — it only applies missing values.
