# Debugging

CMDBsyncer provides several debug tools that let you inspect behavior at every stage of the pipeline — before anything is written to a target system.

## --debug Flag

Most CLI commands accept a `--debug` flag. It does two things:

- Raises exceptions instead of swallowing them, so you see the full stack trace on errors.
- Sets the Python log level to `DEBUG`, giving you detailed output about HTTP requests, responses, and internal processing directly on the console.

```bash
./cmdbsyncer checkmk export_hosts --account=myaccount --debug
```

This is the first tool to reach for when a sync is failing or producing unexpected results.

## Debugging Rule Outcomes

Rules can produce complex outcomes across many hosts. To inspect exactly which rules matched and which attributes were set for a specific host, use `--debug-rules`:

```bash
./cmdbsyncer checkmk export_hosts --account=myaccount --debug-rules=myhostname
```

This prints a detailed table showing:

- Which rules were evaluated for the given host
- Which conditions matched or did not match
- The final attribute values that would be sent to the target

You can combine `--debug-rules` with `--debug` to also raise exceptions during the same run:

```bash
./cmdbsyncer checkmk export_hosts --account=myaccount --debug-rules=myhostname --debug
```

!!! tip
    Use `show_hosts` first to confirm the host name as it appears in the syncer database before passing it to `--debug-rules`.

## Inspecting Without Exporting

Some modules provide read-only commands to inspect what would be exported — without making any changes to the target system:

```bash
# List all hosts that would be exported to a Checkmk account
./cmdbsyncer checkmk show_hosts --account=myaccount

# List all labels that would exist in Checkmk after the sync
./cmdbsyncer checkmk show_labels --account=myaccount

# Show hosts present in Checkmk but missing in the syncer
./cmdbsyncer checkmk show_missing_hosts --account=myaccount
```

## API Request Debugging

To see the raw HTTP requests and responses sent to external systems, enable debug mode either via the `--debug` flag (per run) or permanently via `local_config.py`:

```python
config = {
    'LOG_LEVEL': 'DEBUG',
}
```

See the [App Configuration](lcl_config.md) for all available log settings.

## Web Log

Every sync run creates an entry in the web-based log, accessible from the GUI under **Log**. The log shows:

- Metrics per run (hosts processed, errors, duration)
- Per-host errors, highlighted in red
- Which account and command was involved

This is the most practical place to monitor ongoing syncs and spot problems without needing shell access.

→ [Logging documentation](logging.md)

## Advanced Rule Debugging

For development and deep troubleshooting, you can enable verbose condition matching output by setting `ADVANCED_RULE_DEBUG` in `local_config.py`:

```python
config = {
    'ADVANCED_RULE_DEBUG': True,
}
```

When enabled, every condition evaluation will print whether it matched or not. This produces a lot of output and is intended for development use only.
