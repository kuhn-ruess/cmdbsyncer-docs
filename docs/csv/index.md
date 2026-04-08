# Functions with CSV Files

CSV options are available via the CLI with _./cmdbsyncer csv_.
They are used to add information to your hosts which you don't get from your CMDB,
or to manage hosts via a CSV file.

A real-world scenario is that not all hosts have made it into the CMDB yet, and until then the Syncer gets them from a CSV.


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
Instead of passing command line options, we recommend creating an account for each file.
This not only simplifies the command line, but also enables the Syncer to use the *is_master* feature, which lets another plugin overtake the import.

You can use the following Settings as Custom Fields:

- hostname_field
- delimiter
- csv_path (required)
- key (only in case of inventory needed)

## Command line Options

For Historic reasons, this Module was never meant to be configured via accounts.
Therefore, as default the CLI accepts all the Options as Parameters. To use with an account, use `--account` to specify them.

## Export all Hosts as CSV

Since Version 3.12.3, the host list view provides a hidden CSV export endpoint. Just append `/csv` to the host admin URL:

```
/admin/host/csv
```

This exports all hosts with their current attributes as a CSV file.

## CSV files and Excel → Encoding
If you have encoding problems when importing, it's worth trying to go to the account settings and change the encoding from `utf-8` to `utf-8-sig`.

