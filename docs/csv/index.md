# Functions with CSV Files

CSV Options are CLI only and can be access with _./cmdbsyncer csv_
They are used, to add Information to your Hosts, which you don't get from your CMDB,
or even Mange hosts by a CSV File. 

Real live scenario here are that no all hosts have made it into the CMDB, and until then the Syncer gets them from a CSV. 


## CSV Format

As of default, you need to separate the fields by ;, and have a Column named host, which contains your Hostname. 

All Other Columns, will be translated into either inventory (with key as prefix) or Labels. This depends on if you Import Hosts (means they are managed by the CSV), or Inventorize Hosts (means only extra Inventory Information is added to existing hosts).

Example:
```
host;label_name1;label_name2
srvlx100;content1;content2
```

This means we would have a host: srvlx100 with labels: label_name1:content1, labels_name2:content2

## Account Settings
Instead of passing Command Line Options, we recommend creating a Account for each file.
This not only simplifiess the command line, but also enables the Syncer to use the *is_master* feature. This feature for can let another Plugin overtake the import from the field. 

You can use the following Settings as Custom Fields:

- hostname_field
- delimiter
- csv_path (required)
- key (only in case of inventory needed)

## Command line Options

For Historic reasons, this Module was never meant to be configured via accounts.
Therefore, as default the CLI accepts all the Options as Parameters. To use with an account, use `--account` to specify them.

## CSV files and Excel → Encoding
If you have Coding Problems when importing, it's worth a try going to the Accounts settings and change the Encoding from `utf-8`to `utf-8-sig`

