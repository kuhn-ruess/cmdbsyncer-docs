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
`application:app` WSGI callable, systemd keeps it running and a reverse
proxy terminates TLS.

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

### TLS Certificate

Provision a certificate and key before configuring the reverse proxy —
Apache refuses to start without one
(`BIO_new_file() failed`, `SSLCertificateFile: file does not exist`).
The vhost in the next section expects the cert at
`/etc/ssl/certs/cmdb.example.com.pem` and the key at
`/etc/ssl/private/cmdb.example.com.key`. If you use different paths,
update both the commands here and the vhost below.

On RedHat, open HTTP and HTTPS in firewalld first, certbot and Apache
both need them:

```bash
sudo firewall-cmd --permanent --add-service=http --add-service=https
sudo firewall-cmd --reload
```

=== "Production (Let's Encrypt)"
    Install certbot:

    === "RedHat / Rocky / Alma"
        certbot comes from EPEL:
        ```bash
        sudo dnf install -y epel-release
        sudo dnf install -y certbot
        ```

    === "Ubuntu / Debian"
        ```bash
        sudo apt install -y certbot
        ```

    Request the certificate while port 80 is still free:
    ```bash
    sudo certbot certonly --standalone -d cmdb.example.com
    ```
    Then point the vhost at the generated paths:
    `/etc/letsencrypt/live/cmdb.example.com/fullchain.pem` and
    `/etc/letsencrypt/live/cmdb.example.com/privkey.pem`.

=== "Dev / Lab (self-signed)"
    ```bash
    sudo mkdir -p -m 700 /etc/ssl/private
    sudo openssl req -x509 -nodes -newkey rsa:4096 -days 365 \
        -subj "/CN=cmdb.example.com" \
        -keyout /etc/ssl/private/cmdb.example.com.key \
        -out    /etc/ssl/certs/cmdb.example.com.pem
    sudo chmod 600 /etc/ssl/private/cmdb.example.com.key
    ```
    Browsers will warn about the untrusted issuer — acceptable for
    internal test hosts, not for production.

### Apache Reverse Proxy

Gunicorn speaks plain HTTP and the unit binds it to `127.0.0.1:9090`.
Apache in front handles TLS and the public port. If Apache runs on
another host, change the bind address to `0.0.0.0:9090`.

Install Apache with the TLS and proxy modules:

=== "RedHat / Rocky / Alma"
    ```bash
    sudo dnf install -y httpd mod_ssl
    ```

=== "Ubuntu / Debian"
    ```bash
    sudo apt install -y apache2
    sudo a2enmod proxy proxy_http headers ssl
    ```

Save the vhost as `/etc/httpd/conf.d/cmdbsyncer.conf` (RedHat) or
`/etc/apache2/sites-available/cmdbsyncer.conf` (Ubuntu / Debian):

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
</VirtualHost>
<VirtualHost *:80>
    ServerName cmdb.example.com
    Redirect permanent / https://cmdb.example.com/
</VirtualHost>
```

Then activate it:

=== "RedHat / Rocky / Alma"
    Allow Apache to connect to Gunicorn under SELinux and start it:
    ```bash
    sudo setsebool -P httpd_can_network_connect 1
    sudo systemctl enable --now httpd
    ```

=== "Ubuntu / Debian"
    ```bash
    sudo a2ensite cmdbsyncer
    sudo systemctl reload apache2
    ```

!!! note
    Set `TRUSTED_PROXIES = 1` in `local_config.py` so the Syncer trusts
    the `X-Forwarded-Proto` header and recognises the request as
    HTTPS. Without this flag, password-based API auth stays blocked on
    what the app sees as a plain-HTTP request even though the browser
    speaks TLS.

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
