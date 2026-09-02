# Notification Rules

The Notification Rules feature creates Checkmk notification rules from host attributes. Each outcome is rendered against every matching host's attributes, identical bodies are de-duplicated, and the resulting set is reconciled with what Checkmk currently has.

Go to: _Modules → Checkmk → Manage Notification Rules_

!!! note
    Requires Checkmk 2.4 or 2.5. Older versions are rejected at runtime.

## How Identification Works

Every rule the Syncer creates carries the description `cmdbsyncer_<account_id> - DO NOT EDIT`. On every run the Syncer:

- fetches all notification rules whose description starts with `cmdbsyncer_<account_id>`
- compares each rule's body against the configured outcomes
- rewrites a rule whose content changed
- creates rules that are missing in Checkmk
- deletes rules in Checkmk that no configured outcome produces any more

A manual edit to one of the Syncer's rules in Checkmk is detected on the next run because the body no longer matches what the Syncer would render — the rule is rewritten with the configured values. Do not edit them by hand.

!!! note
    The notification method is the exception: its parameters belong to Checkmk. The Syncer only sets which plugin a rule uses and leaves everything you configured below it — the notification parameters and the bulking settings — untouched. A rule is therefore updated in place instead of being deleted and created again, which would reset those settings.

    A rule the Syncer creates for the first time is bound by Checkmk to the first notification parameter set of that plugin, because the Checkmk API offers no way to name one. Pick the right parameter set on the rule in Checkmk once — it stays from then on.

The Syncer never touches notification rules that are not labelled with its description marker. Rules created manually in Checkmk are left alone.

## How Per-Host Rules Become Per-Value Rules

The sync runs host by host. For each host it reads the host's attributes, renders every outcome against them, and produces one rule body. Identical bodies across many hosts collapse into one rule via dedup.

That is why a label that already carries its target value per host (e.g. one host has `anwendung_kontaktgruppe=app_billing`, another has `app_invoicing`) does not need any loop construct: the values reach Checkmk one rule per distinct rendered body, just because each host contributes its own value through the normal iteration.

## One Rule per List Entry

That changes when a single host carries *several* values — an attribute like `anwendung_kontaktgruppe=grr00_oracle,grr00_sap`. Without a loop the host produces one rule naming both groups. Switch the outcome to _One Rule per List Entry_ and the Syncer renders the list once and then builds one complete rule per entry.

The current entry is offered to every other field of the outcome as `{{name}}`, so conditions and recipients can be derived from it:

| Field                    | Value                                                                                                            |
| :----------------------- | :--------------------------------------------------------------------------------------------------------------- |
| One Rule per List Entry  | on                                                                                                                |
| List to Loop Over        | `{{get_list(anwendung_kontaktgruppe)|safe}}`                                                                       |
| Filter Contact Groups    | `{{name}}`                                                                                                         |
| Contact Group Recipients | `gro00_cmk_alarm_sms_{{name|replace('grr00_', '')}}, gro00_cmk_alarm_email_{{name|replace('grr00_', '')}}`         |

For a host carrying `grr00_oracle,grr00_sap` that yields two rules: one matching contact group `grr00_oracle` and notifying `gro00_cmk_alarm_sms_oracle` and `gro00_cmk_alarm_email_oracle`, and the same for `grr00_sap`.

The _List to Loop Over_ field takes any Jinja that renders to a list. Use the `get_list()` helper with `|safe` — it accepts a real list, a Python list literal, and a comma-separated string alike, and an attribute a host does not carry counts as an empty list, so looping over two of them needs no guard:

```jinja
{{get_list(anwendung_kontaktgruppe)|safe}}
{{get_list(['grr00_oracle', 'grr00_sap'])|safe}}
```

An empty list produces no rule for that host. Rules that several hosts render identically still collapse into one, as everywhere else.

## Rule Parameters

Top-level conditions on the rule itself filter which hosts the outcomes are evaluated for — same `FullCondition` mechanism as in Setup Rules.

Each outcome below is rendered once per matching host. All template fields support Jinja and have access to the host's attributes; an empty field disables the corresponding filter.

### Notification Method

Free-text plug-in name with autocomplete suggestions for the built-in Checkmk plug-ins (`mail`, `asciimail`, `slack`, `msteams`, `pagerduty`, …). You can type any other name — a site-local or third-party notification script.

Checkmk takes a plug-in it ships and everything else through different options of its API, and the Syncer picks the right one for you. A built-in plug-in keeps the notification parameters you configured for it in Checkmk; anything else is pushed as a custom plug-in with the parameters from the field below.

!!! note
    The plug-in must exist in the target site (`local/share/check_mk/notifications/`). Checkmk rejects a name it does not find there with `<name> does not exist`.

**Read from Checkmk**: the button above the outcomes fills the suggestion list from a site. Checkmk's API has no endpoint listing the installed plug-ins, so what you get is the names the notification rules on that site already use — which is where a third-party plug-in shows up — plus the built-in ones.

### Custom Plug-in Parameters

Only for a method Checkmk does not ship. Built-in plug-ins ignore the field — their parameters live in Checkmk. Jinja-rendered, and there are two shapes because Checkmk expects two:

