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

## Rule-based vs. Rewrite-based Custom Attributes

This global rule creates attributes before any module-specific processing. For more powerful transformations — such as splitting values, converting lists, or using complex Jinja logic — use the [Rewrite Attributes](rewrite_attributes.md) feature instead. Rewrites are configured per module and offer additional operations.
