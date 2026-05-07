# Installation from PyPI

Starting with version 3.12.7 the Syncer is published on the Python Package
Index. This is the quickest way to install the application into an existing
Python environment without cloning the repository.

## When to Use This Method

Use `pip install` when you want a lightweight (but full functional) install into your own Python
environment, for example on a bastion host that already runs MongoDB, or
inside a container image that you build yourself.

For most production setups the Docker Compose or Git-based installation is
still the better fit because it ships the helper scripts, the Apache/uWSGI
examples, and the Ansible playbooks.

## Requirements

- Python **3.14 or newer**
- Running MongoDB instance (see
  [MongoDB section in the Apache setup guide](install_wsgi.md#mongodb))
- A writable working directory that holds your `local_config.py`

## Working Directory Convention

All examples in this guide use **`/opt/cmdbsyncer`** as the deployment
directory. Every `cmdbsyncer` command, the systemd unit, and the
Apache vhost expect to be invoked from this directory — it is where
`local_config.py`, the `plugins/` folder and log files live.

Create it up front and make it writable for the user that will run
the Syncer:

```bash
sudo mkdir -p /opt/cmdbsyncer
sudo chown $USER /opt/cmdbsyncer
cd /opt/cmdbsyncer
```

Any other path works, but if you choose one you must replace
`/opt/cmdbsyncer` consistently in the rest of this guide.

## Install the Package

Create a clean virtual environment inside the working directory and
install from PyPI:

```bash
cd /opt/cmdbsyncer
python3.14 -m venv ENV
source ENV/bin/activate
pip install cmdbsyncer
```

After the install, the following commands are on your `PATH`:

- `cmdbsyncer` — the main application CLI (Flask Click commands, plugin
  subcommands, shell access)
- `cmdbsyncer-plugin` — plugin packaging and install helper
- `cmdbsyncer-mcp` — Model Context Protocol server (only when the
  `extras` group is installed; see below)

## Optional Dependency Groups

The platform-heavy groups are not pulled in by the default install because
they would need system libraries such as libldap, ODBC, Kerberos and the
vmware SDK. Use the matching pip **extra** to pull them in:

```bash
# LDAP, MS-SQL / MySQL, vmware SDK, markdown editor, MCP server
pip install 'cmdbsyncer[extras]'

# Ansible + Kerberos / pywinrm
pip install 'cmdbsyncer[ansible]'

# Both at once
pip install 'cmdbsyncer[extras,ansible]'
```

The exact version pins are tracked in `requirements-extras.txt` and
`requirements-ansible.txt` in the
[Git repository](https://github.com/kuhn-ruess/cmdbsyncer); the pip
extras read directly from those files so they always match the released
wheel.

!!! note "Default playbooks are not part of the PyPI package"
    The wheel ships only the Python application. Pull the reference playbooks onto your node with one command after install:
    ```bash
    cmdbsyncer sys install_playbooks ./ansible
    ```
    Details and options: [Playbooks via PyPI Install](../ansible/playbooks_pypi.md). For a remote Ansible control node, see the [cmdbsyncer-inventory](../ansible/cmdbsyncer_inventory.md) plugin instead.

## Install MongoDB

The Syncer stores every rule, account, host, label and plugin run in
MongoDB, so a running instance is a hard requirement for both
`self_configure` and any CLI or web action. For a local install on the
same host:

=== "RedHat / CentOS"
    ```bash
    dnf install -y mongodb-org
    systemctl enable --now mongod
    ```

=== "Ubuntu / Debian"
    Follow the
    [official MongoDB guide for Ubuntu](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/),
    then run:
    ```bash
    systemctl enable --now mongod
    ```

For the full repository setup (GPG keys, version pinning, remote
MongoDB) see the
[MongoDB section in the Apache guide](install_wsgi.md#mongodb). To
point the Syncer at a remote server, set `MONGODB_SETTINGS` in
`local_config.py` or the `CMDBSYNCER_MONGODB_*` environment variables —
details in [Local Config](../basics/lcl_config.md).

## Initialize the Application

With MongoDB running, seed the installation from the working
directory:

```bash
cd /opt/cmdbsyncer
source ENV/bin/activate
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

## Create the First Admin User

`self_configure` seeds the database and config but does **not** create
a login. Create at least one user before opening the web UI, otherwise
there is nothing to sign in with:

```bash
cmdbsyncer sys create_user mail@example.com
```

See [Local Users](authentication.md) for the full options (admin flag,
password reset, SSO integration, LDAP login).

## Customize the Configuration

The default MongoDB connection is `127.0.0.1:27017`, database `cmdb-api`.
To point the Syncer at a different server, either set the
`CMDBSYNCER_MONGODB_*` environment variables before starting `cmdbsyncer`
or edit `MONGODB_SETTINGS` in `local_config.py` after the first
`self_configure` run. The full list of supported keys — including the
MongoDB overrides — is documented in
[Local Config](../basics/lcl_config.md).

## Start an Interactive Shell

To open an interactive REPL for Syncer commands with tab completion
and history:

```bash
cmdbsyncer cli
```

See [Interactive Shell](../basics/syncer_shell.md) for useful recipes.

## Production Deployment

PyPI installs do not ship a WSGI server. Pick one of the three
approaches below — all of them serve the `application:app` WSGI
callable.

### Option A: Gunicorn via systemd (recommended)

Gunicorn is the default for the Docker image and a good starting
point. Install it in the same venv and run a quick foreground check
first:

```bash
pip install gunicorn
cd /opt/cmdbsyncer
/opt/cmdbsyncer/ENV/bin/gunicorn --bind 0.0.0.0:9090 --workers 2 --threads 2 application:app
```

For a real deployment, wrap it in a systemd unit so it starts at boot,
restarts on failure and streams logs to the journal.

First create a dedicated service user and hand the working directory
over to it. systemd refuses to start the unit otherwise
(`status=217/USER`):

```bash
sudo useradd --system --home-dir /opt/cmdbsyncer --shell /usr/sbin/nologin cmdbsyncer
sudo chown -R cmdbsyncer: /opt/cmdbsyncer
```

Then create `/etc/systemd/system/cmdbsyncer.service`:

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
ExecStart=/opt/cmdbsyncer/ENV/bin/gunicorn \
    --bind 0.0.0.0:9090 \
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

!!! note
    The `WorkingDirectory` **must** point to the folder that contains
    `local_config.py`. The Syncer reads `local_config.py` and the
    `plugins/` directory from its current working directory.

### TLS Certificate

Provision a certificate and key before configuring the reverse proxy —
Apache and nginx both refuse to start without one
(`BIO_new_file() failed`, `SSLCertificateFile: file does not exist`).
The vhost snippets in the next section expect the cert at
`/etc/ssl/certs/cmdb.example.com.pem` and the key at
`/etc/ssl/private/cmdb.example.com.key`. If you use different paths,
update both the commands here and the vhost snippets below.

=== "Production (Let's Encrypt)"
    ```bash
    sudo apt install -y certbot
    sudo certbot certonly --standalone -d cmdb.example.com
    ```
    Then point the vhost at the generated paths:
    `/etc/letsencrypt/live/cmdb.example.com/fullchain.pem` and
    `/etc/letsencrypt/live/cmdb.example.com/privkey.pem`.

=== "Dev / Lab (self-signed)"
    ```bash
    sudo openssl req -x509 -nodes -newkey rsa:4096 -days 365 \
        -subj "/CN=cmdb.example.com" \
        -keyout /etc/ssl/private/cmdb.example.com.key \
        -out    /etc/ssl/certs/cmdb.example.com.pem
    sudo chmod 600 /etc/ssl/private/cmdb.example.com.key
    ```
    Browsers will warn about the untrusted issuer — acceptable for
    internal test hosts, not for production.

### Reverse Proxy

Gunicorn on `:9090` is plain HTTP and should not be exposed directly.
Put Apache or nginx in front to handle TLS, compression and the public
port. Bind Gunicorn to `127.0.0.1:9090` in the unit if the proxy lives
on the same host (replace `0.0.0.0:9090` with `127.0.0.1:9090`).

=== "Apache (mod_proxy)"
    Install and enable the required modules:
    ```bash
    sudo apt install -y apache2
    sudo a2enmod proxy proxy_http headers ssl rewrite
    ```
    Create `/etc/apache2/sites-available/cmdbsyncer.conf`:
    ```apache
    <VirtualHost *:443>
        ServerName cmdb.example.com
        SSLEngine on
        SSLCertificateFile    /etc/ssl/certs/cmdb.example.com.pem
        SSLCertificateKeyFile /etc/ssl/private/cmdb.example.com.key
        ProxyPreserveHost On
        ProxyRequests     Off
        RequestHeader set X-Forwarded-Proto "https"
        ProxyPass        /  http://127.0.0.1:9090/
        ProxyPassReverse /  http://127.0.0.1:9090/
        ErrorLog  ${APACHE_LOG_DIR}/cmdbsyncer_error.log
        CustomLog ${APACHE_LOG_DIR}/cmdbsyncer_access.log combined
    </VirtualHost>
    <VirtualHost *:80>
        ServerName cmdb.example.com
        Redirect permanent / https://cmdb.example.com/
    </VirtualHost>
    ```
    Enable and reload:
    ```bash
    sudo a2ensite cmdbsyncer
    sudo systemctl reload apache2
    ```

=== "Nginx"
    Install nginx, then create `/etc/nginx/sites-available/cmdbsyncer`:
    ```nginx
    server {
        listen 80;
        server_name cmdb.example.com;
        return 301 https://$host$request_uri;
    }
    server {
        listen 443 ssl http2;
        server_name cmdb.example.com;
        ssl_certificate     /etc/ssl/certs/cmdb.example.com.pem;
        ssl_certificate_key /etc/ssl/private/cmdb.example.com.key;
        client_max_body_size 32m;
        location / {
            proxy_pass         http://127.0.0.1:9090;
            proxy_set_header   Host              $host;
            proxy_set_header   X-Real-IP         $remote_addr;
            proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Proto https;
            proxy_read_timeout 120s;
        }
    }
    ```
    Enable and reload:
    ```bash
    sudo ln -s /etc/nginx/sites-available/cmdbsyncer /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl reload nginx
    ```

!!! note
    Set `TRUSTED_PROXIES = 1` in `local_config.py` so the Syncer trusts
    the `X-Forwarded-Proto` header and recognises the request as
    HTTPS. Without this flag, password-based API auth stays blocked on
    what the app sees as a plain-HTTP request even though the browser
    speaks TLS.

### Option B: Apache with mod_wsgi

If you already run Apache, mod_wsgi serves the application directly —
no separate Gunicorn process, no reverse proxy hop. The full vhost,
TLS and SELinux details (including a ready-to-use `app.wsgi` for the
PyPI install) live in
[Installation with Apache and mod_wsgi](install_wsgi.md).

!!! warning "Build mod_wsgi from the venv"
    Do **not** use the distro packages (`python3-mod_wsgi` on RHEL,
    `libapache2-mod-wsgi-py3` on Debian/Ubuntu) — they are compiled
    against the system Python (e.g. 3.9 / 3.11), not your 3.14 venv,
    and Apache will fail to import the `application` package. Run
    `pip install mod_wsgi && mod_wsgi-express module-config` from
    inside `/opt/cmdbsyncer/ENV` and use the resulting `LoadModule`
    line. Full instructions: see the linked guide above.

### Option C: Docker Compose

For an all-in-one stack (MongoDB, Gunicorn, reverse proxy) use the
[Docker Compose setup](setup_docker.md). That path skips the PyPI
install entirely and builds the image from a published tag instead.

## Updates

To upgrade to a newer release:

```bash
pip install --upgrade cmdbsyncer
cmdbsyncer sys self_configure
```

The `self_configure` run is important after upgrades because it seeds
any new default values introduced by the release.
