# Building your own Plugin

Plugins extend the CMDBSyncer with new import/export sources, CLI commands, admin views, and REST endpoints.
Every built-in integration (Checkmk, Netbox, Ansible, …) is itself a plugin — so you can use them as reference.

!!! note
    Only import Syncer functions from `syncerapi.v1`. Importing from internal application modules directly will break when the Syncer is updated.

---

## Plugin Structure

A plugin lives in its own subfolder under `application/plugins/`:

```text
application/plugins/myplugin/
├── __init__.py        # CLI commands and cronjob registration
├── plugin.json        # Plugin metadata and account field presets
├── admin_views.py     # Flask-Admin view registration (optional)
├── models.py          # MongoEngine models (optional)
├── views.py           # Flask-Admin view classes (optional)
└── rest_api/
    └── myplugin.py    # REST API namespace (optional)
```

---

## plugin.json

The `plugin.json` is read by the Syncer on startup to register the plugin and pre-fill account fields in the UI.

```json
{
    "version": "1.0.0",
    "author": "Your Name",
    "name": "My Plugin",
    "description": "Short description",
    "ident": "myplugin",
    "account_presets": {
        "address": "https://api.example.com"
    },
    "account_custom_field_presets": {
        "verify_cert": "True",
        "some_option": ""
    },
    "enabled": true
}
```

| Field | Description |
| --- | --- |
| `ident` | Unique identifier used internally to match accounts to this plugin |
| `account_presets` | Default values for the standard account fields (address, etc.) |
| `account_custom_field_presets` | Pre-filled keys for the account's custom fields section |
| `enabled` | Set to `false` to disable the plugin without removing it |

---

## `__init__.py` — CLI Commands and Cronjobs

The `__init__.py` is the entry point. It defines CLI commands (via Click) and registers cronjobs.

A minimal example:

```python
import click
from syncerapi.v1 import Host, register_cronjob

# Define a click group for your plugin
@click.group(name='myplugin')
def cli_myplugin():
    """Commands for My Plugin"""

# Register a CLI command
@cli_myplugin.command('import_hosts')
@click.argument('account')
def import_hosts(account):
    """Import hosts from My Plugin"""
    # your import logic here
    pass

# Register the same function as a cronjob
register_cronjob('My Plugin: Import Hosts', import_hosts)
```

The CLI group name (`myplugin`) becomes the subcommand:

```bash
./cmdbsyncer myplugin import_hosts MYACCOUNT
```

The Syncer automatically discovers the CLI group from `__init__.py` and adds it to the main command.

!!! note
    Register cronjobs only for functions that accept an `account` argument as the first parameter, or no arguments at all — that is what the cronjob scheduler expects.

---

## `admin_views.py` — Admin UI

To add views to the web UI, create an `admin_views.py` with a `register_admin_views(admin)` function.
The Syncer calls this function automatically on startup if it exists.

```python
from .models import MyPluginRule
from .views import MyPluginRuleView

def register_admin_views(admin):
    """Register Flask-Admin views for My Plugin."""
    admin.add_sub_category(name="My Plugin", parent_name="Modules")

    admin.add_view(
        MyPluginRuleView(
            MyPluginRule,
            name="My Plugin Rules",
            category="My Plugin",
            menu_icon_type='fa',
            menu_icon_value='fa-cogs',
        )
    )
```

This creates a sub-menu entry under **Modules → My Plugin** in the navigation.

---

## REST API Endpoints

To expose REST API endpoints, create a `rest_api/` subfolder with a Flask-RESTX `Namespace` and register it in `__init__.py`.

**`rest_api/myplugin.py`:**

```python
from flask_restx import Namespace, Resource
from syncerapi.v1.rest import require_token

API = Namespace('myplugin')

@API.route('/')
class MyPluginApi(Resource):

    @require_token
    def get(self):
        """Return data from My Plugin"""
        return {'status': 'ok'}
```

**Register in `__init__.py`:**

