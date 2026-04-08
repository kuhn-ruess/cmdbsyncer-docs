# Export Hosts to Checkmk

This guide walks through the minimal setup to get hosts from the Syncer into Checkmk —
including a rule that places them into the right folder based on a host attribute.

## Prerequisites

- A Checkmk account configured in the Syncer (**Accounts**)
- At least one host with attributes already imported into the Syncer

---

## Step 1: Set up the Filter Rule

The filter rule controls **which host attributes are exported as labels to Checkmk**.
By default, none of the Syncer attributes are sent to Checkmk as labels — you have to explicitly whitelist them here.
The only exception are labels starting with `cmdbsyncer/`, which the Syncer manages internally.

Navigate to:
**Modules → Checkmk → Filter Attributes for Checkmk Export**

Create a new rule. Leave the conditions empty to apply it to all hosts, and add the attribute names you want to export as outcomes:

| Field | Value |
| --- | --- |
| Outcome | `os` |
| Outcome | `location` |

Each outcome is an attribute name from the Syncer that will be sent as a label to Checkmk.

!!! tip
    Use conditions to export different sets of attributes for different hosts — for example only export the `datacenter` label for hosts where `os` equals `linux`.

---

## Step 2: Create a Folder Rule

The folder rule controls **where in Checkmk** the host is placed.
Navigate to **Modules → Checkmk → Set Folder and Attributes of Host**.

Create a new rule with the action **Move to Folder**.

### Example: Static folder

To put all matching hosts into a fixed folder, enter the folder name in the **Action Param** field:

| Field | Value |
| --- | --- |
| Action | `Move to Folder` |
| Action Param | `my_servers` |

This places all hosts into `/my_servers` in Checkmk.

### Example: Folder from an attribute

If your hosts have a `location` attribute (e.g. `dc1`, `dc2`), you can use it directly as the folder name:

| Field | Value |
| --- | --- |
| Action | `Move to Folder` |
| Action Param | `{{ location }}` |

Hosts with `location = dc1` go into `/dc1`, hosts with `location = dc2` go into `/dc2`.

### Example: Multi-level path with `/`

You can build a nested folder path directly in a single rule by using `/` as separator:

| Field | Value |
| --- | --- |
| Action | `Move to Folder` |
| Action Param | `{{ os }}/{{ location }}` |

A host with `os = linux` and `location = dc1` goes into `/linux/dc1`.
This also works with static parts mixed in:

| Action Param | Result for `location = dc1` |
| --- | --- |
| `servers/{{ location }}` | `/servers/dc1` |
| `{{ os }}/{{ location }}/prod` | `/linux/dc1/prod` |

### Example: Multi-level path with stacked rules

Alternatively, use multiple rules that are stacked in sort order:

| Sort | Action Param | Result |
| --- | --- | --- |
| 10 | `{{ os }}` | `/linux` |
| 20 | `{{ location }}` | `/linux/dc1` |

The final folder path is the combination of all **Move to Folder** outcomes in sort order.
Both approaches — `/` in one rule or multiple stacked rules — produce the same result.

!!! note
    If a Jinja variable used in a folder rule is not defined for a host, that rule is skipped for that host.
    Use the **last_match** option on a rule to stop processing further rules once it matches.

---

## Step 3: Run the Export

Once filter and folder rules are in place, run the export from the CLI:

```bash
./cmdbsyncer checkmk export_hosts ACCOUNTNAME
```

Or schedule it as a cronjob via **Cronjobs → Checkmk: Export Hosts**.

After the export, activate the changes in Checkmk:

```bash
./cmdbsyncer checkmk activate_changes ACCOUNTNAME
```

---

## Debugging

To check what folder and attributes a specific host would get without running the full export:

```bash
./cmdbsyncer checkmk debug_host HOSTNAME
```

This prints the resolved folder path, all labels, and the actions that would be applied — without making any changes in Checkmk.

For a full reference of the available rule actions, see [Set Folder and Host Attributes](export_rules.md).
