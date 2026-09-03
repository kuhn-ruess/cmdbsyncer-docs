# Objects Endpoints

Base path: `/api/v1/objects` — needs the API role `objects` or `all`.

These endpoints read, create, update and delete hosts (and objects) inside the
syncer from external systems. This is the way to feed a CMDB the syncer has no
importer for.

!!! note
    There is no `PUT` method. The syncer gets or creates the host from its
    database on `POST`, so you never have to check whether a host exists first.

---

## `GET /api/v1/objects/<hostname>`

Return labels, inventory and the import timestamps of one host.

```bash
curl -u "user:password" \
     https://cmdbsyncer.example.com/api/v1/objects/srv-web01
```

```json
{
  "hostname": "srv-web01",
  "labels": {"os": "linux", "location": "muc"},
  "inventory": {"checkmk": {"folder": "/muc"}},
  "last_seen": "2026-04-26T17:55:00Z",
  "last_update": "2026-04-26T17:55:00Z"
}
```

`last_seen` is the last time an import saw the host, `last_update` the last time
an import actually changed it. Both are `false` when the host was never imported.

Unknown hosts — and hosts outside the caller's [scope](index.md#restricting-a-user-to-accounts) — answer `404`.

---

## `POST /api/v1/objects/<hostname>`

Create or update a host and bind it to an account.

| Field | Required | Description |
|---|---|---|
| `account` | yes | Name of an existing account. An unknown name returns `400`. |
| `labels` | yes | Flat key/value attributes. An empty object is valid. |

```bash
curl -u "user:password" \
     -H "Content-Type: application/json" \
     -d '{"account": "my_import", "labels": {"os": "linux", "location": "muc"}}' \
     https://cmdbsyncer.example.com/api/v1/objects/srv-web01
```

```json
{"status": "saved"}
```

A host that already belongs to a **different** account is not touched; the call
returns `403` with `{"status": "account_conflict"}`. Re-binding a host to another
account is done in the admin interface, not over the API.

---

## `DELETE /api/v1/objects/<hostname>`

Archive the host. <span class="since">Since 4.3</span> the host is soft-deleted —
it moves to the Archive view and can be restored — instead of being removed
permanently. If the host frees a seat in a Checkmk folder pool, the seat is
given back.

```bash
curl -u "user:password" -X DELETE \
     https://cmdbsyncer.example.com/api/v1/objects/srv-web01
```

```json
{"status": "deleted"}
```

---

## `POST /api/v1/objects/bulk`

Create or update many hosts under one account in a single call. Use this instead
of a loop over the single-host endpoint — it is far faster for a full import run.

| Field | Required | Description |
|---|---|---|
| `account` | yes | Account that owns every host in this batch |
| `objects` | yes | List of `{"hostname": ..., "labels": {...}}` |

```bash
curl -u "user:password" \
     -H "Content-Type: application/json" \
     -d '{
           "account": "my_import",
           "objects": [
             {"hostname": "srv-web01", "labels": {"os": "linux"}},
             {"hostname": "srv-web02", "labels": {"os": "linux"}}
           ]
         }' \
     https://cmdbsyncer.example.com/api/v1/objects/bulk
```

```json
{"status": "saved 2", "not-saved": []}
```

The call does not abort on a single bad host: hosts that belong to another
account (or that the caller may not write) are listed in `not-saved`, everything
else is saved.

---

## `POST /api/v1/objects/<hostname>/inventory`

Replace one inventory section of a host.

| Field | Required | Description |
|---|---|---|
| `key` | yes | Top-level inventory key, e.g. `checkmk`, `netbox`, `my_cmdb` |
| `inventory` | yes | Nested payload stored below that key |

```bash
curl -u "user:password" \
     -H "Content-Type: application/json" \
     -d '{"key": "my_cmdb", "inventory": {"owner": "team-web", "sla": "gold"}}' \
     https://cmdbsyncer.example.com/api/v1/objects/srv-web01/inventory
```

```json
{"status": "saved"}
```

!!! warning
    Inventory writes never create a host — an unknown hostname returns `404`.
    Create the host through `POST /api/v1/objects/<hostname>` first, so it gets
    a proper account binding.

Keys must be valid MongoDB keys: no leading `$` and no dots. A rejected key
returns `400`.

---

## `POST /api/v1/objects/bulk/inventory`

Write inventory sections for many hosts at once.

```bash
curl -u "user:password" \
     -H "Content-Type: application/json" \
     -d '{
           "inventories": [
             {"hostname": "srv-web01", "key": "my_cmdb", "inventory": {"sla": "gold"}},
             {"hostname": "srv-web02", "key": "my_cmdb", "inventory": {"sla": "bronze"}}
           ]
         }' \
     https://cmdbsyncer.example.com/api/v1/objects/bulk/inventory
```

```json
{"status": "saved 2", "not-found": []}
```

Every item is validated **before** the first write, so one bad key aborts the
whole batch with `400` instead of leaving half of it saved. Hostnames that do not
exist are not an error — they come back in `not-found`.

---

## `GET /api/v1/objects/all`

Paginated listing of every host (objects excluded).

| Parameter | Default | Description |
|---|---|---|
| `start` | `1` | Zero-based offset |
| `limit` | `100` | Page size, maximum `10000` |

```bash
curl -u "user:password" \
     "https://cmdbsyncer.example.com/api/v1/objects/all?start=0&limit=500"
```

```json
{
  "results": [{"hostname": "srv-web01", "labels": {}, "inventory": {}, "last_seen": "...", "last_update": "..."}],
  "start": 0,
  "limit": 500,
  "size": 12043,
  "_links": {
    "next": "/api/v1/objects/all?limit=500&start=500",
    "prev": "/api/v1/objects/all?limit=500&start=0"
  }
}
```

Follow `_links.next` until it is no longer present — that is the last page.
Non-numeric or negative parameters, and a `limit` above `10000`, return `400`.

---

## Relations
<span class="since">Since 4.1</span>

Typed relations between hosts. These endpoints only exist when `CMDB_MODE = True`
is set in `local_config.py`; otherwise they answer `404`. Available types are
`depends_on`, `runs_on`, `member_of`, `parent_of` and `connects_to`.

### `GET /api/v1/objects/<hostname>/relations`

```json
{
  "hostname": "srv-web01",
  "outgoing": [
    {"type": "runs_on", "type_label": "Runs on", "target": "esx-01", "source": "manual"}
  ],
  "inbound": [
    {"type": "depends_on", "type_label": "Required by", "target": "srv-app01", "source": "import"}
  ]
}
```

Outgoing edges are stored on the host itself, inbound edges are looked up from
the other side and are read-only here — change them on their source host.

### `POST /api/v1/objects/<hostname>/relations`

Add an edge from `hostname` to `target`.

| Field | Required | Description |
|---|---|---|
| `type` | yes | One of the relation types above |
| `target` | yes | Hostname of the target object |
| `source` | no | Provenance tag, default `manual`. Importers set their own tag so they can later prune their own edges without touching manual ones. |

```bash
curl -u "user:password" \
     -H "Content-Type: application/json" \
     -d '{"type": "runs_on", "target": "esx-01"}' \
     https://cmdbsyncer.example.com/api/v1/objects/srv-web01/relations
```

```json
{"status": "added"}
```

An edge that already exists answers `{"status": "unchanged"}`. An unknown type or
a host pointing at itself returns `400`.

### `DELETE /api/v1/objects/<hostname>/relations`

Same body as `POST` (`type` and `target`); removes the edge and answers
`{"status": "removed"}`, or `{"status": "unchanged"}` if there was nothing to
remove.
