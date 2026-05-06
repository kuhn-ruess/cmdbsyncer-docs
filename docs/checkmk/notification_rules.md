# Notification Rules

The Notification Rules feature creates Checkmk notification rules from host attributes. Each outcome is rendered against every matching host's attributes, identical bodies are de-duplicated, and the resulting set is reconciled with what Checkmk currently has.

Go to: _Modules → Checkmk → Manage Notification Rules_

!!! note
    Requires Checkmk 2.4 or 2.5. Older versions are rejected at runtime.

## How Identification Works

Every rule the Syncer creates carries the description `cmdbsyncer_<account_id> - DO NOT EDIT`. On every run the Syncer:

- fetches all notification rules whose description starts with `cmdbsyncer_<account_id>`
- compares each rule's full body against the configured outcomes
- creates rules that are missing in Checkmk
- deletes rules in Checkmk that no configured outcome produces any more

A manual edit to one of the Syncer's rules in Checkmk is detected on the next run because the body no longer matches what the Syncer would render — the rule is removed and re-created with the configured values. Do not edit them by hand.

The Syncer never touches notification rules that are not labelled with its description marker. Rules created manually in Checkmk are left alone.

## How Per-Host Rules Become Per-Value Rules

The sync runs host by host. For each host it reads the host's attributes, renders every outcome against them, and produces one rule body. Identical bodies across many hosts collapse into one rule via dedup.

That is why a label that already carries its target value per host (e.g. one host has `anwendung_kontaktgruppe=app_billing`, another has `app_invoicing`) does not need any loop construct: the values reach Checkmk one rule per distinct rendered body, just because each host contributes its own value through the normal iteration.

## Rule Parameters

Top-level conditions on the rule itself filter which hosts the outcomes are evaluated for — same `FullCondition` mechanism as in Setup Rules.

Each outcome below is rendered once per matching host. All template fields support Jinja and have access to the host's attributes; an empty field disables the corresponding filter.

### Notification Method

Free-text plugin name with autocomplete suggestions for the built-in Checkmk plugins (`mail`, `asciimail`, `slack`, `msteams`, `pagerduty`, …). You can type any custom plugin name — useful for site-local notification scripts.

### Contact Group Recipients

Jinja-rendered, comma-separated list of contact group names that should receive the notification. **Required.** If it renders empty (or only the literal `_ALARM` because the source label is missing on the host), no rule is generated.

### Filter Host / Service Event Types

Multi-select shown as a checkbox list per event-type group. Pick any number of transitions; empty selection disables the filter. Typical entries:

- Host event types: "Host: UP → DOWN", "Host: UP → UNREACHABLE", "Acknowledgement of problem", "Start of flapping state"
- Service event types: "Service: OK → CRIT", "Service: WARN → CRIT", "Service: any → CRIT"

### Other Filters

All Jinja-rendered. Empty disables the filter.

| Field                          | Format                                          |
| :----------------------------- | :---------------------------------------------- |
| Filter Contact Groups          | Comma-separated CG names                        |
| Filter Host Groups             | Comma-separated host group names                |
| Filter Service Groups          | Comma-separated service group names             |
| Filter Sites                   | Comma-separated site IDs                        |
| Filter Folder                  | Single folder path (subfolders matched)         |
| Filter Hosts / Exclude Hosts   | Comma-separated host names                      |
| Filter Services / Exclude Services | Comma-separated service descriptions / regex |
| Filter Host Labels             | Comma-separated `key:value` pairs               |
| Filter Service Labels          | Comma-separated `key:value` pairs               |
| Filter Host Tags               | Comma-separated `tag_group:tag_id` pairs        |
| Filter Check Types             | Comma-separated check plugin names              |
| Filter Plugin Output           | Regex against service plugin output             |
| Filter Time Period             | Single time period name                         |
| Filter Service Levels          | Range `min,max` (numeric)                       |
| Filter Contacts                | Comma-separated user IDs                        |

If `Filter Contact Groups` is set on an outcome but renders empty for a host (the host is missing the source label), the outcome is silently skipped for that host — no nonsense rule with an empty CG match is sent to Checkmk.

### Disable Rule

Mark the resulting rule as disabled in Checkmk.

## Example: Forward Per Contact Group to its `_ALARM` Variant

Premise: hosts carry an `anwendung_kontaktgruppe` label with the application contact group they belong to. The Group Sync already creates `<group>` and `<group>_ALARM` contact groups in Checkmk.

Goal: each `<group>` triggers notifications, but the recipients are the members of `<group>_ALARM`. Service notifications fire only on critical transitions, host notifications fire on every host problem regardless of service state.

Two outcomes on the same rule:

**Outcome 1 — Service alarms**

- Notification Method: `mail`
- Filter Contact Groups: `{{ anwendung_kontaktgruppe }}`
- Filter Service Event Types: tick "Service: OK → CRIT", "Service: WARN → CRIT", "Service: UNKNOWN → CRIT"
- Contact Group Recipients: `{{ anwendung_kontaktgruppe }}_ALARM`

**Outcome 2 — Host problems**

- Notification Method: `mail`
- Filter Contact Groups: `{{ anwendung_kontaktgruppe }}`
- Filter Host Event Types: tick "Host: UP → DOWN", "Host: UP → UNREACHABLE", "Host: DOWN → UNREACHABLE", "Host: UNREACHABLE → DOWN"
- Contact Group Recipients: `{{ anwendung_kontaktgruppe }}_ALARM`

Run:

```bash
./cmdbsyncer checkmk export_notifications SITEACCOUNT
```

The Syncer iterates all hosts, renders both outcomes for each, dedups by body, and pushes the resulting set to Checkmk. With N distinct contact-group values across the hosts you get 2 × N rules. Activate Changes is **not** triggered automatically — run it explicitly when you are ready.
