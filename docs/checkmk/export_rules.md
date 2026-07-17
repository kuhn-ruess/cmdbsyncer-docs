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

### Contact Groups and WATO Permissions

Contact groups are just another folder attribute, named `contactgroups`. Its value is a dict: `groups` holds the list of contact groups and `use` grants those groups permission on the folder (WATO permissions).

```text
/{{customer}} | {'contactgroups': {'groups': ['team_{{customer}}'], 'use': True}}
```

Optional flags inside `contactgroups`:

| Flag            | Meaning                                                                    |
| :-------------- | :------------------------------------------------------------------------- |
| `use`           | Add these contact groups to the hosts in this folder.                      |
| `recurse_use`   | Also add the groups as contacts to the hosts in **all sub-folders**.       |
| `recurse_perms` | Also grant permission on **all sub-folders**.                              |

This assigns the groups on the **folder**. To have the Syncer create the group objects themselves from host attributes, see [Manage Contact Groups](recipe_contact_groups.md).

### Merging when hosts share a folder

Several hosts can land in the same folder while each brings its **own** contact groups — for example one rule per customer adding `team_a`, another adding `team_b`, both resolving to the same folder. In that case the Syncer **unions** the `groups` lists (duplicates removed), so the folder ends up with the contact groups of **all** its hosts:

```text
Host A → /shared | {'contactgroups': {'groups': ['team_a'], 'use': True}}
Host B → /shared | {'contactgroups': {'groups': ['team_b'], 'use': True}}

Result folder /shared → contactgroups.groups = ['team_a', 'team_b']
```

Scalar options such as `title` or `site` cannot be merged — two hosts cannot pick one title — so the **first** host to reach the folder wins for those. The Syncer is the source of truth for the merged group list: it replaces whatever contact groups are currently set on that folder in Checkmk. If you manage some folders' contact groups by hand in Checkmk, do not also set them via a folder option.
