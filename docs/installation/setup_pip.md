# Installation from PyPI

Starting with version 3.12.7 the Syncer is published on the Python Package
Index. This is the quickest way to install the application into an existing
Python environment without cloning the repository.

## When to Use This Method

Use `pip install` when you want a lightweight install into your own Python
environment, for example on a bastion host that already runs MongoDB, or
inside a container image that you build yourself.

For most production setups the Docker Compose or Git-based installation is
still the better fit because it ships the helper scripts, the Apache/uWSGI
examples, the Ansible playbooks and the sample `local_config.py` in one go.

## Limitations

Before you choose this method, make sure you understand what is *not*
included in the PyPI distribution:

| Item                        | Included? | Notes                                                |
| --------------------------- | --------- | ---------------------------------------------------- |
| Core application + web UI   | Yes       | `application` package with templates and static data |
| `syncerapi` (plugin API)    | Yes       | Shipped alongside the application                    |
| `cmdbsyncer` CLI            | Yes       | Registered as a console script                       |
| `cmdbsyncer-plugin` CLI     | Yes       | Plugin packaging / install helper                    |
| Ansible requirements        | No        | Install separately (see below)                       |
| Extras (ODBC, LDAP, vmware) | No        | Install separately (see below)                       |
| `docker-compose.*.yml`      | No        | Only in the Git repository                           |
| `helper` shell wrapper      | No        | Only in the Git repository                           |
| `gunicorn` / `mod_wsgi`     | No        | Choose and install your preferred WSGI server        |

## Requirements

- Python **3.14 or newer**
- Running MongoDB instance (see
  [MongoDB section in the Apache setup guide](install_wsgi.md#mongodb))
- A writable working directory that holds your `local_config.py`

## Install the Package

Create a clean virtual environment and install from PyPI:

```bash
python3.14 -m venv ENV
source ENV/bin/activate
pip install cmdbsyncer
```

After the install, the following commands are on your `PATH`:

- `cmdbsyncer` — the main application CLI (Flask Click commands, plugin
  subcommands, shell access)
- `cmdbsyncer-plugin` — plugin packaging and install helper (formerly `./sp`)

## Optional Dependency Groups

The platform-heavy groups are not pulled in by the default install because
they would need system libraries such as libldap, ODBC, Kerberos and the
vmware SDK. Install them explicitly if you need them.

Ansible integration:

```bash
pip install kerberos pykerberos pywinrm ntlm-auth ansible
```

Database and extra integrations:

```bash
pip install python-ldap markdown-it-py pypyodbc sqlserverport \
    mysql-connector-python pyvim pyvmomi
```

The exact version pins are tracked in `requirements-ansible.txt` and
`requirements-extras.txt` in the
[Git repository](https://github.com/kuhn-ruess/cmdbsyncer).

## Initialize the Application

Pick a working directory for the deployment (for example `/opt/cmdbsyncer`).
Every call to `cmdbsyncer` expects to be run from this directory — it is
where `local_config.py` lives and where plugin files and logs are written.

With MongoDB running, seed the installation:

```bash
cd /opt/cmdbsyncer
cmdbsyncer sys self_configure
```

The command creates `local_config.py` if it is missing, generates a random
`SECRET_KEY` and a Fernet `CRYPTOGRAPHY_KEY`, seeds default values into the
database and writes the effective config back to disk. Run it again after
every update so newly added defaults are applied.

!!! warning
    Treat `local_config.py` like a secret. It contains the Fernet key that
    decrypts every stored credential in the database. Back it up together
    with your MongoDB data or you will lose access to saved credentials.

## Customize the Configuration

The default MongoDB connection is `127.0.0.1:27017`, database `cmdb-api`.
To point the Syncer at a different server, either set the
`CMDBSYNCER_MONGODB_*` environment variables before starting `cmdbsyncer`
or edit `MONGODB_SETTINGS` in `local_config.py` after the first
`self_configure` run. The full list of supported keys — including the
MongoDB overrides — is documented in
[Local Config](../basics/lcl_config.md).

## Start an Interactive Shell

To open a Python REPL with the application context pre-loaded:

```bash
cmdbsyncer shell
```

You now have access to the Flask `app`, the `db` connection and every
MongoEngine model registered by the application. See
[Interactive Shell](../basics/syncer_shell.md) for useful recipes.

## Production Deployment

PyPI installs do not ship a WSGI server. Install the server of your
choice separately — gunicorn is the default for the Docker image and a
good starting point:

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:9090 --workers 2 --threads 2 app:app
```

For Apache-based production setups follow
[Installation with Apache](install_wsgi.md). The WSGI entry point is
`application:app`.

## Updates

To upgrade to a newer release:

```bash
pip install --upgrade cmdbsyncer
cmdbsyncer sys self_configure
```

The `self_configure` run is important after upgrades because it seeds
any new default values introduced by the release.
