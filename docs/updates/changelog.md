# Changelog

## General when Update
Please always check before you update here, if there are changes you need to consider.

After always, please run:
```
./cmdbsyncer sys self_configure
```
This will automatically adapt config changes if needed, and add needed default values to the local_config.py if you don't have them. For example, the Cryptography key.

## To Version 3.11
IMPORTANT: Minmal required Python Version is now 3.10
The Syncer uses now a new Plugin Structure. All plugins are migrated, and tested as good as possible.


## To Version 3.10
The authentication for the REST API now works only with users, no longer with accounts  You need to adapt all your scripts that are working with the Syncer Rest API.
This change is required because it's planned to implement a permission management for the API later.


## To Version 3.9
If you had Checkmk Custom Attribute Rules, which created multiple outputs because you did a comma seperation, the seperation sign changed from comma to double (\|\|) pipes.
Please adapt your rules after Update

Also, all account passwords are now encrypted. If you run self_configure, everything will be migrated automatically. 

## To Version 3.8

### Format of Imported Data
Before 3.8, every imported Label Value was converted to a String. That was fine in the beginning with simple Labels. But since more and more Jinja is used, it was a pain that Data structures, like Lists and Dicts, first had to be converted back from their string state. 
This Conversation does not happen anymore. A dict stays a dict, a list stays a list.
But also, a None, False or True, stays like that. 
Does this affect you: In short: No.
Because if you us normal matches, the value will still convert to a string for this match.
Only if you set to Bool Match, the bool stays like the origin. Although the Bool Match even can convert the strings of True, None or False back. So nothing to worry about.
But why then, this all?
In Jinja Templates, you now have all the Flexibility you need to customize Data, Loop etc.pp to your need. 

### Mongodb Update
This only applies if you're using the docker-compose files shipped with the Syncer. Otherwise, you can skip that Part. The Version of Mongo Updates from 4.4 to 7.0.14 You can either Back up your Data with the Syncers export function and start with and Empty Database again. Or just first change the MongoDB Version in the Docker File to 5.0, start and login to Syncer, then 6.0, start and login to Syncer and finally to the 7.0.14.  In the Future I will directly add the new Versions the moment they are Stable. So there will not be such a Big Step anymore.


### Netbox
The Netbox Module is completely rewritten and therefore more flexible and simpler to use. But the catch is, that you need to update your rules. In short:  For Attributes you need to use Jinja Syntax {{ATTRIBUTE}} and no need for Netbox ID's anymore, you can directly use the Name.
If you have a manual setup, make sure to update the python requirements. A new requirement is pynetbox.

#### VM Import
The Import of VMs from Inbox is not longer part of the device import.
It's an own command which has to be set. Also, since now pynetbox is used, it's possible that attribute names change. 

## To Version 3.7

After Update, please commit the changes, otherwise there will be an exception on Checkmk Export

### General
- GUI: Simplified Interface, clearer Descriptions in Menu
- Export of Hosts and Tags to Checkmk, use now all available Processing Power to calculate Rules before importing.
- Bulk Operations for Checkmk are now Enable as Default


#### Supported Versions
- Checkmk: API Calls are Adapted to Checkmk 2.3 and some functions may not work on 2.2
	- Checkmk Rules: On 2.2 the rules will delete and created again all the time due an API change in Checkmk. 
- SET local_config: 'CMK_SUPPORT': '2.2' to make version better compatible to old 2.2


### Interaction Needed
- **CSV**: On Import, Hostnames are only set to lowercase if set in local_config.py. No longer as Default. See [Local Config](../basics/lcl_config.md)
- **MySQL**: On Import, Hostnames are only set to lowercase if set in local_config.py. No longer as Default. See [Local Config](../basics/lcl_config.md)
- **Mssql**: On Import, Hostnames are only set to lowercase if set in local_config.py. No longer as Default. See [Local Config](../basics/lcl_config.md)
- **Checkmk**: Export Rule Value of Folder is deprecated. Replaced by Jinja Support of normal Move Folder Rule.
- **General**: Jina Placeholder for Hostsname is now always Uppercase HOSTNAME.
- **Checkmk**: The Checkmk API once allowed, accidentally, that a host could be converted to a cluster. Since that is no longer possible, the Syncer now deletes hosts which should become a cluster to recreate them as such.
- **General**: Config introduced "CRYPTOGRAPHY_KEY". Please overwrite it, since it is used to encrypt stored passwords in the database
- **CRON**: The Maintenance Cronjob had a Typo. After Update, you need to reelect this command in the config of the cron group. 

### New Features
- **Checkmk**:Folder names can now set that they will not be lowercase to keep their case. See [Checkmk Config](../checkmk/config_vars.md)
- **Checkmk**: Folders can now get Attributes and Different Names, managed by Syncer.
- **Checkmk**: Move to Folder Rule now Supports full Jinja and Replaces Value of Folder rule
- **Checkmk**: It's possible to create folders but not move the host in
- **Checkmk**: The Debug Page shows now the Rule Debug was before only was possible in cli
- **Checkmk**: Export --dry-run and --save-requests to test or just save needed actions to run them later or archive them
- **Checkmk**: Support to Manage DCD (Dynamic Configuration) Rules
- **Checkmk**: Support to manage Password Store
- **Checkmk**: Detailed logging (if enabled) for changes made
- **Global**: Changes on Import hosts for Labels are now logged inside the Host Objects log
- **LDAP**: Added Support for Inventorize


### Minor Changes
- **Checkmk**: Modul for Checkmk Rules now supports Jinja for Folder names


## To Version 3.5

Version 3.5 is a Major Update which updates all required Python Modules and also 
resolves older problems which can't be resolved staying compatible. So your help is needed for this one. 

These steps are only needed for the first time when you update from pre 3.5 Versions. Also when you skip 3.5 or you're working with the git versions. 

### 1) requirements.txt
The Requirements txt is now divided in 3 Files.

- requirements.txt → All you need to run the Syncer
- requirements-extras.txt → Modules like ldap/ mysql which not all users need
- requirements-ansible.txt → Everything needed for the Ansible automations

Note: If you're using Docker, all Modules are installed automatically.

### 2) Module Updates
Due to Security problems in some of the Modules,  we had to upgrade all Modules of the Framework. So after Update of the Syncers code, you need to run the pip install -r requirements.txt again. Nothing more to-do.

### 3) Inventory Prefix
In the past, inventory values were prefixed like name_ something.
This is now changed to name__. The Problem with the old approach:
cmk_ vs cmk_svc_. If you now want to clean the cache, and delete everting starting with cmk_,
you will also delete the namespace cmk_svc.
This effects only rules later, you created based on inventorized data. Normal Attributes from imports are not affected.

Steps for the migration:

- Delete current Inventory: ./cmdbsyncer sys delete_inventory
- Run your inventories again
- Update the rules wich are based on Inventory Data and fix the naming. 
	- cmk_ goes cmk__
	- cmk_svc_ goes cmk_svc__
	- csv_ goes csv__
	- and so on


### 4) Checkmk: Create Tags
The function is now simpler and has more power at the same time.
Only Change: Instead specify a for each and refer to {{name}}, you can directly refer to the attribute.


### 5) dns:service dhcp:service Attributes
In the first Version of the Syncer, there was a limit to key:value for attributes.
That lead to lists where key and values were switched, to allow multiple entries.
With this Version, attributes can be not only key:string but also key:list or key:dict.  You can use that in your plugins, in case you use the outcome in jinja Templates.
Example: service:['dns', 'dhcp'] could in jinja be:
{{ service[0] }} or: {% for svc in service %} as loop. 
