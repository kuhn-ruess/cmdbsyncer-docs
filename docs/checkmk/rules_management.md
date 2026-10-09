# Manage Checkmk Setup Rules

The Syncer can create, update, and delete Checkmk setup rules automatically — for example threshold rules, active check configurations, or contact group assignments. Rules are created for specific hosts based on their attributes, and deleted again when the conditions no longer apply.

Go to: _Modules → Checkmk → Manage Checkmk Setup Rules_

!!! tip "Read a run before you make it"
    `checkmk export_rules <account> --dry-run` calculates everything and
    prints every rule it would create, update and delete — values included —
    without sending anything to Checkmk. See
    [Commandline Parameters](commandline.md#try-the-rule-export-out-before-it-runs).

## Rule Settings

These apply to the whole rule and decide *for which hosts* it is calculated.

| Option        | Description                                                                                 |
| :------------ | :------------------------------------------------------------------------------------------ |
| Name          | Name of the Syncer rule. It ends up in the description of every Checkmk rule it creates (see below) |
| Documentation | Free text for your own notes                                                                |
| Project       | Optional. Assign the rule to a [Project](../basics/projects.md), which limits it to the accounts the project allows (empty account filter = all accounts) |
| Enabled       | Only enabled rules are exported                                                             |
| Last Match    | Stop evaluating further rules for a host once this one matched                              |
| Static Rule   | Host-independent rule: render once and always create it, ignoring the match conditions (see below) |
| Rule source   | **Per host** (default): the outcomes are rendered for every host matching the conditions. **From a pasted list**: they are rendered once per row of a list, see [Rules from a pasted list](#rules-from-a-pasted-list) |
| Conditions    | Which hosts the rule applies to — see [Conditions](../basics/conditions.md)                  |

## Outcomes: the Checkmk Rule

Each outcome creates one entry in a Checkmk ruleset. All fields support Jinja
and see the host's attributes, `{{ HOSTNAME }}` included.

| Option                          | Description                                                                           |
| :------------------------------ | :------------------------------------------------------------------------------------ |
| Ruleset                         | Checkmk ruleset ID (searchable picker over the known 2.4/2.5 rulesets — see below)   |
| Folder                          | Target folder in Checkmk                                                              |
| Folder Index                    | Position of the rule within the folder                                                |
| Comment                         | Rule comment                                                                          |
| Value Template                  | Jinja template for the rule value (check Checkmk Swagger API for the expected format) |
| Keep manual Value               | Write the Value only once (on rule creation) and never overwrite it afterwards, so it can be adjusted in Checkmk. A hint is added to the rule description and comment. |
| Enforce exact Value             | Compare the Value exactly, so entries removed from the Value Template are applied too (see below) |
| Loop over List (Attribute or Jinja) | Create one Checkmk rule per list entry instead of a single one (see below). Empty = one rule |
| Condition — Host name           | Only apply to these hosts. Comma-separated = any of them matches (OR)                 |
| Condition — Host label          | Only apply to hosts carrying this label. One `key:value` label only                    |
| Condition — Service name        | For service rulesets only: apply to these services. Comma-separated = OR              |
| Condition — Service label       | For service rulesets only: apply to services carrying these labels. `key:value`, comma-separated = all must match (AND) |

A condition left empty means no restriction on that dimension. Note the
difference between the two comma rules: for names a comma means OR, for
service labels it means AND.

If a syncer-owned rule is found in a folder other than the one configured
here, the export moves it to the configured folder on the next run instead
of leaving the misplaced copy behind.

!!! tip
    A rule using **Condition — Host name** with `{{ HOSTNAME }}` ends up as one Checkmk
    rule listing every matching host — on a large installation that means
    hundreds of hostnames in one condition.
    [Rule Optimization](rule_optimization.md) finds those rules and the host
    label that covers exactly the same hosts, and can switch them over for you.
    It is linked above the rule list.

## One rule per list entry (Loop over List)

**Loop over List** turns a single outcome into one Checkmk rule per entry of a
list. Leave it empty and the outcome creates exactly one rule.

The field takes two spellings, decided by whether it contains a brace:

- **A plain Host Attribute name** — the attribute holding the list, e.g.
  `services`. A comma separated string is split into entries as well.
- **A Jinja expression** — anything that renders to a list or a comma
  separated string, with all host attributes and filters available, e.g.

  ```jinja
  {{ get_list(services)|reject("equalto", "web")|join(",") }}
  ```

  so the entries can be built, filtered or combined instead of having to exist
  as an attribute of their own.

Inside every template of that outcome — Value, Folder, conditions — the current
entry is available as `{{ loop }}` and its 0-based position as `{{ loop_idx }}`.

An entry that cannot be rendered is reported and the outcome is skipped for
that host, instead of aborting the export.

## Conditions Checkmk does not support

Not every ruleset accepts every condition. Checkmk's REST API answers such a
rule with a success, but **stores it without the condition** — a host ruleset
(for example `active_checks:*` or `host_contactgroups`) drops service
conditions and service labels, a ruleset that assigns labels cannot match on
those labels.

The Syncer knows which conditions a ruleset keeps and leaves the others out of
the exported rule, so what it sends is what Checkmk stores. Without that, every
run would compare its own rule against a stored copy that never matches and
delete and recreate it each time.

You are told once per ruleset and condition:

```text
Checkmk ignores the 'service_description' condition in ruleset
'active_checks:http', so it is left out of the exported rule.
Remove it from the Setup Rule.
```

The rule itself is exported normally — the message only says the condition has
no effect, so remove it from the Setup Rule to keep it honest.

## Which Syncer rule created a Checkmk rule

Every rule the Syncer creates carries its own marker in the Checkmk rule
description, followed by the name of the Setup Rule it was generated from:

```
cmdbsyncer_<account_id> - <Name of the Syncer rule>
```

So the Checkmk rule list already says which Syncer rule you have to edit to
change a rule — no need to search for the matching Value Template.

A rule with **Keep manual Value** additionally ends on `(Value editable)`, as
a reminder that its Value may be adjusted in Checkmk and the Syncer will not
overwrite it.

Descriptions are kept up to date: when a Syncer rule is renamed, the next
export rewrites the description of the Checkmk rules it owns — the rule itself,
including a manually adjusted Value, stays untouched. Rules created by older
Syncer versions carry the plain `cmdbsyncer_<account_id>` marker and get the
name on the next export.

If two Syncer rules are configured with exactly the same outcome, the name is
left out — the rules cannot be told apart.

## Removing rules that are no longer generated

While a rule still produces at least one Checkmk rule, the export removes any
of its earlier copies that no longer match. But when you **disable or delete**
a rule so it produces nothing at all, its previously created Checkmk rules are
left in place by default.

Set the Checkmk account custom field `remove_orphaned_rules` to `True` to also
clean those up: on every `checkmk export_rules` run the Syncer scans all
rulesets it no longer generates anything for and deletes the rules whose
description starts with its own `cmdbsyncer_<account_id>` marker. Rules created
by hand in Checkmk (without that marker) are never touched. Rules with **Keep manual Value** are removed
here like any other — once a rule is no longer generated there is nothing left
to keep.

## How the Value is compared (removing keys)

On every run the Syncer compares the value it renders with the value stored in
Checkmk. The comparison is deliberately **one-way**: every key the Syncer sets
must be present in Checkmk with the same value, but keys that exist *only* in
Checkmk are accepted. Checkmk enriches saved rule values with the defaults of
the ruleset schema, and treating those additions as a difference would re-write
every rule on every run (endless pending changes).

The consequence: **removing a key from the Value Template is not detected as a
change.** If the previous value was

```python
{'ec2': {'selection': 'all', 'limits': True}}
```

and you change the template to

```python
{'ec2': {'selection': 'all'}}
```

the Syncer still considers the rule up to date and leaves it untouched — it
cannot tell whether `limits` was added by Checkmk as a default or removed by
you. Changing a value (`'all'` → `'tags'`) or adding a key is detected normally
and updated in place.

Writing the key with an "off" value instead of removing it usually does not
work either: many rulesets model an optional setting as a checkbox whose only
allowed content is `True`, so Checkmk rejects the update, for example with

```
Problem in (sub-)field 'servicesec2limits' ... Invalid value, must be 'True' but is 'False'
```

### Enforce exact Value

Enable **Enforce exact Value** on the affected rule to switch that rule to an
exact comparison. Both values then have to carry the same keys, so a key you
removed from the Value Template is written to Checkmk on the next
`checkmk export_rules` run.

Only enable it where you need it. If Checkmk does add schema defaults to that
particular ruleset when saving, the exact comparison never matches again and
the rule is rewritten on **every** run, which leaves permanent pending changes
in Checkmk. If you see that happening, switch the option off again and instead
delete the affected rule once in Checkmk — the next run recreates it from the
current Value Template.

**Keep manual Value** takes precedence: when both are enabled the Value is
never overwritten.

## Rule Order

The Syncer applies the `Folder Index` you configured on each outcome to
the order rules appear in Checkmk. After every
`checkmk export_rules` run the syncer-owned rules in each ruleset are
re-anchored: the first syncer rule keeps its current position
relative to user-created rules around it, and every subsequent rule
is moved to sit directly after the previous one — strictly within
the syncer's own rules.

Important: rules **not** managed by the syncer (i.e. whose description does not
start with the `cmdbsyncer_<account_id>` marker) are never moved. Their
position relative to other user rules is preserved; only their
position relative to the syncer block can shift, because the syncer
rules cluster together once sorted.

If you need a specific top-to-bottom order in a ruleset, just set
the `Folder Index` on each outcome (lower index = higher in the list)
and re-run `checkmk export_rules`.

Every move is one Checkmk write plus a pending change, so the export only
moves the rules that are actually out of place. A ruleset that already has
the configured order sends no request at all. The run says how many moves it
will make before it starts:

```text
 -- Reorder syncer rules
  * 3 rule(s) to move across 2 ruleset(s)
```

If you do not care about the order inside Checkmk at all, set the Checkmk
account custom field `skip_rule_reorder` to `True`. The export then leaves the
Checkmk-side order untouched, which on a ruleset with hundreds of rules is by
far the slowest part of the run.

## Static (host-independent) rules

Most setup rules are calculated per host: the Syncer loops over every
host, renders the templates against that host's attributes and matches
the conditions. When a rule does **not** depend on any host data — its
value, folder and conditions contain no host attributes and resolve to
exactly the same Checkmk rule for every host — that per-host pass is
pure overhead.

Enable **Static Rule** on such a rule. The Syncer then renders it **once**
against an empty context and always creates it, skipping the per-host
calculation entirely. On large inventories this noticeably speeds up
`checkmk export_rules`.

Notes:

- The rule's match conditions (`Condition Type` / conditions) are
  **ignored** for static rules — a static rule is always emitted once.
- Only use it when the templates reference no host attributes. A
  hardcoded **Condition — Host name**, a fixed `Value Template`, or a
  `{% for %}` loop over a literal list are fine; anything reading
  `{{HOSTNAME}}` or other host labels is not.
- **Loop over List** is not supported on static rules (it iterates a host
  attribute list) and is skipped with a log entry.

## Rules from a pasted list

Some rules are not about hosts at all but about a long list of services,
each with its own setting: a service level per service, a contact group
label, a notification period, a number of check attempts. Writing one Setup
Rule per line does not scale, and a host-based rule would have to be
calculated for every host only to produce the same rules again.

Set **Rule source** of the Setup Rule to **From a pasted list** instead.
The form then swaps the host **Conditions** for a **Pasted List** step and
hides **Static Rule**: a list rule is always host-independent, the hosts
play no part in it. Switching back to **Per host** keeps the pasted text
but no longer uses it.

Paste the list into the **List Source** field. The rule then works through
the list, not through the hosts:

- The **first line names the columns**. Every column becomes a Jinja
  variable: the header is lower cased and everything that is not a letter,
  digit or underscore becomes `_`, so `Service Level` is
  `{{ service_level }}`. The whole row is also available as `{{ row }}`
  (for example `{{ row.service_level }}`) and its 0-based position as
  `{{ row_idx }}`.
- The separator is detected from the first line: tab (what a block copied
  out of a spreadsheet arrives as), semicolon, comma or `|`. Cells in double
  quotes may contain the separator and line breaks.
- Empty lines are skipped. A header cell left empty drops its column, so a
  trailing separator does no harm. A line with more cells than the header
  is an error.
- While you paste or type, the form shows below the field:
  - the number of rows and the detected separator,
  - the **column variables** exactly as you write them, e.g.
    `{{ service_name }}` and `{{ level }}`. Click into an outcome field
    (Value, a condition, ...) and then on a variable to insert it there,
  - a table of the first 20 rows under those variable names,
  - every problem, with its line and cell, e.g. a line with a cell more
    than the header has columns (usually a wrong separator or a cell that
    needs quotes),
  - every outcome field reading a variable that is no column of the list,
    e.g. a typo like `{{ levl }}`: it would render empty, so those rows would
    create no rule.

  A list with a problem cannot be saved; an unknown variable is only a
  warning.

Every outcome of the rule is rendered **once per row**. All outcome fields
(Value, Folder, conditions, Loop over List) see the columns of that row.

- A row whose **Value**, **Condition: Service name** or **Condition: Host
  name** renders empty creates **no** rule for that outcome. Without the
  condition the rule would apply to every service or host, without a Value
  it would be no rule at all. So a column that is only filled for some
  services simply leaves the other rows out.
- Rows that render to the **same rule except for the service name** are
  joined into one Checkmk rule matching all of their services. A list of a
  hundred services in three service levels creates three rules, not a
  hundred. The joined rule keeps the position of its first row.
- **Loop over List** works on list rules: give a column name (or Jinja) and
  a cell holding several entries, e.g. `ops,db`, creates one rule per entry,
  with `{{ loop }}` next to the columns of the row.
- Put the hosts into **Condition: Host name** of the outcome if the rules
  should only apply to some hosts, either fixed or from a column.

Checkmk compares service names as regular expressions that match the
beginning of the name. Add `$` to match a name exactly, e.g. `{{ service }}$`,
and escape characters like `(` or `.` in the list if a name contains them.

Changing the list works like changing any other rule: the next
`checkmk export_rules` creates the rules of new rows, updates changed ones
and removes the rules this Setup Rule created for rows that are gone. Rules
the Syncer did not create are never touched. Run
`checkmk export_rules <account> --dry-run` first to see exactly what would
change, values included.

### Example

One Setup Rule per ruleset, each with Rule source **From a pasted list** and the same list:

```
service;level;team;max_attempts
Disk C:;20;ops;
CPU load;10;ops;5
Memory;10;db;5
Interface 1;;ops;
```

| Ruleset | Value | Condition: Service name | other |
| :------ | :---- | :---------------------- | :---- |
| `extra_service_conf:_ec_sl` | `{{ level }}` | `{{ service }}$` | |
| `extra_service_conf:max_check_attempts` | `{{ max_attempts }}` | `{{ service }}$` | |
| `service_label_rules` | `{'team': '{{ team }}'}` | `{{ service }}$` | |
| `service_contactgroups` | `'{{ team }}'` | | Condition: Service label `team:{{ team }}` |

This creates two service level rules (`Disk C:` with level 20, `CPU load`
and `Memory` together with level 10; `Interface 1` has no level), one check
attempts rule for `CPU load` and `Memory`, one label rule per team, and one
contact group rule per team that matches the services by their label.

## Ruleset Autocomplete

The **Ruleset** field on the edit form has a searchable picker over every
internal ruleset of Checkmk 2.4 and 2.5. Start typing to search — matches are
found both by the ruleset **ID** (e.g. `checkgroup_parameters:filesystem`) and
by its plain-language **name** ("File systems (used space and growth)"). Each
suggestion shows which Checkmk version(s) it belongs to, so version-specific
rulesets are easy to spot. Free text stays possible — the picker only suggests.

Rulesets that ship an example are marked with a `★`. When you pick one, its
example is shown below the field together with an **Apply example to Value
Template** button — click it to fill the Value Template. If that field already
holds something different, the Syncer asks before overwriting it.

The suggestion list is data-driven and lives in JSON files under
`application/plugins/checkmk/data/`:

- `rulesets_<version>.json` — the ruleset catalog per Checkmk version.
  Regenerate or add a version by running
  `cmdbsyncer checkmk export_rulesets <account>` against a Checkmk of that
  version; the file is named automatically from the probed version.
- `ruleset_examples.json` — the example Value Templates, keyed by ruleset ID.
  Add entries here to grow the pre-fill suggestions — no code change needed.

## Finding the Ruleset ID and Value Format

The easiest way to find the correct ruleset ID and the expected JSON value format is to:

1. Create an example rule in Checkmk manually
2. Open the Checkmk Swagger API documentation
3. Look up the rule via the API and copy the JSON value

See [Manage Contact Groups](recipe_contact_groups.md) for a full step-by-step example of this workflow.

## Full Example

- [Manage Contact Groups](recipe_contact_groups.md) — full walkthrough including group creation and assignment rule setup
- [Create Checkmk Rules Automatically](recipe_checkmk_rules.md) — example with active check rules
