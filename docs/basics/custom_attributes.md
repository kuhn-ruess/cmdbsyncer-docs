# Custom Attributes

No data source is perfect. CMDBsyncer lets you enrich your hosts with additional attributes using rule-based assignments — independent of what the source provides.

Custom Attribute rules are the first rule type applied and work globally across all modules.

Go to: _Modules → Syncer Rules → Custom Attributes_

A rule consists of a [Condition](conditions.md) and an outcome:

- **Attribute Name** — the name of the new or existing attribute to set
- **Attribute Value** — the value to assign

## The Rule List: Grouped by Attribute

Since version 4.5 the list of Global Custom Attributes groups the rules by the
attribute they set: all rules that set `site` stand under the heading `site`,
all rules that set `owner` under `owner`. A rule that sets several attributes
forms a group of that combination: a rule that sets `site` and `owner` stands
under the heading `owner + site`, together with every other rule that sets
exactly these two attributes (in whatever order the rule lists them). Every
rule appears exactly once, a rule without an attribute under _No new
attribute_.

The grouping is only a view. The rules still run in the order of their
**Sort Field**, and when several rules set the same attribute, the last one
that matches wins. So that this order stays visible:

- every rule shows its place in the order the rules run, for example `#3`
- a group whose rules are interleaved with rules of other groups says so in
  its heading, and a dashed line above a rule marks that rules of other groups
  run between it and the rule above it
- an `=` next to the place marks rules with the same sort value: their order
  among each other is not fixed

The grouping applies to the default order. Clicking a column header to sort by
it, or _Show as plain list_, shows the normal table. When the rules do not fit
on one page, the list is not grouped either.

A click on a group heading (or Enter or Space while it has the focus) folds
the group to its heading, which still shows the name and the number of rules.
_Expand all_ and _Collapse all_ in the menu bar fold or unfold every group.
The browser remembers which groups are folded, by the attributes of the group. A rule
moved with the arrow keys into a folded group unfolds that group.

### Changing the Order by Drag and Drop

Drag a rule by its handle (☰) to another place. The rule is put directly
behind the rule above its new place in the group (or in front of the rule
below it, when it lands at the top of a group). Only the moved rule gets a new
sort value; the rules behind it are shifted only when there is no free value
left between its new neighbours.

Without a mouse: focus the handle with the Tab key and move the rule with the
arrow keys up and down.

Dropping a rule into **another group** changes what the rule does: after a
confirmation it sets the attribute of that group instead of its own, with the
same value. This works only between groups of a single attribute. A rule with
several attributes can not be dropped into another group, and no rule can be
dropped into the group of a combination: such a move is refused and nothing
changes. To change the attributes of such a rule, edit the rule. Within its
own group it can be moved as any other rule. Rules without an attribute can
not change their group either.

Read-only users see the grouped list without the handles.

## Jinja Support in Outcome Values

Since version 3.12.1, the outcome value field supports Jinja templating. You can reference any host attribute and the `{{HOSTNAME}}` placeholder:

```jinja
{{HOSTNAME}}-{{location|lower}}
```

This makes it easy to compose derived attributes from existing data.

## Example: Mark Hosts That Have Not Been Seen for a While

Every import stamps the host with the timestamp of its last sighting. The
Syncer stores it in the inventory as `syncer_last_seen` (alongside
`syncer_account` and `syncer_last_sync`), and inventory data is part of the
attribute set every rule sees. Combined with the [`datetime`](../advanced/jinja_functions.md)
helper this is enough to derive a `disabled` flag purely in Jinja — no plugin
and no code change needed.

!!! tip "Since version 4.4: no Jinja needed"
    The conditions [`Older Than` / `Newer Than`](conditions.md#older-than-newer-than)
    match on the age of `syncer_last_seen` directly. A rule with the condition
    _Tag_ `syncer_last_seen`, _Value Match_ `Older Than`, value `14d` and the
    fixed outcome `disabled` covers the first half of the expression below; a
    second rule with `Newer Than` and `active` covers the other. Both are
    easier to read in the rule list than the expression. See
    [Match hosts that were not seen for a while](conditions.md#match-hosts-that-were-not-seen-for-a-while).

Create a Custom Attribute rule with a condition of your choice and this
outcome:

- **Attribute Name**: `disabled`
- **Attribute Value**:

```jinja
{% if syncer_last_seen is defined %}{{ 'disabled' if (datetime.datetime.utcnow() - syncer_last_seen).days > 14 else 'active' }}{% else %}active{% endif %}
```

Pick the number of days to suit your environment; 14 is only an example.
Because Custom Attributes are the first rules applied, the resulting
`disabled` attribute is available to every condition that runs afterwards —
filter, rewrite, export and action rules can all match on it.

If you prefer a flag over a word, emit `True` / `False` instead of
`disabled` / `active`:

```jinja
{% if syncer_last_seen is defined %}{{ 'True' if (datetime.datetime.utcnow() - syncer_last_seen).days > 14 else 'False' }}{% else %}False{% endif %}
```

Note that a Jinja-rendered outcome is always a string. Only a value typed
literally as `True` or `False` into the Attribute Value field (without any
Jinja) is stored as a real boolean. Either way, a later condition matching on
`True` works.

### Things to Watch Out For

- `syncer_last_seen` is written in **UTC**, like every timestamp the Syncer
  stores. Compare it against `datetime.datetime.utcnow()`, as shown above — a
  comparison against `now()` shifts the deadline by your UTC offset.
- The timestamp only moves forward when an import actually touches the host.
  That is exactly the point here: a host that disappeared from its source
  keeps ageing and eventually crosses the threshold.
- Such a rule answers differently tomorrow without anything about the host
  changing. From version 4.4 on, a rule set that uses `syncer_last_seen` or
  `syncer_last_sync` is therefore not answered from the export cache, so a
  host that comes back is switched on again with its next export. In older
  versions the cached value could stay in place until the host's data changed.
- A host that has never been imported has no `syncer_last_seen` at all. Without
  the `{% if syncer_last_seen is defined %}` guard the outcome renders to an
  empty value instead of `active`. Alternatively, restrict the rule via its
  condition so it only matches hosts that have the attribute.

## Rule-based vs. Rewrite-based Custom Attributes

This global rule creates attributes before any module-specific processing. For more powerful transformations — such as splitting values, converting lists, or using complex Jinja logic — use the [Rewrite Attributes](rewrite_attributes.md) feature instead. Rewrites are configured per module and offer additional operations.
