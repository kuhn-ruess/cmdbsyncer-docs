# Set Folders and Host Attributes

These rules control how hosts are exported to Checkmk: which folder they land in, which attributes they carry, and special behaviors like cluster creation or opt-outs.

Go to: _Modules → Checkmk → Set Folder and Attributes of Host_

Folder-based rules stack automatically. All folder outcomes across all matching rules are combined in sort order to produce a nested folder path like `/this/is/my/folder`. Use the **Last Match** option on rules to stop evaluation after the first match and avoid unexpected stacking.

## Available Actions

| Action                                 | Description                                                                                                                      |
| :------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------- |
| Move to Folder                         | Move the host to a folder. Supports full Jinja — variables that do not match cause the rule to be skipped.                       |
| Folder by Attribute Name               | Use the attribute key as the folder name, selected by attribute value.                                                           |
| Pool Folder                            | Assign host to a Folder Pool. Optionally restrict to specific pool names (comma-separated). See [Folder Pools](folder_pools.md). |
| CMK Attribute by Syncer Attribute      | Export a Syncer attribute to Checkmk under the same or a mapped attribute name.                                                  |
| Custom CMK Attributes                  | Create a key:value attribute. Use `{{HOSTNAME}}` as placeholder. Separate multiple values with `\|\|`.                           |
| Remove given Attribute if not assigned | Remove specified Checkmk attributes if no other Syncer rule sets them for this host.                                             |
| Cluster                                | Create the host as a Cluster. Specify which attributes contain the node names (comma-separated, wildcard `*` supported).         |
| Parents                                | Set the host parent. Jinja supported.                                                                                            |
| Move Optout                            | Host is never moved to another folder after initial creation.                                                                    |
| Update Optout                          | Host attributes are never updated after initial creation.                                                                        |
| Create Optout                          | Host is not created in Checkmk, but its attributes are updated if it already exists.                                             |
| Prefix Labels                          | Every exported label gets the configured prefix.                                                                                 |
| Update only Prefixed Labels            | Only labels with the given prefix are changed by the Syncer.                                                                     |
| Dont update prefixed Labels            | Labels with the given prefix are never touched by the Syncer.                                                                    |

## Write Status Back (CMK_WRITE_STATUS_BACK)

When `CMK_WRITE_STATUS_BACK` is enabled in `local_config.py`, the Syncer writes the Checkmk existence status of each host back into the Syncer host inventory after every export run:

```python
'CMK_WRITE_STATUS_BACK': True
```

For every host processed during a sync, the Syncer sets the inventory key `checkmk_status`:

| Attribute     | Type    | Description                                          |
| :------------ | :------ | :--------------------------------------------------- |
| `is_existing` | boolean | `True` if the host exists in Checkmk, `False` if not |

Access this value in conditions and Jinja templates as `cmk__is_existing`.

## Custom Folder Attributes

The Syncer creates all required folders automatically. You can set Checkmk folder attributes — including the visible title — by appending them after a pipe character in the folder name.

**Hardcoded folder with attributes:**

```text
/my_folder | {'title': 'My Nice Title', 'tag_something': 'value'}
```

**Jinja-based folder name with attributes:**

```text
/{{my_jinja_var}} | {'title': 'My Nice Title', 'tag_something': 'value'}
```

**Jinja in the attributes as well:**

```text
/{{my_jinja_var}} | {'title': '{{var_containing_title}}', 'tag_something': 'value'}
```

The pipe syntax is separate from the Jinja syntax — note where the pipe is placed relative to the closing `}}`.
