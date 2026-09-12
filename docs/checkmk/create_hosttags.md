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

## Unique Titles

Titles have to be unique inside a tag group. Checkmk recognizes a renamed tag by its **title**, not by its ID. Two tags sharing one title therefore look like the rename of a tag that is in use, and Checkmk refuses the update of the whole group with:

```text
Updating this host tag group requires additional authorization.
The host tag group you intend to edit is used by other instances.
You must authorize Checkmk to update the relevant instances using the repair parameter
```

The group then keeps its old state, new tag values are never created, and every host export that needs one of them fails with `Invalid value for tag-group`.

The Syncer prevents this: if your Rewrite Title produces the same title for two different tag IDs, it appends the tag ID to **each** of them, so Checkmk no longer finds the old title anywhere and recognizes neither a rename nor a removal. Nothing else has to be done.

A common cause is a source value with a trailing blank: the tag ID is built from the raw value while the title is trimmed, which yields two IDs with one title. Add `| trim` at the start of your Rewrite ID to avoid it.

!!! warning
    `CMK_TAG_REPAIR` gives Checkmk permission to modify the objects that use a tag group, and how it repairs them depends on the change:

    * A **renamed** tag is uncritical. The condition of every rule using it is rewritten to the new tag ID, negations included.
    * A **removed** tag is not. Checkmk deletes the condition from every rule that uses it. The rule itself stays, but without that condition it matches **more** hosts than before — silently.

    With `CMK_DONT_DELETE_TAGS = True` (the default) the Syncer never removes a tag value, so only the harmless case can occur. The dangerous combination is `CMK_TAG_REPAIR = True` together with `CMK_DONT_DELETE_TAGS = False`: every value that disappears from your source can then widen a rule. Leave `CMK_TAG_REPAIR` off unless Checkmk explicitly asks for it, and check your rules afterwards.

## Group Multiply by List

In this mode, the Syncer creates multiple tag groups based on a list, without applying Rewrite templates. Use `{{name}}` as the placeholder in the Topic Name and Title fields.

In the _Group Multiply List_ field, provide a Python list using the `get_list()` helper:

```jinja
{{YOUR_LIST_ATTRIBUTE|safe}}
{{get_list(['Name1', 'Name2', 'Name3'])|safe}}
```

The `|safe` filter is required — without it, the list syntax is escaped and the feature does not work.
