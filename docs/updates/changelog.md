# Changelog

## To Version 3.7

### General
- Export of Hosts and Tags to Checkmk, use now all available Processing Power to calculate Rules before importing.
- Bulk Operations for Checkmk are now Enable as Default


### Interaction Needed
- **CSV**: On Import, Hostnames are only set to lowercase if set in local_config.py. No longer as Default. See [Local Config](/basics/lcl_config)
- **MySQL**: On Import, Hostnames are only set to lowercase if set in local_config.py. No longer as Default. See [Local Config](/basics/lcl_config)
- **Mssql**: On Import, Hostnames are only set to lowercase if set in local_config.py. No longer as Default. See [Local Config](/basics/lcl_config)

### New Features
- **Checkmk**:Folder names can now set that they will not be lowercase to keep their case. See [Checkmk Config](/checkmk/config_vars/)
- **Checkmk**: Folders can now get Attributes and Different Names, managed by Syncer.


## Minor Changes
- **Checkmk**: Modul for Checkmk Rules now supports Jinja for Folder names
