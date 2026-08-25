# Commandline Parameters

Access all Checkmk commands with `./cmdbsyncer checkmk <command> <account>`.

| Command                | Description                                                                    |
| :--------------------- | :----------------------------------------------------------------------------- |
| export_hosts           | Export hosts to the Checkmk instance                                           |
| export_groups          | Create Checkmk groups based on your rules                                      |
| export_rules           | Export Checkmk setup rules to the instance                                     |
| export_tags            | Export host tag group configuration to Checkmk                                 |
| export_users           | Create, update, or disable users in Checkmk                                    |
| export_downtimes       | Export scheduled downtimes to Checkmk                                          |
| export_notifications   | Export notification rules to Checkmk (2.4 / 2.5 only)                          |
| export_dcd_rules       | Export DCD (Dynamic Configuration) rules to Checkmk                            |
| export_bi_aggregations | Export BI aggregation rules to Checkmk                                         |
| export_bi_rules        | Export BI rules to Checkmk                                                     |
| activate_changes       | Activate pending changes on the Checkmk instance                               |
| bake_and_sign_agents   | Bake agents — requires bakery_key_id and bakery_passphrase in account settings |
| import_v2              | Import hosts from Checkmk 2.x into the Syncer                                  |
| import_v1              | Import hosts from Checkmk 1.x into the Syncer                                  |
| inventorize_hosts      | Run inventory to fetch attributes from Checkmk into the Syncer                 |
| show_hosts             | Print all hosts that would be exported to Checkmk                              |
| show_labels            | List all labels that would be set in Checkmk after the sync                    |
| show_missing_hosts     | Show hosts present in Checkmk but not in the Syncer                            |
| assign_template        | Assign a CMDB template to every host of a Checkmk folder (see below)           |
| analyse_rules          | Find Setup Rules whose export lists hundreds of hostnames and suggest a host label (account optional) |

## Improve Setup Rules that name every host individually
<span class="since">Since 4.3</span>

When a Setup Rule outcome uses **Condition Host** with `{{HOSTNAME}}` and no
other condition, the rule applies to "this host" — so the Syncer merges every
matching host into **one** Checkmk rule whose condition lists every hostname. On
a large installation that produces rules naming hundreds of hosts. They are hard
to read in Checkmk, slower to match, and the Syncer has to rewrite them whenever
a single host joins or leaves.

Usually those hosts already share a label, and the rule can use that label
instead. `analyse_rules` finds which one:

```bash
./cmdbsyncer checkmk analyse_rules --min-hosts 50
```

```text
 * Setup Rule Agent Access Prod — 902 hosts end up in one condition
   ruleset: agent_config:only_from   folder: /
   comment: Agent access
   value:   {'only_from': ['10.0.0.1']}
   -> in the outcome set Condition Label to env:prod and clear Condition Host
      — covers all 902 hosts and no other host
   ~  site:hamburg covers all 902 hosts, but 14 more host(s) would get the rule too
   ~  role:web covers 890 of 902 hosts, no other host — 12 would lose the rule
```

The candidates are every attribute the hosts carry **in the Syncer** — labels,
inventory and CMDB template values alike — not only the ones that are currently
exported. They are shown the way the host export writes them as a Checkmk label,
and an attribute that cannot be a single label value is never suggested:
comma-separated lists, values with spaces, wildcards and service patterns. If the suggested attribute does not pass your export filter, Checkmk
never sees it as a host label, and the report says so:

```text
   -> in the outcome set Condition Label to env:prod and clear Condition Host
      note: 'env' does not pass the export filter, so Checkmk never sees it as a
            host label — add it to the filter rules first
```

The report names the **Setup Rule**, because that is where the change belongs —
open it, and in the outcome set **Condition Label Template** to the suggested
label and clear **Condition Host**.

| Marker | Meaning |
| :----- | :------ |
| `->`   | The label covers exactly the hosts of the rule. Switching is a straight swap: same hosts, one short condition. |
| `~` (more would get it) | The label covers the rule, but additional hosts carry it as well. Switching widens the rule to those hosts. |
| `~` (covers N of M) | No host outside carries the label, but it does not reach all hosts of the rule. Those hosts would lose it. |

If no label comes close, the hosts share nothing the others do not. A
[Rewrite rule](../basics/rewrite_attributes.md) that sets a label on exactly those
hosts gives the Setup Rule something to match on.

| Option | Description |
| :----- | :---------- |
| `--min-hosts` | Only report rules built from at least this many hosts (default: 10). |
| `--top` | How many of the largest rules to report (default: 20). |
| `--apply` | Make the change instead of only reporting it (see below). |

### Applying the findings

```bash
./cmdbsyncer checkmk analyse_rules --min-hosts 50 --apply
```

For every `->` finding this sets the outcome's **Condition Label Template** to
the suggested label, clears its **Condition Host**, and — if the attribute does
not pass the export filter — whitelists it in a filter rule named
`Syncer: attributes used by rule conditions`, so Checkmk actually receives it as
a label. The cached export data of every host is dropped afterwards, exactly as
a rule edit in the web interface does it.

Only the `->` findings are applied. They are a straight swap: the label covers
the hosts of the rule and no others, so the export keeps producing the same rule
for the same hosts. The `~` findings change *which* hosts get the rule, so they
are yours to decide. A rule condition produced by more than one Setup Rule is
skipped as well — there is no telling which of them to rewrite. If several
labels are equally exact, the first by name is used and the report names the
alternatives.

Run it once without `--apply` first and read the list.

The command reads the Syncer database and nothing else — it never changes a rule
and never contacts Checkmk, so it also works while the site is unreachable.

The account is optional. Given one, the report is narrowed to what an export of
*that* account would produce: its project scope, its `limit_by_folders` scope
and its object-type filter. Without one, every enabled rule is reported. The
rule cache is ignored either way, so the report always judges the rules as they
are configured right now.

## Assign a CMDB template from a Checkmk folder
<span class="since">Since 4.3</span>

Unlike the commands above, `assign_template` takes extra arguments — the Checkmk
folder and the template name:

```bash
./cmdbsyncer checkmk assign_template <account> <folder> <template> [--dry-run]
```

It reads the hosts of the given Checkmk folder and assigns the named CMDB template to
each host that exists in the Syncer. Use `--dry-run` to preview which hosts would be
changed without writing anything.

## Debugging

Add `--debug` to any command to raise exceptions and enable verbose logging. Add `--debug-rules=hostname` to inspect rule outcomes for a specific host. See [Debugging](../basics/debug_rules.md) for details.

Add `--dry-run` to simulate an export without making any changes. Add `--save-requests` to write all planned API requests to a file for review.
