# Export

Export is the process of syncing data from the CMDBsyncer database to a target system. The target receives exactly what the rules engine has computed — hostnames, attributes, labels, folder assignments, or whatever the target module supports.

Most users export to Checkmk or Netbox, but any module that supports export works the same way: configure an account, define rules, run the export.

## How Export Works

1. CMDBsyncer reads all hosts from its local database.
2. For each host, the rules engine evaluates conditions and produces the final set of attributes and actions.
3. The results are compared against the current state of the target system.
4. Only the differences are written — new hosts are created, changed hosts are updated, removed hosts are deleted.

This diff-based approach means repeated exports are efficient and idempotent.

## Running an Export

Every module has its own export command. The general pattern is:

```bash
./cmdbsyncer <module> <export_command> --account=<account_name>
```

For example, to export hosts to Checkmk:

```bash
./cmdbsyncer checkmk export_hosts --account=my-checkmk
```

Add `--debug` to see the full request/response details, or `--dry-run` (where supported) to simulate the export without writing anything to the target.

## Previewing Before Export

Most modules offer read-only commands to inspect what would be exported:

```bash
# List all hosts that would be sent to the target
./cmdbsyncer checkmk show_hosts --account=my-checkmk

# Check rule outcomes for a specific host
./cmdbsyncer checkmk export_hosts --account=my-checkmk --debug-rules=myhostname
```

→ [Debugging documentation](debug_rules.md)

## Controlling Which Hosts Get Exported

By default, all hosts in the database are candidates for export. You have several ways to limit this:

- **Filters** — restrict which hosts and attributes are included per account. Filters can be negated with `!` to exclude specific values. → [Filter documentation](filter.md)
- **Conditions on rules** — rules only apply when their conditions match, so hosts that don't match any rule produce no output for that rule.
- **Object flag** — hosts marked as **Is Object** are never exported as hosts to target systems.

## Handling Deletions

When a host disappears from all import sources, it is eventually removed from the CMDBsyncer database by the [maintenance process](maintenance.md). Once removed from the database, it will also be deleted from all export targets on the next export run.

The timing of deletion is controlled by the maintenance configuration — typically a grace period of several days to avoid accidental deletions from temporary import failures.

→ [Maintenance and host removal](maintenance.md)

## Building Your Own Export Plugin

If your target system is not supported out of the box, you can build an export plugin. Export plugins are more involved than import plugins — they need rule integration and a frontend component — but follow a well-defined API.

→ [Build your own Plugin](../advanced/own_plugins.md)
