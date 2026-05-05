# Use CMDBsyncer as a Simple CMDB

CMDBsyncer can be used as a lightweight CMDB, even without a full external source system.
In this mode, you create and maintain objects and hosts directly in the UI.

## What CMDB mode does

If `CMDB_MODE` is enabled, you can manage CMDB-like data directly inside CMDBsyncer:

- Create **Objects** (for example application, network, contact, group)
- Create **Templates** and assign them to hosts/objects
- Maintain custom fields (`cmdb_fields`) with your Data

## Enable CMDB mode

In your `local_config.py`, enable CMDB mode:

```python
config = {
  "CMDB_MODE": True,
}
```
Thats default enabled with Syncer Version 3.12.4.

## Create hosts

1. Open **Hosts**.
2. Click **Create**.
3. Fill basic data:
   - `hostname`
   - `object_type`
   - `available`
   - optional `cmdb_templates`
4. Add or update CMDB fields in the form.
5. Save.

Hosts created this way are treated as CMDB-managed entries inside the syncer.

## Create objects

1. Open the admin UI.
2. Go to **Objects** → **All Objects**.
3. Click **Create**.
4. Fill:
   - `Object Name`
   - `Object Type`
   - `CMDB Fields` (key/value pairs)
5. Save.

Objects are stored as internal CMDB entries and can be used by rules, filters, but not host exports.


## Use Account object mode (`cmdb_object`) for external imports

You can also import objects from external sources and still treat them as CMDB-managed entries in CMDBsyncer.

In the related account, enable object mode and set `cmdb_object`:

- Enable `cmdb_object`
- If`is_object` is enabled, the data can be used in rules, but will not exportet to systems like Checkmk
- Set the matching `object_type`

## Create and use templates (`cmdb_match`)

Templates are special CMDB objects used to standardize fields.

1. Open **Objects** → **Templates**.
2. Create or edit a template with:
   - template name
   - Add `CMDB Fields`
   - optional `cmdb_match`
3. Save.

`cmdb_match` is used for automatic assignment of templates to objects/hosts.

- Format: `label_key:label_value`
- Matching is exact (label key and value)
- Example: `site:dc1`

When an object/host is created or processed and its labels match the expression, the template is added automatically to `cmdb_templates`.

If you changed template matching rules and want to re-apply matching to existing objects/hosts, run:

```bash
./cmdbsyncer sys update_cmdb
```

### Jinja in template values

Field values on a template can use Jinja and reference the host's labels,
inventory and `HOSTNAME`. Rendering happens when the template is merged
into the host's attributes (i.e. at sync / debug time), so the template
itself stores the raw expression.

Example field on a template:

```
description = Server {{ HOSTNAME }} for {{ environment }}
```

Applied to a host with label `environment: prod`, the resulting attribute
is `description = Server web01 for prod`. Values without `{{ ... }}` are
passed through unchanged. Missing variables render as empty strings (the
syncer's default `ignore` mode).

## Define default CMDB fields in local_config.py

You can predefine CMDB fields globally and per object type via `CMDB_MODELS`.
Use `application/config.py` as the structure reference, then override it in `local_config.py`.

### Example

```python
config = {
  "CMDB_MODE": True,
  "CMDB_MODELS": {
    "host": {
      "ipaddress": {"type": "string"},
      "environment": {"type": "string"}
    },
    "network": {
      "cidr": {"type": "string"}
    },
    "all": {
      "owner": {"type": "string"},
      "managed": {"type": "boolean"}
    }
  }
}
```

### How it works

- `all`: fields added for every object/host type
- `<object_type>` (for example `host`, `network`): fields only for that type
- supported field types in forms:
  - `string`
  - `boolean`

When you save a host/object, missing configured fields are added automatically to `cmdb_fields`.

## Soft delete and Archive

Hosts that disappear from a source system are no longer hard-deleted.
Instead they are **archived**: lifecycle state moves to *Archived* and a
`deleted_at` timestamp is recorded. The same applies to the
`sys maintenance` cleanup of stale hosts.

The **Objects → Archive** menu lists every archived host with the deletion
timestamp and reason. From there you can:

- **Restore** selected hosts — they come back with lifecycle state *Active*.
- **Hard Delete** selected hosts — irreversible removal; admin role required.

Archived hosts are excluded from the regular Hosts list, exports and
sync runs, but they still show up in the API for tooling that wants to
audit removals.

## Lifecycle states

Every host carries a Lifecycle state independent of `available`:

- **Planned** — the host is on the roadmap but not yet built.
- **Staged** — built but not yet in production.
- **Active** — in productive use (default for new and legacy hosts).
- **Decommissioned** — taken out of service, kept for reporting.
- **Archived** — read-only record, scheduled for eventual cleanup.

The state shows as a badge in the host list, can be filtered, and can be
changed for many hosts at once via the **Lifecycle: …** bulk actions.
Lifecycle changes are stamped with a timestamp and written into the host log.

## Notes

- Keep `CMDB_MODE` enabled if you want to maintain CMDB data in the UI.
- After changing `local_config.py`, restart the application.
- Start with a small set of required fields in `CMDB_MODELS` and extend gradually.
