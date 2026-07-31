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
