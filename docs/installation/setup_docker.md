# Installation with Docker

Running CMDBsyncer with Docker is the recommended approach for most deployments. The repository includes a `docker-compose.yml` that starts CMDBsyncer together with its MongoDB dependency.

## Requirements

- Docker and Docker Compose installed
- Git to check out the repository

## Setup

```bash
git clone https://github.com/kuhn-ruess/cmdbsyncer
cd cmdbsyncer
git checkout lts/3.12
```

!!! tip "Choose a version"
    The Docker image is built from the repo source, so the version you run is determined by the branch or tag that is checked out **before** the image is built.

    - **`lts/3.12`** branch — long-term-support line. Receives only security fixes and general bugfixes, no new features. Recommended for production.
    - **Tag `vX.Y.Z`** — pin to a specific release: `git checkout v3.12.13`.
    - **`main`** — rolling development with new features, not recommended for production.

    Full versioning policy: [RELEASE.md on GitHub](https://github.com/kuhn-ruess/cmdbsyncer/blob/main/RELEASE.md).

Start the stack:

```bash
docker compose up -d
```

The application will be available on port **5000** by default.

## Configuration

CMDBsyncer requires a `local_config.py` in the project root. It is created automatically on first start via `./cmdbsyncer sys self_configure` (which runs with every update). This file contains your `SECRET_KEY` and `CRYPTOGRAPHY_KEY`.

!!! warning "Keep local_config.py safe"
    Do **not** place `local_config.py` inside the container image. Mount it as a volume instead. If you lose this file, all stored passwords become unrecoverable since the `CRYPTOGRAPHY_KEY` is needed to decrypt them.

Run this after every update to apply any new default settings:

```bash
docker exec -it <container_name> ./cmdbsyncer sys self_configure
```

## Create the First User

```bash
docker exec -it <container_name> ./cmdbsyncer sys create_user mail@address.org
```

The command prints a generated password. Run it again at any time to reset a forgotten password or unlock a 2FA-locked account.

## CLI Access

Most operations can be done in the web interface. For debugging, the CLI is available via `docker exec`:

```bash
docker exec -it <container_name> ./cmdbsyncer --help
```

## Cron Jobs

Sync jobs need to be triggered on a schedule. If you use the provided `Dockerfile`, cron is already set up inside the container. Otherwise, schedule `docker exec` calls from the host cron or your orchestrator.

## External Files

If your workflows use CSV files, CA certificates, or other external files, define a Docker volume for them and point `FILEADMIN_PATH` to the mounted path in `local_config.py`:

```python
config = {
    'FILEADMIN_PATH': '/data/files',
}
```

The [Fileadmin](../basics/fileadmin.md) in the web UI will then show and manage files at that path.

## Reverse Proxy

The container exposes a uWSGI socket directly — there is no Nginx inside the container, since your reverse proxy can speak uWSGI directly to the exposed port. A typical setup uses Nginx or Apache on the host as the SSL-terminating reverse proxy in front of the container.

### Tell CMDBsyncer it is behind a proxy

When a reverse proxy terminates TLS in front of the container, CMDBsyncer needs to know that the client is actually using HTTPS. Otherwise the HTTPS requirement for password-based API authentication blocks every API call.

Add this to `local_config.py`:

```python
config = {
    'TRUSTED_PROXIES': 1,
}
```

Use `1` for a single proxy in front of the container (the usual Apache/Nginx setup). Use `2` if there is another proxy further out, e.g. Cloudflare → Nginx → container. Leave it at the default `0` only for direct deployments without a proxy.

!!! warning "Only reachable via the proxy"
    Setting `TRUSTED_PROXIES` greater than `0` makes the app trust the `X-Forwarded-Proto`, `X-Forwarded-For`, and `X-Forwarded-Host` headers. Make sure the container is only reachable through the proxy — bind the published port to `127.0.0.1`, use a private Docker network, or firewall the port. Otherwise a client that reaches the container directly can spoof those headers.

### Apache example

Apache 2.4.25 and later sets `X-Forwarded-Proto` automatically on `ProxyPass`. Setting it explicitly is safer:

```apache
<VirtualHost *:443>
    ServerName cmdbsyncer.example.com
    SSLEngine on
    SSLCertificateFile /etc/ssl/cmdbsyncer.crt
    SSLCertificateKeyFile /etc/ssl/cmdbsyncer.key

    RequestHeader set X-Forwarded-Proto "https" env=HTTPS

    ProxyPreserveHost On
    ProxyPass        / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
</VirtualHost>
```

### Nginx example

```nginx
server {
    listen 443 ssl http2;
    server_name cmdbsyncer.example.com;

    ssl_certificate     /etc/ssl/cmdbsyncer.crt;
    ssl_certificate_key /etc/ssl/cmdbsyncer.key;

    location / {
        proxy_pass         http://127.0.0.1:5000;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
```

### How to check

After deploying, log in once. If the REST API or the login page complains about "HTTPS is required" even though the browser URL is `https://…`, either `TRUSTED_PROXIES` is still `0` or the proxy is not forwarding `X-Forwarded-Proto`.

## Resources

CMDBsyncer is lightweight in terms of memory and CPU at rest. For large environments with many rules, it benefits from additional CPUs since rule calculations use Python multiprocessing across all available cores. Disk space for MongoDB is the main resource to plan for.

## Behind a Corporate Proxy

### Option 1: Build argument in docker-compose.local.yml

```yaml
api:
  build:
    dockerfile: Dockerfile.local
    args:
      HTTPS_PROXY: "PROTOCOL://SERVERNAME:PORT"
  environment:
    config: compose
  ports:
    - 5003:5003
  volumes:
    - ./:/srv
```

### Option 2: Docker daemon proxy config

Add the proxy to `~/.docker/config.json` for the user running Docker:

```json
{
  "proxies": {
    "default": {
      "httpProxy": "PROTOCOL://SERVERNAME:PORT",
      "httpsProxy": "PROTOCOL://SERVERNAME:PORT",
      "noProxy": "EXCLUDE1,EXCLUDE2,127.0.0.0/8"
    }
  }
}
```

## Development Mode

For local development with live code reload, use the `./helper` command provided in the repository. It starts the container with the source directory mounted and Flask in debug mode.

## Next Steps

- [Configure the application](../basics/lcl_config.md)
- [First Steps](../basics/first_steps.md)
