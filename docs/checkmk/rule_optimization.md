# Rule Optimization
<span class="since">Since 4.3</span>

When a Setup Rule outcome matches on **Condition Host** with `{{HOSTNAME}}` and
nothing else, the rule says "this applies to this host". The Syncer merges every
matching host into **one** Checkmk rule whose condition lists every hostname.

On a large installation that produces rules naming hundreds of hosts:

- they are hard to read in Checkmk,
- Checkmk is slower at matching them,
- and the Syncer has to rewrite the rule whenever a single host joins or leaves
  it, so every export churns.

Usually those hosts already share an attribute. Rule Optimization finds which
one, and can switch the rule over to a label condition — same hosts, one short
condition, and the rule stops moving when the host set changes.

## In the web interface

Go to: _Modules → Checkmk → Create Checkmk Setup Rules_ and click
**Rule Optimization** above the list.

Pick a scope and press **Run analysis**. The analysis renders every rule for
every host and then walks the hosts again to count attribute coverage, which is
far too slow for a web request — so it runs in the background. The page refreshes
itself every ten seconds while a run is in flight and stops once it is done.

Each finding is one card: the Setup Rule, how many hosts end up in its condition,
and the attributes that could replace the host list.

The **Apply** button on a finding writes the change straight into the Setup Rule.
Findings are applied one at a time, and a finding disappears from the list once
it has been applied — it described the rule as it was.

!!! note
    The result is a snapshot from when the analysis ran. If you changed rules or
    imported hosts since, run it again before applying anything.

## On the command line

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

| Option | Description |
| :----- | :---------- |
| `--min-hosts` | Only report rules built from at least this many hosts (default: 10). |
| `--top` | How many of the largest rules to report (default: 20). |
| `--apply` | Make the change instead of only reporting it. |
| `--hash-labels` | With `--apply`: match on a hash instead of letting raw attribute values through as Checkmk labels. |

The account is optional. Given one, the report is narrowed to what an export of
*that* account would produce: its project scope, its `limit_by_folders` scope and
its object-type filter. Without one, every enabled rule is reported.

The command reads the Syncer database and nothing else — it never changes a rule
without `--apply` and never contacts Checkmk, so it also works while the site is
unreachable. The rule cache is ignored, so the report always judges the rules as
they are configured right now.

## Reading a finding

| Marker | Meaning |
| :----- | :------ |
| `->` | The attribute covers exactly the hosts of the rule. Switching is a straight swap: same hosts, one short condition. |
| `~` (more would get it) | The attribute covers the rule, but additional hosts carry it as well. Switching widens the rule to those hosts. |
| `~` (covers N of M) | No host outside carries it, but it does not reach all hosts of the rule. Those hosts would lose it. |

Only the `->` findings are applied automatically. The `~` findings change *which*
hosts get the rule, so they are yours to decide. A rule condition produced by more
than one Setup Rule is skipped as well — there is no telling which of them to
rewrite. If several attributes are equally exact, the first by name is used and
the report names the alternatives.

Some rulesets are never offered a label condition: a ruleset that assigns host
labels (`host_label_rules`) cannot match on them, so Checkmk would store the rule
**without** the condition and it would apply to every host in the folder. Those
rules are reported as not convertible.

## Where the candidates come from

Every attribute the hosts carry **in the Syncer** — labels, inventory and CMDB
template values alike — not only the ones that are currently exported. They are
shown the way the host export writes them as a Checkmk label.

If the suggested attribute does not pass your export filter, Checkmk never sees
it as a host label. The report says so, and applying lets it through by adding it
to a filter rule named `Syncer: attributes used by rule conditions`.

## Values that cannot be a label

An attribute whose value is a comma-separated list, carries spaces, or is a
wildcard or service pattern cannot be a Checkmk label on its own. It is offered
**hashed** instead — the hash is a valid label value and groups exactly the same
hosts:

```text
   -> in the outcome set Condition Label to roles_hash:3ae68845 and clear Condition Host
      'roles' is no usable label on its own, so roles_hash is a hash of it —
      needs a Rewrite rule adding roles_hash = {{ roles | hash }}
```

Applying creates that Rewrite rule in `Syncer: hashed attributes for rule
conditions`. It adds a *new* attribute rather than renaming, so the original value
stays available to every other rule, and a host that does not carry the source
attribute gets nothing.

With `--hash-labels` no raw attribute value reaches Checkmk at all: an attribute
that would have to be newly let through the filter is matched by a hash of it
instead. Use it when the values are long, noisy or none of Checkmk's business —
the condition still groups exactly the same hosts, the label is just not readable.

The `hash` filter is available in every Jinja template, see
[Rewrite Attributes](../basics/rewrite_attributes.md).

## What applying changes

For each applied finding:

1. the Setup Rule outcome gets the attribute as its **Condition Label Template**,
2. its **Condition Host** is cleared,
3. the attribute is whitelisted in a filter rule if it did not pass the filter,
4. a Rewrite rule is created if the label is a hash,
5. and the cached export data of every host is dropped, exactly as a rule edit in
   the web interface does it.

Nothing is sent to Checkmk. The next export produces the new rule and removes the
old host-list one.

Run the analysis once without applying and read the list first.
