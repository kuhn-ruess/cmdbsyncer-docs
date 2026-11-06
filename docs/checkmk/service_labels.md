# Service Labels

<span class="since">Since 4.5</span>

Set labels on Checkmk services from rules in the Syncer, including a value which is rebuilt from the label a check plugin reports. The rules read the services and their labels from the hosts in the Syncer and write the result to the Checkmk ruleset _Service labels_.

Go to: _Modules → Checkmk → Manage Service Labels_

## How It Works

1. [Inventorize](inventorize.md) reads the services of a host and their labels into the host in the Syncer. Use the source **Labels per Service** with a regular expression for the service names.
1. A rule says: on a host matching the conditions, set this label on the services matching this pattern.
1. `export_service_labels` creates the rules in Checkmk. Services ending up with the same labels share one rule, and hosts with the same services and labels as well.
1. Activate the changes, for example with the cron job `Checkmk: Activate Changes`.

A service known from the inventory gets a rule of its own, computed from its `LABELS` and `MATCH`. A service without any label is known as well, and a rule can give it one.

A Service Pattern hitting no known service, for example before the first Inventorize, goes to Checkmk as it is, with the value computed from the host alone. A value that needs `LABELS` or `MATCH` usually renders empty then and is not sent until Inventorize has read the service. Once a pattern hits known services, their rules take its place. Patterns of a host with the same folder and the same labels share one rule, unless a rule between them sets one of these labels to another value: in Checkmk the first rule wins per label, so the order has to stay.

## Configuration

Conditions work on the host, as in every other rule. To select hosts by the labels found on their services, use the attribute of the source **Labels per Service**: Match for Attribute, _Tag_ `cmk_svc_label_list__services`, _Tag Match_ `Exact Match`, and a _Value Match_ on it, `Contains` or `Regular Expression`. The attribute holds one entry per service with the labels of that service.

Each outcome of a rule has these fields:

| Field           | Description                                                                                                    |
| :-------------- | :------------------------------------------------------------------------------------------------------------- |
| Service Pattern | Regular expression on the service name, with groups for `MATCH`. It is searched, so anchor it with `^` and `$` |
| Label Name      | Name of the label to set (Jinja)                                                                               |
| Label Value     | The new value (Jinja). An empty result sets nothing                                                            |
| Folder          | Checkmk folder of the created rule (Jinja, default `/`). `{{ HOST_FOLDER }}` is available                      |

One outcome covers every service its pattern matches, so `^(Port|Fan)` puts the label on all of them, each with its own rendered value. For another label or value, add a further outcome.

A service without the label is no problem: in the template it is simply empty, so `{{ LABELS.my_label }}` renders nothing and the service gets no rule. Other services and hosts go on. Calling a function on the missing label fails and is logged instead, so give it a default: `LABELS.my_label|default('')`.

Rules are worked through by their sort field. Per service and label the first non empty value counts, so a special case is a rule in front of the general one, and a template which renders empty leaves the label to the next rule.

These variables are available in the templates:

| Variable   | Content                                                                          |
| :--------- | :------------------------------------------------------------------------------- |
| `HOSTNAME` | Name of the host                                                                 |
| `SERVICE`  | Name of the service                                                              |
| `MATCH`    | What the pattern matched: `MATCH[0]` all of it, `MATCH[1]` the first group       |
| `LABELS`   | Labels of the service as of the last Inventorize: `LABELS.my_label`              |
| Attributes | Every attribute of the host under its own name, and `lookup()` for Lookup Tables |

## Example: Repair a Name

A device plugin reports the names of the units attached to a device as label `raw_name`, for example `e-s05-a` on the port services of `rack-x-dc1-s04-b`. The services should also carry `display_name` with `rack-x-dc1-s05-a`: the first part has to be replaced with the first three parts of the host name. The rule should only act where one of the two labels is missing.

Inventorize, source **Labels per Service**:

```text
^Port
```

Rule conditions, with `Any condition can match`, the first for a service with only the raw name, the second for one with only the display name:

```text
Tag:         cmk_svc_label_list__services
Tag Match:   Exact Match
Value Match: Regular Expression
Value:       .*\{(?![^}]*display_name)[^}]*raw_name
```

