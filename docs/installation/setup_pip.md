# Installation from PyPI

The Syncer is published on the Python Package Index. Installing it with
pip into a venv, served by Gunicorn behind an Apache reverse proxy, is the
recommended installation. To run it in containers instead, see
[Installation with Docker](setup_docker.md).

## Requirements

A running MongoDB 8.0, see [MongoDB](mongodb.md), and Python **3.14 or
newer** with venv support:

=== "RedHat / Rocky / Alma"
    ```bash
    sudo dnf install -y python3.14
    ```

=== "Ubuntu / Debian"
    ```bash
    sudo apt install -y python3.14 python3.14-venv
    ```

## Service User and Working Directory

The Syncer runs as the system user **`cmdbsyncer`** from the working
directory **`/opt/cmdbsyncer`**, which holds the venv, `local_config.py`,
the `plugins/` folder and the log files. If you choose another path,
replace it consistently in the rest of this guide.

```bash
sudo useradd --system --home-dir /opt/cmdbsyncer --shell /usr/sbin/nologin cmdbsyncer
sudo mkdir -p /opt/cmdbsyncer
sudo chown cmdbsyncer: /opt/cmdbsyncer
```

Install, configure and update the Syncer as this user, so every file
belongs to the account the service runs under. The user has no login
shell, so open one explicitly:

```bash
sudo -u cmdbsyncer -H bash
cd /opt/cmdbsyncer
```

All `python`, `pip` and `cmdbsyncer` commands below run in this shell.
Commands prefixed with `sudo` run from your admin account.

## Install the Package

```bash
python3.14 -m venv venv
source venv/bin/activate
pip install cmdbsyncer
```

This puts three commands on the `PATH`: `cmdbsyncer` (the application
CLI), `cmdbsyncer-plugin` (plugin packaging and install helper) and
`cmdbsyncer-mcp` (Model Context Protocol server, needs the `extras`
group).

### Optional Dependency Groups

Groups that need system libraries (libldap, ODBC, Kerberos, the vmware
SDK) are pip **extras**:

```bash
# LDAP, MS-SQL / MySQL, vmware SDK, MCP server
pip install 'cmdbsyncer[extras]'

# Ansible for Linux / SSH targets
pip install 'cmdbsyncer[ansible]'

# Ansible Windows targets (WinRM + Kerberos/NTLM; needs system Kerberos libs)
pip install 'cmdbsyncer[ansible-windows]'

# Several at once
pip install 'cmdbsyncer[extras,ansible,ansible-windows]'
```

