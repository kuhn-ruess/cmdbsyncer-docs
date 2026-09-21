# Custom Attributes

No data source is perfect. CMDBsyncer lets you enrich your hosts with additional attributes using rule-based assignments — independent of what the source provides.

Custom Attribute rules are the first rule type applied and work globally across all modules.

Go to: _Modules → Syncer Rules → Custom Attributes_

A rule consists of a [Condition](conditions.md) and an outcome:

- **Attribute Name** — the name of the new or existing attribute to set
- **Attribute Value** — the value to assign

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

Create a Custom Attribute rule with a condition of your choice and this
outcome:

- **Attribute Name**: `disabled`
- **Attribute Value**:

```jinja
{% if syncer_last_seen is defined %}{{ 'disabled' if (datetime.datetime.now() - syncer_last_seen).days > 14 else 'active' }}{% else %}active{% endif %}
```

Pick the number of days to suit your environment; 14 is only an example.
Because Custom Attributes are the first rules applied, the resulting
`disabled` attribute is available to every condition that runs afterwards —
filter, rewrite, export and action rules can all match on it.

If you prefer a flag over a word, emit `True` / `False` instead of
`disabled` / `active`:

```jinja
{% if syncer_last_seen is defined %}{{ 'True' if (datetime.datetime.now() - syncer_last_seen).days > 14 else 'False' }}{% else %}False{% endif %}
```

Note that a Jinja-rendered outcome is always a string. Only a value typed
literally as `True` or `False` into the Attribute Value field (without any
Jinja) is stored as a real boolean. Either way, a later condition matching on
`True` works.

### Things to Watch Out For

- `syncer_last_seen` is written in **local time** (the server's own clock),
  not UTC. Compare it against `datetime.datetime.now()`, as shown above — a
  comparison against `utcnow()` shifts the deadline by your UTC offset.
- The timestamp only moves forward when an import actually touches the host.
  That is exactly the point here: a host that disappeared from its source
  keeps ageing and eventually crosses the threshold.
- A host that has never been imported has no `syncer_last_seen` at all. Without
  the `{% if syncer_last_seen is defined %}` guard the outcome renders to an
  empty value instead of `active`. Alternatively, restrict the rule via its
  condition so it only matches hosts that have the attribute.

## Rule-based vs. Rewrite-based Custom Attributes

This global rule creates attributes before any module-specific processing. For more powerful transformations — such as splitting values, converting lists, or using complex Jinja logic — use the [Rewrite Attributes](rewrite_attributes.md) feature instead. Rewrites are configured per module and offer additional operations.
