# Plugin API

For your plugins, only import from `syncerapi.v1` and its sub-modules.
Importing directly from `application.*` is not supported and will break on updates.

---

## `syncerapi.v1`

```python
from syncerapi.v1 import Host, get_account, register_cronjob, cc, render_jinja
```

| Name | Description |
| --- | --- |
| `Host` | The central host object — see [Host Object API](#host-object-api) below |
| `get_account(name)` | Returns the account config dict for the given account name, or `None` |
| `register_cronjob(name, func)` | Register a function to appear as a schedulable cronjob in the UI |
| `cc` | `ColorCodes` — constants for colored terminal output (`cc.OKBLUE`, `cc.FAIL`, `cc.ENDC`, …) |
| `render_jinja(template, **kwargs)` | Render a Jinja template string with the given variables |

---

## `syncerapi.v1.core`

```python
from syncerapi.v1.core import logger, app, app_config, cli, Plugin
```

| Name | Description |
| --- | --- |
| `logger` | Standard Python logger — use for debug/info messages |
| `app` | The Flask application object |
| `app_config` | Direct access to `app.config` (the global configuration dict) |
| `cli` | The Flask CLI object — use to register top-level CLI commands |
| `Plugin` | Base class for plugins — see [Plugin Base Class](#plugin-base-class) below |

---

## `syncerapi.v1.inventory`

```python
from syncerapi.v1.inventory import run_inventory
```

| Name | Description |
| --- | --- |
| `run_inventory(account, config)` | Execute an inventory run for the given account |

---

## `syncerapi.v1.rest`

```python
from syncerapi.v1.rest import API, require_token
```

| Name | Description |
| --- | --- |
| `API` | The Flask-RESTX `Api` instance — use `API.add_namespace(ns, path='/...')` to register REST endpoints |
| `require_token` | Decorator to protect REST endpoints with API authentication |

See [Building your own Plugin](own_plugins.md#rest-api-endpoints) for a usage example.

---

## Host Object API

The `Host` object represents a single host in the database.
It is used both to look up existing hosts and to create new ones.

### Static / Class Methods

| Method | Description |
| --- | --- |
| `Host.get_host(hostname, create=True)` | Return the host object for the given hostname. Creates a new (unsaved) object if it does not exist and `create=True`. Returns `False` for empty or invalid names. |
| `Host.get_export_hosts()` | Return a queryset of all hosts that are available for export (not objects, not disabled). |
| `Host.rewrite_hostname(old_name, template, attributes)` | Render a new hostname from a Jinja template string with the given attributes dict. |

### Instance Methods

| Method | Description |
| --- | --- |
| `update_host(labels)` | Replace all labels on the host with the given dict. Applies key normalization (lowercase, replacers) and only triggers a sync timestamp update if labels actually changed. |
| `replace_label(key, value)` | Set or update a single label without touching the others. Clears the attribute cache if the value changed. |
| `get_labels()` | Return all labels as a dict. |
| `update_inventory(key, new_data)` | Update the inventory section identified by `key`. All existing entries for that key are replaced with `new_data`. Keys are stored as `key__fieldname`. Pass an empty dict to clear the section. |
| `set_inventory_attribute(key, value)` | Set a single inventory key/value pair and immediately save the host. |
| `get_inventory(key_filter=False)` | Return the full inventory dict, or only entries whose key starts with `key_filter`. |
| `set_account(account_dict=...)` | Mark the host as belonging to the given account. Prevents overwrites from other import sources. Pass the full account dict from `get_account()`. Returns `False` if the host is locked (CMDB mode). |
| `add_log(entry)` | Append a log message to the host's log history (visible in the host detail view in the UI). |
| `save()` | Persist all changes to the database. Always call this after modifying a host. |

!!! warning
    `set_labels()` is deprecated and raises an error. Use `update_host(labels)` instead.

### Example: Import

```python
from syncerapi.v1 import Host, get_account

account_config = get_account('my_account')

db_host = Host.get_host('server01.example.com')
if db_host:
    db_host.set_account(account_dict=account_config)
    db_host.update_host({'os': 'linux', 'location': 'dc1'})
    db_host.update_inventory('myplugin', {'serial': 'ABC123'})
    db_host.save()
```

---

## Plugin Base Class

For plugins that need HTTP requests, logging, and account config handling, inherit from `Plugin`.

```python
from syncerapi.v1.core import Plugin

class MyPlugin(Plugin):
    name = "My Plugin"   # shown in the log view
    source = "myplugin"  # used to filter log entries

    def __init__(self, account):
        super().__init__(account)
        # self.config is now populated from the account
```

### Class Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| `name` | `str` | Human-readable name, shown in the Syncer log |
| `source` | `str` | Log source key — used to filter log entries. Defaults to the class name. |
| `config` | `dict` | Account configuration, populated by `__init__` when an account is passed |
| `log_details` | `list` | List of `(name, value)` tuples appended during the run — written to the log on exit |
| `debug` | `bool` | Enables debug output |
| `dry_run` | `bool` | When `True`, write requests are skipped |
| `save_requests` | `str` | File path — when set, all HTTP requests are written to this file |
| `verify` | `bool` | SSL certificate verification for HTTP requests. Read from the account config automatically. |

### Methods

| Method | Description |
| --- | --- |
| `inner_request(method, url, data, json, headers, auth, params, cert)` | Execute an HTTP request with automatic retry, timeout handling, SSL config, dry-run support, and debug logging. Returns a `requests.Response` object. |
| `get_attributes(db_host, cache)` | Return the full processed attribute set for a host (`{'all': ..., 'filtered': ...}`). Applies rewrite, filter, and custom attribute rules. Returns `False` if the host is filtered out. Pass a cache key string to enable caching. |
| `init_custom_attributes()` | Load and initialize the custom attribute rules. Called automatically by `get_attributes()`. |
| `debug_rules(hostname, model)` | Print rule debug output for a given hostname. Used by `--debug-rules` CLI switches. |
| `get_unique_id()` | Return a unique UUID string, usable as an import ID. |
| `save_log()` | Write all collected `log_details` to the Syncer log. Called automatically at process exit via `atexit`. |

### Log Details

`log_details` is a list of `(name, value)` tuples that are written to the log entry when the plugin finishes.
You can append to it at any point during the run:

```python
self.log_details.append(('hosts_processed', 42))
self.log_details.append(('hosts_skipped', 3))
```

If any entry's name contains `"error"` or `"exception"` (case-insensitive), the entire log entry is marked as an error — which can trigger monitoring alerts.

```python
self.log_details.append(('error', f"Failed to connect: {e}"))
```
