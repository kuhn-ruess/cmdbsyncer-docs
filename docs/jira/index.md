# Jira Cloud

Since Syncer 3.8.2 the Jira Cloud plugin imports Assets/Insight objects
into the Syncer; since 4.1 it can also export host fields back into
Jira Cloud Assets.

## Account Settings

Configure on the Account record:

- **Address**: your `https://<workspace>.atlassian.net` URL
- **Username**: Jira account username (email)
- **Password**: API token (not your password)

In *Additional Settings*:

- `workspace_id` — Atlassian Assets workspace id. Discover it via
  `GET <address>/rest/servicedeskapi/assets/workspace`.
- `ql_query` — AQL filter used by **import only**, e.g.
  `objectType = "Hardware Server"`.
- `verify_cert` — `True` / `False`.

## Import

```
cmdbsyncer jira import_cloud <account>
```

Walks the configured `ql_query` and stores each Asset object as a Host
record with one label per Asset attribute.

## Export

The export writes selected host attributes back into Jira Cloud Assets
objects.  One **Export Rule** = one target object type.  Multiple rules
can run in a single export pass, e.g. push Linux hosts to
*Red Hat Linux* and Windows hosts to *Windows Server* without
re-iterating the host list.

### One-off: cache the Jira schema

The GUI needs to know which object types and attributes exist to offer
autocomplete; the export plugin uses the same cache to resolve
attribute names to ids without doing a live Jira call per host.

```
cmdbsyncer jira sync_schema <account>
```

Re-run after schema edits in Jira.  The cache is visible under
**Modules → Jira Cloud → Schema Cache**.

### Define an Export Rule

**Modules → Jira Cloud → Export Rules → Create:**

- **Conditions**: standard rule conditions — pick which hosts the rule
  applies to.
- **Field Mapping**: one row per Jira attribute to write.  Pick the
  **Target** (a single dropdown over every cached object-type /
  attribute pair, e.g. `CMDB / Hardware Server / Zweck`), then enter
  the **Value** as a Jinja template rendered against the host's labels
  and inventory; `{{HOSTNAME}}` is available.  Multiple rows targeting
  different object types in the same rule write to one Jira object per
  type per host.

Missing Jira objects are created on the fly — the hostname is filled
into the `Name` attribute.  If you want certain hosts to be left alone
entirely, add a **Filter** rule (see below).

### Filter (exclude hosts)

**Modules → Jira Cloud → Filter** uses the standard Filter rule format:
match conditions on the host, then an `Ignore Matching Hosts` action
drops the host from the export entirely (no update, no create).  This
is the canonical place to scope the export — narrower than
`Account → Plugin Settings → object_filter` (which only filters by
object type).

Lookup is always by hostname → Jira's `Name` attribute.  If you need
to match by something else, use a label / inventory rewrite to put the
desired value into the hostname (or open an issue if this stops
covering your case).

### Run

```
cmdbsyncer jira export_cloud <account>
```

For each enabled rule the plugin:

1. Loads every existing object of the target type in one paginated AQL
   call.
2. Iterates matching hosts and renders the field mapping.
3. Compares with the current values and `PUT`s only when something
   changed (unchanged objects are not re-sent).
4. `POST`s a new object when the lookup yields nothing **and**
   *Create if missing* is on.

The run logs `updated=`, `created=`, `unchanged=` and `skipped=` per
rule so an idempotent re-run produces visible "no changes" output
instead of silent traffic.

### Cron

Both `jira sync_schema` and `jira export_cloud` are registered as
cronjobs and can be scheduled under **Cron → Cronjobs**.
