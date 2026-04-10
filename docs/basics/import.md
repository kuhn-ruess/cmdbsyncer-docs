# Import

Import is the process of connecting to a source system, reading its data, and storing it as hosts and attributes in the CMDBsyncer database. Once imported, the data is available to the rules engine and can be exported to any configured target.

## What Gets Imported

Every imported entry becomes a **host** in CMDBsyncer (or an **object**, if the account is configured accordingly). Along with the hostname, any associated data is stored as attributes — IP addresses, contacts, locations, tags, or any other key-value information the source provides.

Attributes can be strings, numbers, lists, or dicts. CMDBsyncer normalizes and stores them all, and they become available as conditions and values in your rules.

## How Import Works

1. CMDBsyncer connects to the source system using the credentials and settings from the [Account](accounts.md).
2. The source data is fetched and mapped to hosts and attributes.
3. Hosts are created or updated in the local database.
4. Hosts that are no longer present in the source are marked as stale and eventually deleted (after the configured grace period).

Import is triggered either manually via the CLI or automatically via a [Cron job](cron.md).

## Running an Import

Every module has its own import command. The general pattern is:

```bash
./cmdbsyncer <module> <import_command> <account_name>
```

For example, to import from Netbox:

```bash
./cmdbsyncer netbox import_devices my-netbox
```

Add `--debug` to see the full request/response output, or `--help` to list all available commands for a module.

## Multiple Sources

CMDBsyncer can import from multiple sources simultaneously. Hosts from different sources are merged by hostname — if the same host exists in two sources, its attributes are combined. Accounts marked as **Is Master** can overwrite attributes set by other accounts.

## Adding a Custom Source

If your source is not supported out of the box, you can add it by writing a small import plugin. See [Build your own Plugin](../advanced/own_plugins.md) for details.

## Next Steps

- [Export to a target system](export.md)
- [Use rules to control what gets exported](conditions.md)
- [Rewrite or enrich attributes before export](rewrite_attributes.md)
