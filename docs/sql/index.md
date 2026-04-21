# SQL Imports (MSSQL, ODBC, MySQL)

The Syncer can read hosts and inventory rows from any SQL database via
the MSSQL/ODBC or MySQL plugins. The workflow is the same for both:
create an account with the connection parameters, point it at a table
or hand-written query, then run `import_hosts` or `inventorize_hosts`.

## CLI

```bash
./cmdbsyncer mssql import_hosts my-mssql-account
./cmdbsyncer mssql inventorize_hosts my-mssql-account

./cmdbsyncer mysql import_hosts my-mysql-account
./cmdbsyncer mysql inventorize_hosts my-mysql-account
```

The ODBC plugin (`./cmdbsyncer odbc ...`) uses the same account-level
fields as MSSQL and is the right choice for non-Microsoft ODBC
sources.

## Account Settings

Configure these fields as Custom Fields on the account:

| Field                      | Purpose                                                                  |
| :------------------------- | :----------------------------------------------------------------------- |
| `database`                 | Database name                                                            |
| `table`                    | Source table (ignored when `custom_query` is set)                        |
| `fields`                   | Comma-separated column list (ignored when `custom_query` is set)         |
| `hostname_field`           | Column that holds the hostname                                           |
| `custom_query`             | Optional hand-written SQL; overrides `table` + `fields`                  |
| `allow_ddl`                | Opt-in flag that lets `custom_query` include a CREATE before the SELECT  |
| `rewrite_hostname`         | Optional Jinja template applied to the hostname before lookup            |
| `driver`                   | ODBC driver name (MSSQL/ODBC only, e.g. `ODBC Driver 18 for SQL Server`) |
| `instance` / `serverport`  | MSSQL instance name or explicit port (MSSQL/ODBC only)                   |
| `trust_server_certificate` | Accept untrusted TLS certs on MSSQL (`yes` / `true` / `1`)               |

## Custom Queries

When `custom_query` is set, the Syncer runs that SQL verbatim instead
of building a `SELECT … FROM table`. The query must return the columns
the importer needs (including `hostname_field`), for example:

```sql
SELECT name AS host, ip, role
FROM dbo.cmdb_hosts
WHERE active = 1
```

By default `custom_query` is read-only. It must start with `SELECT` or
`WITH` and may not contain any write or DDL keyword — a safeguard
against a stale config accidentally mutating the source database.

## Creating the Target Table (opt-in)

Some installations want the Syncer to bootstrap its own source table —
for example when an ETL populates the table on the same server but the
schema should be managed alongside the Syncer account. Set
`allow_ddl` to `yes` (or `true` / `1`) on the account and the same
`custom_query` may then include a `CREATE TABLE` before the `SELECT`:

```sql
CREATE TABLE IF NOT EXISTS syncer_hosts (
    host VARCHAR(255) PRIMARY KEY,
    ip   VARCHAR(45),
    role VARCHAR(64)
);
SELECT host, ip, role FROM syncer_hosts;
```

For MSSQL the vendor-specific `IF NOT EXISTS` guard also works:

```sql
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'syncer_hosts')
BEGIN
    CREATE TABLE syncer_hosts (
        host NVARCHAR(255) PRIMARY KEY,
        ip   NVARCHAR(45),
        role NVARCHAR(64)
    )
END;
SELECT host, ip, role FROM syncer_hosts;
```

Rules that stay in force even with `allow_ddl` set:

- The statement must contain at least one `SELECT` so the importer has
  rows to iterate.
- Destructive or data-mutating keywords are still rejected:
  `DROP`, `TRUNCATE`, `DELETE`, `UPDATE`, `INSERT`, `EXEC`, `EXECUTE`,
  `GRANT`, `REVOKE`, `REPLACE`, `MERGE`.
  A typo or stale config therefore cannot wipe the schema or alter
  existing rows.
- The bootstrap DDL must be idempotent (`IF NOT EXISTS` or an
  equivalent guard); the Syncer runs the whole `custom_query` on every
  sync.

Leave `allow_ddl` unset to keep the hardened, read-only default.

## Multi-Statement Execution Notes

- MSSQL / ODBC: the query is dispatched through a single
  `cursor.execute`; after the query runs the Syncer commits the
  connection so the CREATE persists.
- MySQL: the connector is invoked with `multi=True`. The Syncer walks
  all result sets and uses the one that actually returned rows, then
  commits.

If your driver does not support multi-statement execution, split the
DDL out into a separate tool and leave `allow_ddl` off.
