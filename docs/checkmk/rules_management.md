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

## Finding the Ruleset ID and Value Format

The easiest way to find the correct ruleset ID and the expected JSON value format is to:

1. Create an example rule in Checkmk manually
2. Open the Checkmk Swagger API documentation
3. Look up the rule via the API and copy the JSON value

See [Manage Contact Groups](recipe_contact_groups.md) for a full step-by-step example of this workflow.

## Full Example

- [Manage Contact Groups](recipe_contact_groups.md) — full walkthrough including group creation and assignment rule setup
- [Create Checkmk Rules Automatically](recipe_checkmk_rules.md) — example with active check rules
