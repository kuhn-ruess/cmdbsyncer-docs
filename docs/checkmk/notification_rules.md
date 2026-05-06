# Notification Rules

The Notification Rules feature creates Checkmk notification rules from host attributes. Each rule template is rendered against every matching host's attributes, identical bodies are de-duplicated, and the resulting set is reconciled with what Checkmk currently has.

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

## Rule Parameters

Conditions on the rule itself filter which hosts the outcomes are evaluated for — same `FullCondition` mechanism as in Setup Rules.

Each outcome turns into one notification rule per matching host (after dedup). All template fields support Jinja and have access to the host's attributes; an empty field disables the corresponding condition.

### Notification Method

Free-text plugin name with autocomplete suggestions for the built-in Checkmk plugins (`mail`, `asciimail`, `slack`, `msteams`, `pagerduty`, …). You can type any custom plugin name — useful for site-local notification scripts.

### Recipients

| Option                          | Description                                                                                  |
| :------------------------------ | :------------------------------------------------------------------------------------------- |
| Contact Group Recipients        | Jinja, comma-separated CG names that receive the notification. **Required.**                 |

If `Contact Group Recipients` renders empty for a host, no rule is generated.

### Match: Event Types

Multi-select with human-readable labels. Pick zero or more transitions per outcome. Empty selection disables the condition.

| Field                    | Examples                                          |
| :----------------------- | :------------------------------------------------ |
| Match Host Event Types   | "Host: UP → DOWN", "Host: DOWN → UP", "Acknowledgement of problem" |
| Match Service Event Types| "Service: OK → CRIT", "Service: WARN → CRIT", "Start of flapping state" |

### Match: Other Conditions

All as Jinja-rendered strings. Empty disables the condition.

| Field                          | Format                                          |
| :----------------------------- | :---------------------------------------------- |
| Match Contact Groups           | Comma-separated CG names                        |
| Match Host Groups              | Comma-separated host group names                |
| Match Service Groups           | Comma-separated service group names             |
| Match Sites                    | Comma-separated site IDs                        |
| Match Folder                   | Single folder path (subfolders matched)         |
| Match Hosts / Exclude Hosts    | Comma-separated host names                      |
| Match Services / Exclude Services | Comma-separated service descriptions / regex |
| Match Host Labels              | Comma-separated `key:value` pairs               |
| Match Service Labels           | Comma-separated `key:value` pairs               |
| Match Host Tags                | Comma-separated `tag_group:tag_id` pairs        |
| Match Check Types              | Comma-separated check plugin names              |
| Match Plugin Output            | Regex against service plugin output             |
| Match Time Period              | Single time period name                         |
| Match Service Levels           | Range `min,max` (numeric)                       |
| Match Contacts                 | Comma-separated user IDs                        |

### Disable Rule

Mark the resulting rule as disabled in Checkmk.

## Example: Forward to a `<group>_ALARM` Recipient

Two rules per existing contact group: one for service notifications, one for host problems. Both match on the original contact group and forward to `<group>_ALARM`.

Set the rule's `conditions` to filter the hosts you want this to apply to (e.g. only managed hosts), then add two outcomes:

**Outcome 1 — Service alarms**

- Notification Method: `mail`
- Match Contact Groups: `{{cmk_contact_group}}`
- Match Service Event Types: select "Service: OK → WARN", "Service: OK → CRIT", "Service: WARN → CRIT", "Service: WARN → UNKNOWN", "Service: CRIT → UNKNOWN"
- Contact Group Recipients: `{{cmk_contact_group}}_ALARM`

**Outcome 2 — Host problems**

- Notification Method: `mail`
- Match Contact Groups: `{{cmk_contact_group}}`
- Match Host Event Types: select "Host: UP → DOWN", "Host: UP → UNREACHABLE"
- Contact Group Recipients: `{{cmk_contact_group}}_ALARM`

Run:

```bash
./cmdbsyncer checkmk export_notifications SITEACCOUNT
```

The Syncer iterates all matching hosts, renders both outcomes for each, dedups by body and pushes the resulting set to Checkmk. Activate Changes is **not** triggered automatically — run it explicitly when you are ready.
