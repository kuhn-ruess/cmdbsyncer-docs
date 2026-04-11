# Export all Hosts as CSV

The Syncer has a hidden endpoint that returns every host in the database as a
single CSV file. The endpoint is not linked from the menu — you reach it by
appending `/csv` to the Host admin URL:

```text
https://<your-syncer>/admin/host/csv
```

The response is a download named `hosts_export_<YYYYMMDD_HHMMSS>.csv`.

## Permissions

The endpoint is gated by the normal admin login and requires the `host` right
on the current user. Unauthenticated requests get a `401 Unauthorized`.

## What is Exported

- All hosts where `is_object` is not `True` (templates are excluded)
- Sorted alphabetically by hostname
- One row per host, one column per field

### Fixed Columns

| Column                | Description                                                                |
|-----------------------|----------------------------------------------------------------------------|
| `hostname`            | Host name as stored in the Syncer.                                         |
| `object_type`         | Object type of the host.                                                   |
| `available`           | `True`/`False` — whether the host is currently marked as available.        |
| `source_account_name` | Name of the account the host was last imported from.                       |
| `folder`              | Resolved target folder (e.g. for Checkmk).                                 |
| `last_import_seen`    | Timestamp the host was last seen by an import run (`YYYY-MM-DD HH:MM:SS`). |
| `last_import_sync`    | Timestamp of the last successful sync.                                     |
| `no_autodelete`       | `True` if the host is protected from automatic cleanup.                    |
| `label_<name>`        | One column per label name listed in `export_labels_list`.                  |
| `inventory_<name>`    | One column per inventory field listed in `export_inventory_list`.          |

### Configurable Columns

Which labels and inventory fields end up in the CSV is controlled in the
global Syncer configuration, **not** via a query parameter:

- `export_labels_list` — list of label keys; each one becomes a column
  prefixed with `label_`.
- `export_inventory_list` — list of inventory keys; each one becomes a column
  prefixed with `inventory_`.

Both settings live in the Syncer _Config_ ([Local Config Variables](../checkmk/config_vars.md)).
Hosts that don't have a value for a configured label or inventory key get an
empty cell.

## Format

- Separator: `,` (standard CSV)
- Quoting: Python `csv.writer` default (minimal)
- Encoding: UTF-8
- First row: header

## See also

- [Hosts, Labels and Inventory](host_labels_inventory.md) — where `export_labels_list` and `export_inventory_list` are described.
- [CSV Basics](../csv/index.md) — CLI-driven CSV _import_ (the opposite direction).
