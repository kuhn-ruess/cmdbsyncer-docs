# Host Tags

The Syncer can manage predefined host tag groups in Checkmk. Based on your host attributes, it adds and removes the tags that belong to those groups automatically.

Go to: _Modules → Checkmk → Manage Host Tags_

!!! note
    The Syncer cannot remove a tag that is still in use by a Checkmk rule. In that case, the tag group is silently skipped — no exception is thrown.

This feature uses host-based caching for performance. The cache is refreshed automatically when a host changes, making tag exports fast even in environments with more than 100,000 hosts.

## Configuration

| Field                  | Description                                                           |
| :--------------------- | :-------------------------------------------------------------------- |
| Group Topic Name       | The category the tag group is shown under in Checkmk                  |
| Group Title            | Human-readable title of the group, e.g. "My Locations"                |
| Group ID               | Internal ID of the tag group, e.g. `my_locations`                     |
| Group Help             | Help text shown to users in the Checkmk UI                            |
| Group Multiply by List | Create multiple tag groups from a list (see below)                    |
| Group Multiply List    | Syncer attribute containing the list. Use `get_list()`.               |
| Filter by Account      | Only create tags based on objects managed by this account             |
| Rewrite ID             | Jinja template for the tag ID, e.g. `{{name\|lower}}`                 |
| Rewrite Title          | Jinja template for the tag display title, e.g. `{{name\|capitalize}}` |
| Enabled                | Enable or disable this rule                                           |

All Rewrite fields support custom [Syncer Jinja Functions](../advanced/jinja_functions.md) and the `{{HOSTNAME}}` placeholder.

!!! important
    The `cmk_cleanup_tag_id()` Jinja function is applied automatically to the Rewrite ID field. If you reference this tag ID elsewhere — for example in export rules — make sure to apply the same function to ensure the IDs match.

## Group Multiply by List

In this mode, the Syncer creates multiple tag groups based on a list, without applying Rewrite templates. Use `{{name}}` as the placeholder in the Topic Name and Title fields.

In the _Group Multiply List_ field, provide a Python list using the `get_list()` helper:

```jinja
{{YOUR_LIST_ATTRIBUTE|safe}}
{{get_list(['Name1', 'Name2', 'Name3'])|safe}}
```

The `|safe` filter is required — without it, the list syntax is escaped and the feature does not work.
