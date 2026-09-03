# Rules Endpoints

Base path: `/api/v1/rules` — needs the API role `rules` or `all`.

These endpoints read and write the syncer configuration itself: filters,
rewrites, export rules, custom attributes and everything else the rule engine
knows. They share their import/export helpers with `cmdbsyncer rules
import_rules` / `export_rules` (see [Rule Import/Export](../basics/rule_import_export.md)),
so CLI and API always produce the same format.

Typical uses: keep the rule set of a test and a production instance in sync, or
put the configuration under version control.

---

## `GET /api/v1/rules/types`

Every rule type the server knows — the catalog for the endpoints below.

```bash
curl -u "user:password" \
     https://cmdbsyncer.example.com/api/v1/rules/types
```

```json
{"rule_types": ["accounts", "ansible_filter", "cmk_export_rules", "cmk_filter", "custom_attributes", "..."]}
```

---

## `GET /api/v1/rules/<rule_type>`

Every rule of one type, as a JSON list. An unknown type answers `404`.

```bash
curl -u "user:password" \
     https://cmdbsyncer.example.com/api/v1/rules/custom_attributes
```

```json
{
  "rule_type": "custom_attributes",
  "rules": [{"_id": {"$oid": "..."}, "name": "Set location", "enabled": true, "...": "..."}]
}
```

The documents come back exactly as they are stored, so they can be posted back
unchanged.

---

## `POST /api/v1/rules/<rule_type>`

Create one or many rules of that type. The body is either a single rule object
or a list of them, in the same shape as the export above.

| Parameter | Description |
|---|---|
| `override` | `?override=1` replaces rules that already exist instead of counting them as duplicates |

```bash
curl -u "user:password" \
     -H "Content-Type: application/json" \
     -d '[{"name": "Set location", "enabled": true}]' \
     "https://cmdbsyncer.example.com/api/v1/rules/custom_attributes?override=1"
```

```json
{"rule_type": "custom_attributes", "imported": 1, "duplicate": 0, "invalid": 0}
```

The answer is `201` when at least one rule was newly written, and `200` when
everything in the body was a duplicate or invalid.

---

## `GET /api/v1/rules/export`

Every rule of every type in one document — the backup format.

| Parameter | Default | Description |
|---|---|---|
| `include_hosts` | off | Also export the host objects. CMDB templates are always exported as their own type. |
| `include_accounts` | off | Also export the accounts |
| `include_users` | off | Also export users — contains password hashes and roles, **treat as secret** |
| `include_passwords` | off | Also export the Checkmk password store; entries stay encrypted with this instance's key, **treat as secret** |

```bash
curl -u "user:password" \
     https://cmdbsyncer.example.com/api/v1/rules/export > rules_backup.json
```

```json
{
  "exported_at": "2026-04-26T17:55:00Z",
  "rules": {
    "custom_attributes": [{"...": "..."}],
    "cmk_filter": [{"...": "..."}]
  }
}
```

---

## `POST /api/v1/rules/import`

Import rules in bulk. Three body formats are accepted:

* single type: `{"rule_type": "custom_attributes", "rules": [ {...}, ... ]}`
* multiple types: `{"rules": {"custom_attributes": [ {...} ], "cmk_filter": [ {...} ]}}` —
  exactly what `GET /rules/export` returns
* the on-disk JSONL form as `Content-Type: text/plain`, one rule per line with
  optional `{"rule_type": "..."}` header lines

Pass `?override=1` — or `"override": true` inside a JSON body — to replace rules
that already exist instead of skipping them.

```bash
curl -u "user:password" \
     -H "Content-Type: application/json" \
     --data-binary @rules_backup.json \
     "https://cmdbsyncer.example.com/api/v1/rules/import?override=1"
```

```json
{"imported": {"custom_attributes": 12, "cmk_filter": 3}, "total": 15}
```

---

## `POST /api/v1/rules/autorules`

Run the rule automation that builds rules out of the host data, the same pass as
the autorules cronjob (see [Autocreate Rules](../basics/auto_rules.md)). The body
is optional; `{"debug": true}` writes verbose output to the server log.

```bash
curl -u "user:password" -X POST \
     https://cmdbsyncer.example.com/api/v1/rules/autorules
```

```json
{"status": "ok"}
```

The call runs synchronously and only answers when the pass is finished — on a
large installation this can take a while.
