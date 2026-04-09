# Fileadmin

The Fileadmin is a built-in file manager accessible from the web interface under **Filemanager**. It lets you upload and manage files on the server without needing shell access — useful for CA certificates, CSV files, YAML configs, and any other files your accounts or rules reference.

## Enabling the Fileadmin

The Fileadmin is enabled automatically as soon as its working directory exists. Create it on the server:

```bash
mkdir -p /srv/cmdbsyncer-files
chown <syncer-user> /srv/cmdbsyncer-files
```

To use a different path — recommended when running Docker with a mounted volume — set `FILEADMIN_PATH` in `local_config.py`:

```python
config = {
    'FILEADMIN_PATH': '/data/files',
}
```

In Docker, mount the directory as a volume so files persist across container restarts:

```yaml
volumes:
  - /data/files:/data/files
```

→ [App Configuration](lcl_config.md)

## Supported File Types

| Operation | Supported Extensions                                    |
| :-------- | :------------------------------------------------------ |
| Upload    | `.md`, `.txt`, `.csv`, `.yml`, `.json`, `.pem`, `.cert` |
| Edit      | `.md`, `.txt`, `.csv`, `.yml`, `.json`, `.pem`          |

## Features

- **Upload** files directly from the browser
- **Edit** text-based files in-browser (CSV, YAML, JSON, PEM, etc.)
- **Rename** and **create subdirectories** to organize files
- **Full path display** — the absolute server path for each file is shown in the list, so you can copy it directly into account settings (e.g. CA certificate fields) without guessing paths

## Permissions

Access to the Fileadmin is controlled by user rights. A user needs the **fileadmin** permission to see and use the Filemanager in the navigation.

## Common Use Cases

- Upload CA certificate files (`.pem`, `.cert`) and copy their path into the [SSL certificate fields](accounts.md#ssl-certificate-verification) of an account
- Manage CSV import files without shell access
- Store YAML or JSON configuration files referenced by import plugins
