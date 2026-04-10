# Groups Management

The Groups Management feature creates Contact-, Host-, and Service-Groups in Checkmk based on attributes from your hosts.

Go to: _Modules → Checkmk → Manage Host-/Contact-/Service-Groups_

## Object Cache

The Syncer maintains a local cache of all groups it has created (_Rules → Checkmk → Object Cache_). This allows it to safely remove groups from Checkmk when they are no longer needed — without deleting groups that were created manually by a user.

If you delete a cache entry, the Syncer will only re-take ownership of that group when it is provided again by the source data.

!!! note
    Checkmk does not allow two groups of different types to share the same name. You cannot have a Contact Group and a Host Group with identical names. Use the Rewrite feature to add a prefix if needed.

## Rule Parameters

| Option        | Description                                                                           |
| :------------ | :------------------------------------------------------------------------------------ |
| Group Name    | Type of group to create: Contact Group, Host Group, or Service Group                  |
| Foreach Type  | Iterate by attribute name, by attribute values, or by objects                         |
| Foreach       | Attribute name or value to iterate. Use `*` at the end as a wildcard (e.g. `dhcp*`)   |
| Rewrite       | Jinja template for the group ID. `{{name}}` refers to the found value                 |
| Rewrite Title | Jinja template for the group display title                                            |

The Rewrite fields support all custom [Syncer Jinja Functions](../advanced/jinja_functions.md).

## Example

Your hosts have an attribute `application` that indicates their role. You want to create a Checkmk Contact Group for each unique application value, prefixed with `cg_`.

1. Set **Group Name** to _Contact Groups_
2. Set **Foreach Type** to _Foreach Attribute_
3. Set **Foreach** to `application`
4. Set **Rewrite** to `cg_{{name|lower}}`
5. Set **Rewrite Title** to `{{name}}`

After committing changes, run:

```bash
./cmdbsyncer checkmk export_groups ACCOUNTNAME
```

## Wildcard Values

If your attribute values follow a naming pattern — for example `contact_1`, `contact_2`, `contact_3` — you can use `contact_*` as the Foreach value to match all values starting with that string. The wildcard only works at the end of the string.
