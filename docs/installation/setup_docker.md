# Installation with Docker

Running CMDBsyncer with Docker is the recommended approach for most deployments. Every release is published as a ready-made image, so there is nothing to build.

## Requirements

- Docker and Docker Compose installed

## Setup

Fetch the compose file and start the stack:

```bash
curl -O https://raw.githubusercontent.com/kuhn-ruess/cmdbsyncer/main/docker-compose.registry.yml
docker compose -f docker-compose.registry.yml up -d
```

That starts CMDBsyncer together with its MongoDB and makes it available on port **8080**.

### Choosing a version

The compose file above tracks `latest`. Replace the tag in it with the version you want to stay on:

```yaml
api:
  image: ghcr.io/kuhn-ruess/cmdbsyncer:4.4.0
```

| Tag      | Moves                         | Use it for                                  |
| -------- | ----------------------------- | ------------------------------------------- |
| `4.4.0`  | never                         | a deployment that must not shift on its own |
| `4.4`    | with every patch of that line | staying on one minor version                |
| `latest` | with every new release        | test systems that should follow along       |

The images are built for `linux/amd64` and `linux/arm64`, so the same tag works on an ARM server. Full versioning policy: [RELEASE.md on GitHub](https://github.com/kuhn-ruess/cmdbsyncer/blob/main/RELEASE.md).

### Building the image yourself

The repository also builds an image from source — useful for a fork, a custom base image or a preinstalled plugin:

```bash
git clone https://github.com/kuhn-ruess/cmdbsyncer
cd cmdbsyncer
git checkout lts/3.12
docker compose up -d
```

Here the version you run is decided by the branch or tag that is checked out **before** the image is built:

- **`lts/3.12`** branch — long-term-support line. Receives only security fixes and general bugfixes, no new features.
- **Tag `vX.Y.Z`** — pin to a specific release: `git checkout v3.12.13`.
- **`main`** — rolling development with new features, not recommended for production.

## Configuration

CMDBsyncer keeps its `SECRET_KEY` and `CRYPTOGRAPHY_KEY` in a `local_config.py`, created automatically on first start by `./cmdbsyncer sys self_configure` (which also runs with every update).

!!! danger "That file has to outlive the container"
    Every stored account password is encrypted with the `CRYPTOGRAPHY_KEY` in it. Written inside the container, it is thrown away the moment the container is replaced — which is exactly what an update does — and a new key is generated. None of the stored passwords can be read after that.

    Set `CMDBSYNCER_CONFIG_DIR` to a mounted directory and CMDBsyncer keeps the file there instead. `docker-compose.registry.yml` already does this with a named volume:

    ```yaml
    api:
      environment:
        CMDBSYNCER_CONFIG_DIR: /srv/etc
      volumes:
        - config:/srv/etc
    ```

    Back that volume up together with the database.

!!! tip "Coming from an older Docker setup"
    A deployment that has been running without `CMDBSYNCER_CONFIG_DIR` has its
    `local_config.py` inside the container. Copy it into the new location
    **before** the first start with the variable set, otherwise a fresh key is
    generated and the stored passwords are lost:

    ```bash
    docker cp <old_container>:/srv/local_config.py ./local_config.py
    docker compose -f docker-compose.registry.yml up -d
    docker compose -f docker-compose.registry.yml cp \
        local_config.py api:/srv/etc/local_config.py
    docker compose -f docker-compose.registry.yml restart api
    ```

Run this after every update to apply any new default settings:

```bash
docker exec -it <container_name> ./cmdbsyncer sys self_configure
```

## Updating

Change the tag in the compose file (or, on a moving tag, pull the new image) and bring the stack up again:

```bash
docker compose -f docker-compose.registry.yml pull
docker compose -f docker-compose.registry.yml up -d
```

The container runs `sys self_configure` on start, so any new default settings are applied on the way up.

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

The scheduler reports itself in the container log, so `docker logs` tells you whether it is alive and what it fired:

```text
crond: crond 4.5 dillon's cron daemon, started with loglevel info
crond: FILE /etc/crontabs/root USER root PID 214 run-parts /etc/periodic/15min
```

The output of the runs themselves lands there too — one line per fired job, plus whatever the sync writes.

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

## Shell Completion

`./helper shell` opens a bash login shell in the container with tab completion for the `cmdbsyncer` CLI: press TAB to complete command groups, subcommands and options.

```
/srv # ./cmdbsyncer checkmk export_<TAB>
export_bi_aggregations  export_downtimes  export_notifications  export_rules
export_bi_rules         export_groups     export_passwords      export_rulesets
export_dcd_rules        export_hosts      export_tags           export_users
```

Completion is set up by `/etc/profile.d/cmdbsyncer_completion.sh`, so it needs a login shell. If you enter the container yourself, use `docker exec -it <container> bash -l`.

## Next Steps

- [Configure the application](../basics/lcl_config.md)
- [First Steps](../basics/first_steps.md)
