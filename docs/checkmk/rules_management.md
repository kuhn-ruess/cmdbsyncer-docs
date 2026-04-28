# Manage Checkmk Setup Rules

The Syncer can create, update, and delete Checkmk setup rules automatically — for example threshold rules, active check configurations, or contact group assignments. Rules are created for specific hosts based on their attributes, and deleted again when the conditions no longer apply.

Go to: _Modules → Checkmk → Create Checkmk Setup Rules_

## Configuration Options

| Option                   | Description                                                                           |
| :----------------------- | :------------------------------------------------------------------------------------ |
| Ruleset                  | Checkmk ruleset ID                                                                    |
| Folder                   | Target folder in Checkmk (Jinja supported)                                            |
| Folder Index             | Position of the rule within the folder                                                |
| Comment                  | Rule comment                                                                          |
| Value Template           | Jinja template for the rule value (check Checkmk Swagger API for the expected format) |
| Condition Label Template | Syntax: `label:value`. Jinja supported. `{{HOSTNAME}}` available.                     |
| Condition Host           | Comma-separated list of hostnames. Jinja supported including `{{HOSTNAME}}`.          |

## Rule Order

The Syncer applies your configured `Folder Index` (and the rule's
`Sort Field`) to the order rules appear in Checkmk. After every
`checkmk export_rules` run the syncer-owned rules in each ruleset are
re-anchored: the first syncer rule keeps its current position
relative to user-created rules around it, and every subsequent rule
is moved to sit directly after the previous one — strictly within
the syncer's own rules.

Important: rules **not** managed by the syncer (i.e. without the
`cmdbsyncer_<account_id>` description marker) are never moved. Their
position relative to other user rules is preserved; only their
position relative to the syncer block can shift, because the syncer
rules cluster together once sorted.

If you need a specific top-to-bottom order in a ruleset, just set
the `Folder Index` on each `RuleMngmtOutcome` (lower index = higher
in the list) and re-run `checkmk export_rules`.

## Finding the Ruleset ID and Value Format

The easiest way to find the correct ruleset ID and the expected JSON value format is to:

1. Create an example rule in Checkmk manually
2. Open the Checkmk Swagger API documentation
3. Look up the rule via the API and copy the JSON value

See [Manage Contact Groups](recipe_contact_groups.md) for a full step-by-step example of this workflow.

## Full Example

- [Manage Contact Groups](recipe_contact_groups.md) — full walkthrough including group creation and assignment rule setup
- [Create Checkmk Rules Automatically](recipe_checkmk_rules.md) — example with active check rules
