# Installation with Docker

Running CMDBsyncer with Docker is the recommended approach for most deployments. The repository includes a `docker-compose.yml` that starts CMDBsyncer together with its MongoDB dependency.

## Requirements

- Docker and Docker Compose installed
- Git to check out the repository

## Setup

```bash
git clone https://github.com/kuhn-ruess/cmdbsyncer
cd cmdbsyncer
```

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
