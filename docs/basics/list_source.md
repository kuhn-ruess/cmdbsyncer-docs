# Rules from a Pasted List

Most rules work through the hosts: their conditions pick the hosts, and
their outcomes are rendered with the attributes of every matching host. Some
things are not about the hosts you have, but about a list you already keep
somewhere else: services with their service level, devices that are not in
the Syncer yet, contacts, DCD connections, downtimes for a set of hosts.

For those, a rule can take a **pasted list** as its input instead of the
hosts. Set its **Rule source** to **From a pasted list**. The form then swaps
the host **Conditions** for a **Pasted List** step; switching back to
**Per host** keeps the pasted text but no longer uses it.

## The list

Paste a table, for example a block copied out of a spreadsheet:

```text
hostname;room;owner
srv01;R1;team-a
srv02;R2;team-b
```

- The **first line names the columns**. Every column becomes a Jinja
  variable for the outcomes: the header is lower cased and everything that
  is not a letter, digit or underscore becomes `_`, so `Service Level` is
  `{{ service_level }}`. The whole row is also available as `{{ row }}`
  (for example `{{ row.service_level }}`) and its 0-based position as
  `{{ row_idx }}`.
- The separator is detected from the first line: tab (what a block copied
  out of a spreadsheet arrives as), semicolon, comma or `|`. Cells in double
  quotes may contain the separator and line breaks.
- Empty lines are skipped. A header cell left empty drops its column, so a
  trailing separator does no harm. A line with more cells than the header
  is an error.

While you paste or type, the form shows below the field the number of rows
and the separator, the **column variables** (click into an outcome field and
then on a variable to insert it there), the first 20 rows, every problem
with its line and every outcome field that reads a variable which is no
column of the list. A list with a problem cannot be saved, an unknown
variable is only a warning: it renders empty.

## What a row does

Every row is rendered on its own, the way one host would be: the outcomes of
the rule are rendered with the columns of that row, the host conditions do
not apply, and other rules do not add to it. A list that cannot be read
creates nothing at all, the export names the rule and the reason.

Where a row stands for **one object** (an i-doit object, a Jira object, a
Netbox device, the device or virtual machine of Netbox interfaces, an
inventory host, the host of a downtime or of a playbook run), its `hostname`
column names it, or its `name` column when there is no `hostname` column.
That name is also `{{ HOSTNAME }}` in the outcomes. A row without a name
creates no such object and is reported by the export.

| Rule type | What a row creates |
| :-------- | :----------------- |
| [Checkmk Setup Rules](../checkmk/rules_management.md#rules-from-a-pasted-list) | one Checkmk rule per outcome; rows that only differ in the service name are joined into one rule |
| [Checkmk DCD Rules](../checkmk/dcd_rules.md) | the DCD connections of its outcomes, with `{{ cmk_site }}` and `{{ account }}` next to the columns |
| [Checkmk BI Rules and Aggregations](../checkmk/bi.md) | one BI rule or aggregation per outcome; the same ID is created once |
| [Checkmk Notification Rules](../checkmk/notification_rules.md) | one notification rule per outcome; identical rules are created once |
| [Checkmk Downtimes](../checkmk/create_downtimes.md) | the downtimes of its outcomes, on the Checkmk host the row names |
| [i-doit Custom Attributes](../i-doit/index.md) | one i-doit object, titled with the row's name |
| [Jira Export Rules](../jira/index.md) | one Jira object, found by and named with the row's name |
| [Netbox](../netbox/index.md) Devices, Virtual Machines | one device or virtual machine, named by the row |
| Netbox Interfaces (devices and virtual machines) | the interfaces of its outcomes, on the device or virtual machine the row names; a new interface gets the Netbox ID of that device or virtual machine when the outcomes give none |
| Netbox IP Addresses | the addresses of its outcomes; Assigned Object ID is the Netbox ID of the interface or its name, then on the device the row names |
| Netbox Clusters, Prefixes, Contacts, Dataflow Fields | one object, found by its outcomes like for a host |
| [VMware Custom Attributes](../vmware/index.md) | the custom attributes of the virtual machine the row names |
| Ansible Custom Variables | one more host in the inventory, with the columns and the outcomes as its variables |
| [Ansible Playbook Fire Rules](../ansible/fire_rules.md) | one run per playbook against the host the row names, once, like for a host |

## Rule types without a list

- **Filter, Rewrite and Custom Attribute rules** change the attributes of a
  host. A row is no host, so there is nothing for them to change.
- **Checkmk Export Rules** (folders, attributes, labels of hosts) turn the
  Syncer's hosts into Checkmk hosts. To bring hosts from a list into the
  Syncer, import the list (for example with the [CSV import](../csv/index.md)).
- **Checkmk Groups, User Generation and Host Tags** are no rules with
  conditions and outcomes: they collect group, user or tag names out of the
  attributes of all hosts or the objects of an account, so there are no
  outcomes a row could be rendered into.