The extras read their pins from `requirements-extras.txt`,
`requirements-ansible.txt` and `requirements-ansible-windows.txt` in the
[Git repository](https://github.com/kuhn-ruess/cmdbsyncer).

!!! note "Default playbooks are not part of the PyPI package"
    Pull the reference playbooks onto your node after install:
    ```bash
    cmdbsyncer sys install_playbooks ./ansible
    ```
    Details: [Playbooks via PyPI Install](../ansible/playbooks_pypi.md). For a remote Ansible control node, see the [cmdbsyncer-inventory](../ansible/cmdbsyncer_inventory.md) plugin instead.

### Install from a Built Wheel

To install a version that is not on PyPI, for example the current
state of a branch, build the wheel from a checkout of the
[Git repository](https://github.com/kuhn-ruess/cmdbsyncer):

```bash
git clone https://github.com/kuhn-ruess/cmdbsyncer.git
cd cmdbsyncer
python3.14 -m venv venv
venv/bin/pip install build
make build
```

`make build` writes `cmdbsyncer-<version>-py3-none-any.whl` into
`dist/`. The wheel holds the complete application, so it is the one file
to copy to `/opt/cmdbsyncer` on the target host. Install it there in
place of `pip install cmdbsyncer`, extras work the same way:

```bash
pip install './cmdbsyncer-<version>-py3-none-any.whl[extras]'
```

pip still downloads the dependencies from PyPI. For a host without
internet access use the [Offline Installation](setup_offline.md)
bundle, its `--syncer-from-git` option packs a wheel built from the
checkout together with all dependencies.

## Initialize the Application

With MongoDB running, seed the installation and create the first login:

```bash
cmdbsyncer sys self_configure
cmdbsyncer sys create_user mail@example.com
```

`self_configure` creates `local_config.py` if it is missing, generates a
random `SECRET_KEY` and a Fernet `CRYPTOGRAPHY_KEY`, seeds default values
into the database and writes the effective config back to disk. It does
**not** create a login, hence `create_user`; see
[Local Users](authentication.md) for its options.

!!! warning
    Treat `local_config.py` like a secret. It contains the Fernet key that
    decrypts every stored credential in the database. Back it up together
    with your MongoDB data or you will lose access to saved credentials.

`cmdbsyncer cli` opens an interactive shell with tab completion and
history, see [Interactive Shell](../basics/syncer_shell.md).

## Production Deployment

PyPI installs do not ship a WSGI server. Gunicorn serves the
`application:app` WSGI callable, systemd keeps it running and Apache
forwards the requests to it.

### Gunicorn via systemd

Gunicorn is the default for the Docker image. Install it in the venv
and run a quick foreground check, still in the service-user shell:

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:9090 --workers 2 --threads 2 application:app
```

Stop it with `Ctrl+C` and leave the service-user shell with `exit`.
Then create `/etc/systemd/system/cmdbsyncer.service`. `WorkingDirectory`
must be the folder that contains `local_config.py`:

```ini
[Unit]
Description=CMDB Syncer (Gunicorn)
After=network.target mongod.service
Requires=mongod.service

[Service]
Type=simple
User=cmdbsyncer
WorkingDirectory=/opt/cmdbsyncer
Environment=config=prod
ExecStart=/opt/cmdbsyncer/venv/bin/gunicorn \
    --bind 127.0.0.1:9090 \
    --workers 2 --threads 2 \
    --access-logfile - \
    --error-logfile - \
    application:app
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now cmdbsyncer
sudo systemctl status cmdbsyncer
sudo journalctl -u cmdbsyncer -f
```

### Apache Reverse Proxy

Gunicorn listens on `127.0.0.1:9090` only. Apache forwards the requests
to it, either through **its own virtual host** or under the **sub-path
`/cmdbsyncer`** of an Apache that already serves other sites. Pick one
of the two. TLS is configured in Apache as for any other site and is
not covered here.

Install Apache with the proxy modules, unless it is already running,
and allow it to connect to Gunicorn:

=== "RedHat / Rocky / Alma"
    SELinux blocks outgoing connections from Apache by default:
    ```bash
    sudo dnf install -y httpd
    sudo setsebool -P httpd_can_network_connect 1
    ```

=== "Ubuntu / Debian"
    ```bash
    sudo apt install -y apache2
    sudo a2enmod proxy proxy_http headers
    ```

In both variants, add `TRUSTED_PROXIES` to the existing `config`
dictionary in `/opt/cmdbsyncer/local_config.py`:

```python
config = {
    # ... keys written by self_configure ...
    'TRUSTED_PROXIES': 1,
}
```

Only then does the Syncer trust the `X-Forwarded-*` headers from Apache
and recognise HTTPS requests as such; without it, password-based API
auth stays blocked.

#### Variant 1: Own Virtual Host

The Syncer gets its own host name and is reachable at
`http://cmdb.example.com/`:

```apache
<VirtualHost *:80>
    ServerName cmdb.example.com
    ProxyPreserveHost On
    RequestHeader set X-Forwarded-Proto expr=%{REQUEST_SCHEME}
    ProxyPass        /  http://127.0.0.1:9090/
    ProxyPassReverse /  http://127.0.0.1:9090/
</VirtualHost>
```

=== "RedHat / Rocky / Alma"
    Save it as `/etc/httpd/conf.d/cmdbsyncer.conf`, then:
    ```bash
    sudo firewall-cmd --permanent --add-service=http
    sudo firewall-cmd --reload
    sudo systemctl enable --now httpd
    ```

=== "Ubuntu / Debian"
    Save it as `/etc/apache2/sites-available/cmdbsyncer.conf`, then:
    ```bash
    sudo a2ensite cmdbsyncer
    sudo systemctl reload apache2
    ```

#### Variant 2: Sub-Path on an Existing Apache

The Syncer runs next to the existing sites and is reachable at
`https://<your-host>/cmdbsyncer/`, no own host name or virtual host
needed. The prefix `/cmdbsyncer` has to be set in three places.

**1. Syncer:** add `BASE_PREFIX` to the `config` dictionary in
`/opt/cmdbsyncer/local_config.py`, next to `TRUSTED_PROXIES`:

```python
config = {
    # ... keys written by self_configure ...
    'TRUSTED_PROXIES': 1,
    'BASE_PREFIX': '/cmdbsyncer/',
}
```

**2. Gunicorn:** Gunicorn has to know the prefix too, it strips it from
incoming paths and adds it to every link it generates. In
`/etc/systemd/system/cmdbsyncer.service`, add a second `Environment`
line below the existing one:

```ini
Environment=config=prod
Environment=SCRIPT_NAME=/cmdbsyncer
```

Then reload systemd and restart the service:

```bash
sudo systemctl daemon-reload
sudo systemctl restart cmdbsyncer
```

**3. Apache:** forward `/cmdbsyncer` to Gunicorn, keeping the prefix:

```apache
ProxyPass        /cmdbsyncer  http://127.0.0.1:9090/cmdbsyncer
ProxyPassReverse /cmdbsyncer  http://127.0.0.1:9090/cmdbsyncer
<Location /cmdbsyncer>
    RequestHeader set X-Forwarded-Proto expr=%{REQUEST_SCHEME}
</Location>
```

=== "RedHat / Rocky / Alma"
    Save it as `/etc/httpd/conf.d/cmdbsyncer.conf`, then:
    ```bash
    sudo systemctl reload httpd
    ```

=== "Ubuntu / Debian"
    Save it as `/etc/apache2/conf-available/cmdbsyncer.conf`, then:
    ```bash
    sudo a2enconf cmdbsyncer
    sudo systemctl reload apache2
    ```

Files in these directories apply to every virtual host. To limit the
Syncer to one site, put the block into that site's `<VirtualHost>`
instead.

## Updates

Upgrade as the service user, re-run `self_configure` to seed the
defaults of the new release, then restart the service:

```bash
sudo -u cmdbsyncer -H bash
cd /opt/cmdbsyncer
source venv/bin/activate
pip install --upgrade cmdbsyncer
cmdbsyncer sys self_configure
exit
sudo systemctl restart cmdbsyncer
```
