# Create a Label in Checkmk

There are three ways to get a label onto a host in Checkmk via the Syncer.
All three end with the same step: whitelisting the attribute in the Filter rule so it gets exported.

---

## Step 1: Whitelist the attribute in the Filter Rule

No matter how you create or transform an attribute, it only reaches Checkmk as a label if you explicitly allow it in the filter rule.

Navigate to **Modules → Checkmk → Filter Attributes for Checkmk Export** and add the attribute name as an outcome:

| Field | Value |
| --- | --- |
| Outcome | `os` |

Any existing Syncer attribute can be used here directly — just enter its name as the outcome.
The Syncer will then send it as a label to Checkmk on the next export.

!!! note
    This applies to all attributes already on the host — whether they come from an import, inventory, custom attributes, or a rewrite rule. If the name is in the filter, it goes to Checkmk.

---

## Way 1: Use an existing attribute

If the host already has the attribute you need (e.g. `os`, `location`, `serial`), you only need to whitelist it as described in Step 1. Nothing else is required.

---

## Way 2: Create a global Custom Attribute

Use this when you want to assign a fixed value (or a Jinja-based value) to all hosts that match a condition — without depending on an existing import attribute.

Navigate to **Syncer Rules → Custom Attributes**.

Create a new rule:

| Field | Example |
| --- | --- |
| Condition | `os` equals `windows` |
| Outcome name | `monitoring_team` |
| Outcome value | `windows_ops` |

This creates the attribute `monitoring_team = windows_ops` on every host where `os` is `windows`.

Since version 3.12.1, the outcome value supports Jinja:

| Outcome value | Result for hostname `srv01` |
| --- | --- |
| `team_{{ location }}` | `team_dc1` |
| `{{ os }}-server` | `windows-server` |

Then whitelist `monitoring_team` in the filter rule as described in Step 1.

---

## Way 3: Create or transform an attribute in the Rewrite section

The Checkmk-specific rewrite rules let you create new attributes or modify existing ones just before the export — without affecting other modules.

Navigate to **Modules → Checkmk → Rewrite and Create Custom Syncer Attributes**.

### Rename an existing attribute

| Field | Value |
| --- | --- |
| Old Attribute Name | `csv_ipaddress` |
| Operation (Name) | `Overwrite with fixed String` |
| New Attribute Name | `ipaddress` |
| Operation (Value) | `Don't change` |

This renames `csv_ipaddress` to `ipaddress` for the Checkmk export only.

### Create a new attribute from other attributes

Set an attribute name that does not exist yet as **Old Attribute Name** — the Syncer will create it:

| Field | Value |
| --- | --- |
| Old Attribute Name | `cmk_alias` |
| Operation (Name) | `Don't Use` |
| Operation (Value) | `With Jinja Template` |
| New Value | `{{ os }}-{{ location }}` |

This creates `cmk_alias = linux-dc1` on a host with `os = linux` and `location = dc1`.

Then whitelist `cmk_alias` in the filter rule as described in Step 1.

---

## Summary

| Approach | Where | When to use |
| --- | --- | --- |
| Existing attribute | Filter rule only | Attribute already exists on the host |
| Custom Attribute | Syncer Rules → Custom Attributes | Assign fixed or computed values based on conditions, across all modules |
| Rewrite | Modules → Checkmk → Rewrite | Rename, transform, or create attributes specifically for the Checkmk export |

All three require the attribute to be whitelisted in **Modules → Checkmk → Filter Attributes for Checkmk Export**.
