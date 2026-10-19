# Folders and Folder Options
<span class="since">Since 4.5</span>

The Export Rules put every host into a Checkmk folder and can give each folder
options behind a `|`: contact groups (and with them the permissions on the
folder), a title, a site, tags and so on (see
[Custom Folder Attributes](export_rules.md#custom-folder-attributes)). When
several hosts land in the same folder, the Syncer merges their options into one
set. This page shows the result: which folders the host export would use, which
hosts land in them and which folder options are sent to Checkmk. The debug of a
folder tells you where every value comes from.

Go to: _Modules → Checkmk → Folders and Folder Options_.

!!! note
    Everything is calculated from the rules and hosts in the Syncer. Checkmk is
    not asked and nothing is changed: no pool seat is taken or freed, no host and
    no cache is saved. A host that waits for its first [pool folder](folder_pools.md)
    is shown where it is without one; the next host export picks its pool folder.

## The folder list

Pick a Checkmk account and press **Calculate**.

- **With an account**, its host selection applies exactly as in its host
  export: the object filter, `limit_by_hostnames`, `limit_by_accounts`, the
  [Projects](rule_projects.md) and the folder scope of
  [Limit Host Export to Folders](limit_host_export_folders.md).
- **Without an account**, every host is calculated, like on the host debug page.

Each row is one folder, shown as a tree:

| Column | What it shows |
| :----- | :------------ |
| Folder | The folder path. Parent folders are listed too, they are created on the way. |
| Hosts | How many hosts land directly in the folder (click to list them) and how many with its sub-folders. |
| Folder options sent to Checkmk | The merged folder options of all hosts of this folder. `broken option` marks a folder where one host has an option the export cannot read and skips. |

Folders made by the action **Create Empty Folder** are listed as well, with
their options.

## Debug of a folder

**Debug** next to a folder opens its debug page. It is the counterpart of the
host debug page for one folder:

- **Folder options sent to Checkmk**: the final value, after all hosts were merged.
- **Contributions and merge**: one block per host that gives the folder options,
  in the order the export reads them. For each block you see
    - the host (links to its host debug page),
    - the Export Rule that put the folder with its options there, the conditions
      that made the rule match and the folder actions of the rule,
    - every single value of the options, e.g. `contactgroups.groups` or
      `contactgroups.use`,
    - what the merge did with it.
- **Hosts in this folder**: the hosts that land directly in the folder.

The merge column follows the rules of
[Merging when hosts share a folder](export_rules.md#merging-when-hosts-share-a-folder):

| Merge | Meaning |
| :---- | :------ |
| set | The first value for this option, it is used. |
| added to the list | List entries (e.g. contact groups) not in the list yet, they are added. |
| already in the list | List entries another host gave already. |
| same value already set | A single value that equals the one already set. |
| ignored, first value wins | A single value (title, site, the `use` flag, ...) that differs from the one already set. The first one is kept and shown next to it. |
| dropped, renders to no value | The option renders to `True`, `False` or `None` for this host and is not sent. |
| broken, skipped by the export | The options of this host cannot be read (e.g. a stray brace) and are skipped. |

### Example: who gave which permission

Two Export Rules move hosts into the same folder, each with its own contact
group:

```text
Rule "Team A": team equal team_a  → shared | {'contactgroups': {'groups': ['team_a'], 'use': True}}
Rule "Team B": team equal team_b  → shared | {'contactgroups': {'groups': ['team_b'], 'use': True}}
```

The debug of `/shared` shows:

| # | Host | Export Rule | Option | Value | Merge |
| :- | :--- | :---------- | :----- | :---- | :---- |
| 1 | srv01.example.com | Team A (matched: tag equal 'team', value equal 'team_a') | contactgroups.groups | ['team_a'] | set |
| | | | contactgroups.use | True | set |
| 2 | srv02.example.com | Team B (matched: tag equal 'team', value equal 'team_b') | contactgroups.groups | ['team_b'] | added to the list |
| | | | contactgroups.use | True | same value already set |

and as the value sent to Checkmk
`contactgroups: groups: team_a, team_b, use: True`.

## Permissions and restricted users

The page needs the `Checkmk` right.

A folder is shared by all hosts in it, so users limited to accounts or
templates (see [Local Users](../installation/authentication.md#restricting-a-user-to-accounts)) see it like this:

- They only see the folders where at least one of their hosts lands (directly
  or in a sub-folder) or gives options, plus the parents of those folders.
- Host lists and contributions only show their own hosts. Hidden hosts are only
  counted (`outside your scope`).
- The folder options are merged from their own hosts only, so a contact group
  given by a host outside their scope never shows up. The debug page then says
  that the value sent to Checkmk may hold more.

The account dropdown lists every Checkmk account: the account only decides which
hosts the export would send, the user's own scope is applied on top.

!!! tip
    The calculation runs over all hosts of the account each time the page is
    opened. In large environments it takes as long as the calculation step of a
    host export.