| Your plug-in | Write | Sent as |
| :----------- | :---- | :------ |
| brings its own configuration mask, like the built-in ones | a dict, e.g. `{"webhook_url": "https://…", "channel": "{{ cmk_contact_group }}"}` | its own fields next to the plug-in name |
| is a plain notification script | a comma-separated list, e.g. `https://hook, {{ cmk_contact_group }}` | the positional parameter list the script is called with |

Anything starting with `{` is read as a dict, anything starting with `[` as a list (JSON or Python literal); everything else is split on commas. An empty field sends the plug-in name alone — which of the two shapes it should mean cannot be guessed, and a wrong guess is not harmless: a list sent to a plug-in with its own configuration makes Checkmk 2.4 answer `Internal Server Error / KeyError: 'params'` and 2.5 reject the request. A script that really takes no parameter is written as `[]`.

#### Using a notification configuration that already exists

A rule cannot point at one of the notification configurations you created in Checkmk: its API has no field for their id, and sending one is rejected. It binds to the configuration whose parameters it **repeats** — enter the same values and the rule lands on your existing configuration; enter different ones and Checkmk stores a copy next to it, named `Auto-generated during rule creation via the REST API`.

**Parameter template**: the second button above the outcomes does that lookup for you. It fills an empty parameter field with the parameters of the first configuration that exists for the plug-in on the chosen site, and names it in the status line. Only when there is none does it fall back to the empty skeleton the plug-in declares — useful in itself, because Checkmk rejects a missing field with `A required (sub-)field is missing.` and never says which one.

A secret cannot be read back: Checkmk hands out an existing password encrypted, so the placeholder stays for you to fill in. Everything else, the password id included, is kept — that is what decides whether the rule matches the configuration. A password from the Checkmk password store carries no secret at all and is repeated as it is, so those match without any further input.

The field names in the dict are the ones the plug-in declares in its own ruleset. A `Password` field does not take a plain string — Checkmk wants the shape it stores on disk:

```json
{
  "api_host": "https://eagle.example",
  "api_token": ["cmk_postprocessed", "explicit_password", ["syncer", "{{ACCOUNT:sms-eagle:password}}"]],
  "ssl_verify": false
}
```

Keep the secret on an Account and pull it in with `{{ACCOUNT:<account>:password}}` as above, so it is not stored in clear text on the rule. A password from the Checkmk password store is referenced instead of inlined:

```json
{"api_token": ["cmk_postprocessed", "stored_password", ["{{ cmk_password('sms-eagle') }}", ""]]}
```

!!! note
    The stored-password variant needs the password to exist in the target site — export it with `checkmk export_passwords` first. Checkmk 2.4 rejects an unknown store id, 2.5 accepts it and fails later.

Unlike the parameters of a built-in plug-in, these belong to the Syncer: change them here and the next run rewrites the rule in Checkmk.

### One Rule per List Entry / List to Loop Over

Build one rule per entry of a list instead of one rule per host, with the entry available to every other field as `{{name}}`. See [One Rule per List Entry](#one-rule-per-list-entry) above.

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

If `Filter Contact Groups` is set on an outcome but renders empty for a host (the host is missing the source label), the outcome is skipped for that host — no nonsense rule with an empty CG match is sent to Checkmk. The run reports how many hosts that affected, see [Nothing Was Exported](#nothing-was-exported-what-now).

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

Add `--dry-run` to see which rules would be created, updated or deleted without sending anything to Checkmk:

```bash
./cmdbsyncer checkmk export_notifications SITEACCOUNT --dry-run
```

The Syncer iterates all hosts, renders both outcomes for each, dedups by body, and pushes the resulting set to Checkmk. With N distinct contact-group values across the hosts you get 2 × N rules. Activate Changes is **not** triggered automatically — run it explicitly when you are ready.

## Nothing Was Exported — What Now?

Every template field is Jinja, and a template that does not compile renders to an empty string. An outcome without recipients is dropped, so a single typo can cost you the whole rule. Three things make that visible:

**1. The form rejects broken Jinja.** Saving a rule whose field does not compile shows the field name and the parser error, and keeps you on the form.

**2. The export checks all templates before it starts:**

```
Check Rule Templates
 !! App Alarm: field 'multiply_list' is not valid Jinja: expected token 'end of print statement', got '.'
```

**3. Hosts that produce no rule say why:**

```
Build needed Notification Rules
 -- 0 rule(s) configured
 !! 214 outcome(s) skipped: loop list rendered empty (e.g. srv001, srv002, srv003)
 !! 12 outcome(s) skipped: no contact group recipients rendered (e.g. srv100)
```

The common reasons:

| Message | Meaning |
| :------ | :------ |
| loop list rendered empty | "List to Loop Over" produced nothing — the attribute is missing or empty on those hosts |
| loop list render error | The loop template raised at render time |
| no contact group recipients rendered | "Contact Group Recipients" rendered empty; the rule would notify nobody |
| contact group filter rendered empty | "Filter Contact Groups" is set but renders empty on that host |
| render error | A match field raised at render time |

All of these also land in the Log view of the run, together with the sample host names.
