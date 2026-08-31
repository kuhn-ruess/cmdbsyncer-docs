# Manage Checkmk Setup Rules

The Syncer can create, update, and delete Checkmk setup rules automatically — for example threshold rules, active check configurations, or contact group assignments. Rules are created for specific hosts based on their attributes, and deleted again when the conditions no longer apply.

Go to: _Modules → Checkmk → Create Checkmk Setup Rules_

## Configuration Options

| Option                   | Description                                                                           |
| :----------------------- | :------------------------------------------------------------------------------------ |
| Ruleset                  | Checkmk ruleset ID (autocompletes from the known 2.4/2.5 rulesets — see below)        |
| Folder                   | Target folder in Checkmk (Jinja supported)                                            |
| Folder Index             | Position of the rule within the folder                                                |
| Comment                  | Rule comment                                                                          |
| Value Template           | Jinja template for the rule value (check Checkmk Swagger API for the expected format) |
| Keep manual Value        | Write the Value only once (on rule creation) and never overwrite it afterwards, so it can be adjusted in Checkmk. A hint is added to the rule description and comment. |
| Enforce exact Value      | Compare the Value exactly, so entries removed from the Value Template are applied too (see below) |
| Condition Label Template | Syntax: `label:value`. Jinja supported. `{{HOSTNAME}}` available.                     |
| Condition Host           | Comma-separated list of hostnames. Jinja supported including `{{HOSTNAME}}`.          |

If a syncer-owned rule is found in a folder other than the one configured
here, the export moves it to the configured folder on the next run instead
of leaving the misplaced copy behind.

!!! tip
    A rule using **Condition Host** with `{{HOSTNAME}}` ends up as one Checkmk
    rule listing every matching host — on a large installation that means
    hundreds of hostnames in one condition.
    [Rule Optimization](rule_optimization.md) finds those rules and the host
    label that covers exactly the same hosts, and can switch them over for you.
    It is linked above the rule list.

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

The Syncer applies your configured `Folder Index` (and the rule's
`Sort Field`) to the order rules appear in Checkmk. After every
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
the `Folder Index` on each `RuleMngmtOutcome` (lower index = higher
in the list) and re-run `checkmk export_rules`.

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

Enable **Static** on such a rule. The Syncer then renders it **once**
against an empty context and always creates it, skipping the per-host
calculation entirely. On large inventories this noticeably speeds up
`checkmk export_rules`.

Notes:

- The rule's match conditions (`Condition Type` / conditions) are
  **ignored** for static rules — a static rule is always emitted once.
- Only use it when the templates reference no host attributes. A
  hardcoded `Condition Host`, a fixed `Value Template`, or a
  `{% for %}` loop over a literal list are fine; anything reading
  `{{HOSTNAME}}` or other host labels is not.
- `Loop over list` is not supported on static rules (it iterates a host
  attribute list) and is skipped with a log entry.

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