```text
Tag:         cmk_svc_label_list__services
Tag Match:   Exact Match
Value Match: Regular Expression
Value:       .*\{(?![^}]*raw_name)[^}]*display_name
```

Outcome:

```text
Service Pattern: ^Port \d+$
Label Name:      display_name
Label Value:     {% set l = LABELS.raw_name|default(LABELS.display_name|default('')) %}{% if l.startswith('e-') %}{{ HOSTNAME.split('-')[:3]|join('-') }}-{{ l[2:] }}{% else %}{{ l }}{% endif %}
```

Build the value from a label no rule writes, here `raw_name`, or leave a value already repaired as it is, as the `else` above does: Checkmk reports the value of a rule as the label of the service, so the next Inventorize reads it back. A value rebuilt from itself would grow with every run.

Further labels work the same way, for example a room from a [Lookup Table](../basics/lookup_tables.md):

```text
Service Pattern: ^Port
Label Name:      room
Label Value:     {{ lookup('rooms', HOSTNAME.split('-')[3][:1]) }}
```

## Debug

Go to: the tab _Debug_ of a host, Target _Checkmk Host_. The card **Service Labels** debugs the rules: for each rule whose conditions match this host, it lists what the rule sends to Checkmk, with the service or regex, the label name and the value.

```text
Service or regex   Label  Value
Port 1             room   rack-u1
Port 2             room   rack-u1
^Fan               room   rack-u1
```

If services of the host are known from the source **Labels per Service**, a regex hitting them gets one row per service and label, computed from the service's `LABELS` and `MATCH`. A regex without a known service is computed from the host alone, with `SERVICE`, `MATCH` and `LABELS` empty, and the export sends it just like that.

A label whose value renders empty is not sent to Checkmk, so it is not on the card either. A template or Service Pattern that fails shows its error text as the value. As in the export, the first value of a label wins. If no rule matches the host, or the matching rules send no label, the card says so in one line.

The card does not contact Checkmk and leaves out rules whose conditions don't match, so a label [kept by a written rule](#when-a-rule-stays-and-when-it-goes) is not on it. The tab _Service Label Rules_ under **Rules** shows why the conditions of a rule match the host or not.

## When a Rule Stays and When It Goes

The condition of a rule decides where a label is written, not how long the rule stays in Checkmk. In the example both labels are there once the rule is active, so the host stops matching. That must not remove the rule: the label would be gone, the host would match again, and the labels would change with every run.

So the rule of a known service stays untouched in Checkmk as long as its host is exported and an enabled rule in the Syncer, whatever its conditions say, still renders exactly that value for that service. A rule written from a pattern only stays while the conditions match. The rule of a known service is removed when:

- the host is no longer in the Syncer, or the service is gone
- no enabled rule renders the value any more: the rule is disabled or deleted, or the template changed
- the value would be a different one, for example because the raw name changed on the device after "Update service labels". After the next activation and Inventorize the label is missing, the condition matches and the new value is written

A rule deleted by hand in Checkmk comes back through the condition as well: the label is missing after the next Inventorize. To take a label off a single host for good, narrowing the condition is not enough, as the rule stays. Narrow the condition and delete the rule in Checkmk.

## Ownership

The rules in Checkmk carry the description `cmdbsyncer_<account id>_service_labels`. The export only changes and removes rules with this mark. Rules created by hand, by another account or by the [Setup Rules](rules_management.md) export are left alone, and the other way round. See [above](#when-a-rule-stays-and-when-it-goes) for what removes a rule.

Per label, Checkmk uses the first rule that matches, so a rule from another source can win over the exported one. Rules in deeper folders come first, within a folder the order of the rule list counts.

## Command Line

```bash
./cmdbsyncer checkmk export_service_labels ACCOUNTNAME --dry-run
./cmdbsyncer checkmk export_service_labels ACCOUNTNAME
```

`--dry-run` still reads Checkmk, shows every rule it would create, change or delete with its value, and sends nothing. The cron job is called `Checkmk: Export Service Labels`, and it goes behind `Checkmk: Inventorize`. The export takes hosts, not objects, as only hosts have services in Checkmk. The setting `filter` for `Checkmk: Export Service Labels` on the account selects other object types instead.
