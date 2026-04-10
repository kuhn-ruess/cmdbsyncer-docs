# Checkmk

The Checkmk module automates host management, folder creation, group configuration, rules, tags, users, downtimes, and more — all driven by the hosts and attributes already in the Syncer.

## What the Module Does

- Sync hosts to Checkmk, assign them to folders, and set attributes
- Create and manage Contact-, Host-, and Service-Groups based on host attributes
- Manage Checkmk setup rules (thresholds, active checks, contact group assignments)
- Manage host tags, users, downtimes, DCD rules, and the password store
- Import Checkmk site objects and labels back into the Syncer
- Run agent baking and change activation from the command line or cron

See the [Commandline Parameters](commandline.md) page for a full list of available commands, and the [Howtos](recipe_export_hosts.md) section for step-by-step guides.

## Labels

When the Syncer manages a Checkmk instance, you should stop setting labels directly on hosts in Checkmk. If you still need to set labels outside the Syncer — which is not recommended — use distinct prefixes to separate them.

By default, no Syncer attributes are exported to Checkmk as labels. You must explicitly whitelist them in the [Filter](../basics/filter.md) section. The only exception are labels with the prefix `cmdbsyncer/` — these are internal helper labels used by the Syncer for optimization (e.g. rule creation) and are exported automatically.

Labels set on folders or via Checkmk rules are not touched by the Syncer and can be used freely.

## Jinja Placeholder

In all Jinja fields across the Checkmk module, the placeholder `{{ACCOUNT:name:attribute}}` is available globally. It lets you read any attribute from another account's objects by name — useful for injecting site-specific configuration into your rules.
