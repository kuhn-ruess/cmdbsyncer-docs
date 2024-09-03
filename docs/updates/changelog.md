# Changelog

## General when Update
Please always check before you update here, if there are changes you need to consider.

After always, please run:
```
./cmdbsyncer sys self_configure
```
This will automatically adapt config changes if needed, and add needed default values to the local_config.py if you don't have them. For example, the Cryptography key.

## To Version 3.7

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