```python
from syncerapi.v1.rest import API
from .rest_api.myplugin import API as myplugin_api

API.add_namespace(myplugin_api, path='/myplugin')
```

The endpoint is then available at:

```text
GET /api/v1/myplugin/
```

Use `@require_token` on every endpoint to enforce authentication. See the [API documentation](../internal_restapi/index.md) for details on authentication.

---

## Example: REST Import Plugin

The following is a complete, realistic example of a plugin that fetches hosts from a JSON REST API and imports them into the Syncer.
It uses the `Plugin` base class for HTTP requests, account config handling, and automatic logging.

### File layout

```text
application/plugins/myplugin/
├── __init__.py
├── plugin.json
└── syncer.py
```

### `plugin.json`

```json
{
    "version": "1.0.0",
    "author": "Your Name",
    "name": "My Plugin",
    "description": "Import hosts from My REST API",
    "ident": "myplugin",
    "account_presets": {
        "address": "https://api.example.com"
    },
    "account_custom_field_presets": {
        "verify_cert": "True"
    },
    "enabled": true
}
```

### `syncer.py`

```python
from syncerapi.v1 import Host, cc
from syncerapi.v1.core import Plugin


class MyPluginImport(Plugin):
    """
    Import hosts from My REST API
    """

    name = "My Plugin: Import Hosts"
    source = "myplugin_import"

    def __init__(self, account):
        super().__init__(account)
        self.base_url = self.config['address'].rstrip('/')
        self.headers = {
            'Accept': 'application/json',
            'Authorization': f"Bearer {self.config['password']}",
        }

    def run(self):
        """Fetch all hosts from the API and import them into the Syncer."""
        url = f"{self.base_url}/api/v1/hosts"
        print(f"{cc.OKBLUE} -- {cc.ENDC} Fetching hosts from {url}")

        response = self.inner_request(method="GET", url=url, headers=self.headers)

        hosts = response.json().get('hosts', [])
        self.log_details.append(('hosts_found', len(hosts)))

        imported = 0
        for entry in hosts:
            hostname = entry.get('name')
            if not hostname:
                continue

            db_host = Host.get_host(hostname)
            if not db_host:
                continue

            do_save = db_host.set_account(account_dict=self.config)
            if not do_save:
                continue

            db_host.update_host({
                'os':       entry.get('os', ''),
                'location': entry.get('location', ''),
                'status':   entry.get('status', ''),
            })

            db_host.save()
            imported += 1
            print(f"{cc.OKGREEN} +{cc.ENDC} {hostname}")

        self.log_details.append(('hosts_imported', imported))
```

### `__init__.py`

```python
import click
from application.helpers.cron import register_cronjob


@click.group(name='myplugin')
def cli_myplugin():
    """My Plugin Commands"""


def _run_import(account, debug=False):
    from .syncer import MyPluginImport
    syncer = MyPluginImport(account)
    syncer.debug = debug
    syncer.run()


@cli_myplugin.command('import_hosts')
@click.argument('account')
@click.option('--debug', is_flag=True)
def import_hosts(account, debug):
    """
    Import hosts from My Plugin

    ### Example
    _./cmdbsyncer myplugin import_hosts MYACCOUNT_
    """
    _run_import(account, debug)


register_cronjob('My Plugin: Import Hosts', _run_import)
```

### How it works

- `Plugin.__init__` loads the account config from the database into `self.config` and sets `self.verify` from the account's `verify_cert` field.
- `inner_request` handles retries, SSL verification, dry-run mode, and debug logging automatically.
- `set_account` marks the host as belonging to this import source and returns `False` if the host is already owned by a different account — in that case the host is skipped.
- `update_host` replaces all labels; `update_inventory` stores additional data under a namespaced key (`myplugin__serial`, `myplugin__model`, …).
- `log_details` entries are written to the Syncer log automatically when the plugin finishes.

For the full API reference, see [Plugin API](plugin_api.md).
