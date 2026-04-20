# Manage Plugins

The `cmdbsyncer-plugin` command manages the plugins installed in your
Syncer — listing them, enabling or disabling them, and packaging or
installing third-party plugins as `.syncerplugin` bundles.

This is the administrator-facing counterpart to the
[Build your own Plugin](own_plugins.md) guide, which covers *writing* a
plugin.

!!! note
    Pip installs expose the command as `cmdbsyncer-plugin` on `PATH`.
    In a source checkout the same command is available as
    `./cmdbsyncer-plugin` from the repository root.

---

## Where Plugins Live

| Directory | Who owns it |
| --- | --- |
| `application/plugins/` | Built-in plugins that ship with the Syncer (Checkmk, Netbox, Ansible, …) |
| `plugins/` | Local plugins that you installed yourself |

`cmdbsyncer-plugin list` shows both, with a `Local` column so you can
tell which plugins you added after the fact. Only local plugins can be
removed — built-in plugins are protected from `uninstall`.

---

## Listing Plugins

```bash
cmdbsyncer-plugin list
```

Shows a table with the following columns:

| Column | Meaning |
| --- | --- |
| `Local` | `Yes` if the plugin lives under `plugins/`, `No` for built-ins |
| `Enabled` | `Yes` when the plugin is loaded on startup |
| `Ident` | The plugin's internal identifier — used by all other subcommands |
| `Name`, `Version`, `Description` | Metadata from the plugin's `plugin.json` |

Use the `Ident` value as the argument for `enable`, `disable`, `pack`
and `uninstall`.

---

## Enabling and Disabling

Plugins can be turned off without removing them. A disabled plugin is
not loaded on Syncer startup, so its CLI commands, cronjobs and admin
views disappear until it is re-enabled.

```bash
cmdbsyncer-plugin disable netbox
cmdbsyncer-plugin enable netbox
```

Disabled plugin idents are persisted in `disabled_plugins.json` in the
Syncer's working directory. Remove the file (or `enable` each entry) to
restore the default state.

!!! note
    A plugin whose own `plugin.json` sets `"enabled": false` cannot be
    enabled with `cmdbsyncer-plugin enable` — that flag is controlled
    by the plugin author. Local `disable`/`enable` only toggles the
    admin-side override.

---

## Packaging a Plugin

Package a plugin directory into a distributable tarfile:

```bash
cmdbsyncer-plugin pack myplugin
```

The command creates `myplugin-<version>.syncerplugin` in the current
directory. The version is read from `plugin.json`. You can then copy
this file to another Syncer installation and install it there.

---

## Installing from a `.syncerplugin` File

```bash
cmdbsyncer-plugin install myplugin-1.0.0.syncerplugin
```

Extracts the bundle into `plugins/`. If a plugin with the same
directory name already exists, it is replaced.

After installing, restart the Syncer so the new plugin's CLI commands,
cronjobs and admin views are picked up.

---

## Uninstalling a Local Plugin

```bash
cmdbsyncer-plugin uninstall myplugin
```

Removes the plugin directory from `plugins/`. Built-in plugins under
`application/plugins/` cannot be removed this way — the command will
report that internal plugins are protected.

---

## Typical Workflows

**Share a plugin with another Syncer instance:**

```bash
# On the source system
cmdbsyncer-plugin pack myplugin

# Copy myplugin-1.0.0.syncerplugin to the target, then:
cmdbsyncer-plugin install myplugin-1.0.0.syncerplugin
```

**Temporarily turn off a noisy plugin:**

```bash
cmdbsyncer-plugin disable jdisc
# ... investigate ...
cmdbsyncer-plugin enable jdisc
```

**Audit what is active on a Syncer:**

```bash
cmdbsyncer-plugin list
```
