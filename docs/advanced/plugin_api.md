




# Syncer API
For your Plugins, please only import from syncerapi.v1
Otherwise, we can't guarantee that updates won't break something in your scripts.

## Functions
### Base:

``` python
from syncerapi.v1 import XXX
```

| Function         | Description                                                       |
| ---------------- | ----------------------------------------------------------------- |
| Host             | The Central Host Object                                           |
| get_account      | Get the Account Config by Name (Automated with Plugin Base Class) |
| register_cronjob | Register a Function to Appear as Cronjob                          |
| cc (Color Codes) | Use to Print  with nice Colors                                    |
| render_jinja     | Render given String with Jinja                                    |

### Core
```python
from syncerapi.v1.core import XXX
```

| Function   | Description                             |
| ---------- | --------------------------------------- |
| logger     | Add Custom Log Events                   |
| app        | Flask App Object                        |
| app_config | Access to the Global Config             |
| cli        | Register CLI Params                     |
| Plugin     | Base Class for your Plugins (see below) |

### Inventory
``` python
from syncerapi.v1.inventory import XXX
```
- run_invenentory

# Host Object API
The Host Object, you can use inside your Import and Export Plugins.  It's the reference to the the list of your Hosts, or to update a Single one (Host.get_host(name))
It supports the following Methods:

| Method                                          | Description                                                    |
| ----------------------------------------------- | -------------------------------------------------------------- |
| get_host(hostname)                              | Get the Host Object to add Attributes                          |
| get_export_hosts()                              | Return only Hosts, no Objects for e.g. Loop                    |
| rewrite_hostname(old_name, template, attribute) | Shortcut to render_jinja                                       |
| replace_label(key, value)                       | Replace given Label with new Value                             |
| update_host(labels)                             | Replace all Labels of host.                                    |
| update_inventory(key, inventory)                | Update hosts inventory                                         |
| get_inventory()                                 | Get hosts Inventory                                            |
| add_log(entry)                                  | Add Log Entry to Host                                          |
| set_account(config)                             | Set import Account, alsways use to check<br>if allowed to save |
| save()                                          | Save Changes you made on the object                            |


# Plugin Base Class
The Plugin() is the Base class for your Plugin. If you're using it, you can use some automatic benefits like logging and a central Request Class which can be debugged with the normal Syncer Switches.

``` python
class YourPlugin(Plugin):
	name = "Your Plugins Name (for log)"
	source = "Key used in log"

    def __init__(self, account):
        super().__init__(account)
        # Your Stuff
```
If you have your own \__init\__() just make sure to call super() in order that the e.g. the config is processed. 
## Default Methods and Variables:

| Function/ Method                          | Description                                                                                        |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------- |
| name (string)                             | The Name of the Plugin Actions (for log)                                                           |
| source (string)                           | Type of Action, usefull to filter log                                                              |
| config (dict)                             | The Accounts configuration                                                                         |
| log_details (list(tuple))                 | Append Tuples (name, details) which will later<br>appear in the log view which you have in the GUI |
| inner_request(method, url, data, headers) | Use for all HTTP Requests.<br>Has logging, makes your Plugin support save_requests and<br>dry_run  |

### Log Details

When calling **self.log_details.append(("Count", 12 ))** you can add a metric named **Count** with the Value **12** to the Log entry which is generated when you run your plugin. You can use any Name you want, you can also log every type of Object which can casted to string. But If one of your Names contains "error", the whole Log Entry is marked as error entry. This can then show UP in your Monitoring.
