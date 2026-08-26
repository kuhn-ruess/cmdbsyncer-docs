# Set Folders and Host Attributes

These rules control how hosts are exported to Checkmk: which folder they land in, which attributes they carry, and special behaviors like cluster creation or opt-outs.

Go to: _Modules → Checkmk → Set Folder and Attributes of Host_

Folder-based rules stack automatically. All folder outcomes across all matching rules are combined in sort order to produce a nested folder path like `/this/is/my/folder`. Use the **Last Match** option on rules to stop evaluation after the first match and avoid unexpected stacking.

Each outcome action is chosen from a set of categorized cards (Folder placement, Attributes, Built-in Attributes, Labels, Opt-outs, …). An outcome you are not editing stays compact and shows only the selected action — click **Change action** to pick a different one. **Every parameter supports Jinja**, so you can reference `{{hostname}}` or any host attribute in any action's value.

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

## Built-in Host Attributes

For the most common Checkmk host attributes there are ready-made actions, so you do not need to know the attribute key or use **Custom CMK Attribute**. For the enum-based ones the form offers the valid values as one-click suggestions; the parameter field stays editable and supports Jinja.

| Action              | Sets attribute       | Example values                                             |
| :------------------ | :------------------- | :--------------------------------------------------------- |
| IP Address Family   | `tag_address_family` | `ip-v4-only`, `ip-v6-only`, `ip-v4v6`, `no-ip`             |
| IPv4 Address        | `ipaddress`          | `192.168.10.5`, `{{ip}}`                                   |
| IPv6 Address        | `ipv6address`        | `2001:db8::5`                                              |
| Checkmk Agent       | `tag_agent`          | `cmk-agent`, `all-agents`, `special-agents`, `no-agent`    |
| SNMP                | `tag_snmp_ds`        | `no-snmp`, `snmp-v1`, `snmp-v2`                            |
| Piggyback           | `tag_piggyback`      | `auto-piggyback`, `piggyback`, `no-piggyback`             |
| Criticality         | `tag_criticality`    | `prod`, `critical`, `test`, `offline`                     |
| Networking Segment  | `tag_networking`     | `lan`, `wan`, `dmz`                                        |
| Alias               | `alias`              | any text, e.g. `{{description}}`                          |
| Monitored on Site   | `site`               | your Checkmk site id, e.g. `cmk`                          |

`Criticality` and `Networking Segment` are Checkmk's default tag groups — if you customized those tag groups, just type your own value instead of using the suggestions.

!!! note "Deprecated actions"
    A few older actions (`Deprecated: Use move_folder with Jinja`, `Migrate to Custom CMK Attribute`, and `Just switch to normal Custom Attribute`) are being phased out. They can no longer be selected for new rules and **will be removed with 4.4**. Rules that still use one cannot be saved until migrated, and the start page lists them for you.

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

!!! tip "Edit them per folder instead of typing the dict"
    On a `Move to Folder` or `Create Empty Folder` action, the button **Edit folder attributes** below the value opens an editor with one card per folder level and input fields for the common attributes (title, contact groups, site, labels, tags). It writes the pipe syntax below back into the value field, which stays editable — so you can switch between both at any time. A level the editor cannot read exactly (for example a Jinja expression as the whole options dict) is left untouched and marked as such.

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
