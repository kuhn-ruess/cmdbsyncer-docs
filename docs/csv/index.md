# Functions with CSV Files

CSV options are available via the CLI with _./cmdbsyncer csv_.
They are used to add information to your hosts which you don't get from your CMDB,
or to manage hosts via a CSV file.

A real-world scenario is that not all hosts have made it into the CMDB yet, and until then the Syncer gets them from a CSV.

## CSV Format

As of default, you need to separate the fields by ;, and have a Column named host, which contains your Hostname.

All Other Columns, will be translated into either inventory (with key as prefix) or Labels. This depends on if you Import Hosts (means they are managed by the CSV), or Inventorize Hosts (means only extra Inventory Information is added to existing hosts).

Example:

```text
host;label_name1;label_name2
srvlx100;content1;content2
```

This means we would have a host: srvlx100 with labels: label_name1:content1, labels_name2:content2

## Account Settings

Create an account for each CSV source. The account holds the file configuration and enables features like _is_master_ (to let another plugin overtake the import).

Configure these settings as Custom Fields on the account:

- `csv_path` — path to the CSV file (required)
- `delimiter` — field separator (default: `;`)
- `hostname_field` — column name containing the hostname (default: `host`)
- `key` — inventory key prefix (only needed for `inventorize_hosts`)

## Running CSV Commands

Pass the account name as a positional argument:

```bash
./cmdbsyncer csv import_hosts my-csv-account
./cmdbsyncer csv inventorize_hosts my-csv-account
```

Add `--debug` to see detailed output:

```bash
./cmdbsyncer csv import_hosts my-csv-account --debug
```

## Legacy Mode

If you have not set up an account yet, you can pass the file path directly using `--legacy`. This bypasses account configuration entirely:

```bash
./cmdbsyncer csv import_hosts --legacy /path/to/file.csv
./cmdbsyncer csv inventorize_hosts --legacy /path/to/file.csv --key my_inventory_key
```

Note: `--legacy` and an account name are mutually exclusive. One of the two is always required.

## Comparing Hosts

To check which hosts from a CSV are not yet in the syncer database:

```bash
./cmdbsyncer csv compare_hosts /path/to/file.csv --delimiter ';'
```

## Encoding

If you have encoding problems when importing, go to the account settings and change the encoding from `utf-8` to `utf-8-sig`.
This happens mostly when exporting from excel.
