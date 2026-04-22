# Installation from Code

The most common way to use the application without Docker is directly from the Git repository.
Updates are then as simple as `git pull`.

## Overview

``` mermaid
graph LR
A[Download Repo] --> B[Create Python Environment] --> C[Install Requirements] --> D[Configure Defaults] --> E[Setup Apache]
```

## Automated Installation with Ansible

If you prefer a fully automated setup, there is a community-maintained Ansible playbook for Debian 12 available:
[ansible-things/cmdb-syncer](https://github.com/bh2005/ansible-things/tree/main/cmdb-syncer)

It covers system packages, MongoDB, Apache, uWSGI, virtual environment, and corporate proxy support in one run.
The manual steps below remain relevant for understanding the setup or for other distributions.

## Download the Repository

Check out the code from GitHub into `/opt` — this path is used in all examples throughout this documentation.

```bash
cd /opt
git clone https://github.com/kuhn-ruess/cmdbsyncer
cd cmdbsyncer
git checkout lts/3.12
```

!!! tip "Choose a version"
    - **`lts/3.12`** branch — long-term-support line; receives only security fixes and general bugfixes (no new features). Move forward with `git pull`. Recommended for production.
    - **Tag `vX.Y.Z`** — pin to a specific release for reproducible deployments: `git checkout v3.12.13`.
    - **`main`** — rolling development with new features, contains unreleased changes. Use only if you want the bleeding edge.

    Full versioning policy: [RELEASE.md on GitHub](https://github.com/kuhn-ruess/cmdbsyncer/blob/main/RELEASE.md).

## Create the Python Virtual Environment

!!! note
    Skip this section if you are using Docker.

The Syncer requires Python **3.14 or newer**. The interpreter on your system may be named `python3.14` or just `python3` — check with `python3 --version`.

```bash
cd /opt/cmdbsyncer
python3.14 -m venv ENV
source ENV/bin/activate
```

!!! warning
    The virtual environment must be activated every time you interact with the Syncer manually or via cron jobs:
    ```bash
    source /opt/cmdbsyncer/ENV/bin/activate
    ```

## Install Python Requirements

Install the base requirements:

```bash
pip install -r requirements.txt
```

If you plan to use **Ansible**:

```bash
pip install -r requirements-ansible.txt
```

For additional database backends (see `requirements-extras.txt`):

```bash
pip install -r requirements-extras.txt
```

## Install MongoDB

!!! note
    Skip this section if you are using Docker.

Install MongoDB with your package manager. See the [MongoDB section in the Apache setup guide](install_wsgi.md#mongodb) for distribution-specific instructions.

Once installed, start and enable the service:

```bash
systemctl enable --now mongod
```

## Configure Defaults

!!! note
    Make sure the virtual environment is activated, or run this inside the Docker container.

Once MongoDB is running, initialize the application defaults:

```bash
./cmdbsyncer sys self_configure
```

Run this command again after every update.

## Start the Development Server

To quickly verify the installation, you can start the built-in development server:

```bash
flask run --host 0.0.0.0 --port 8080
```

!!! warning
    The development server is not suitable for production use. Set up Apache with mod_wsgi for production deployments: [Installation with Apache](install_wsgi.md)

## Next Steps

- Set up Apache for production: [Installation with Apache](install_wsgi.md)
- Get started with the application: [First Steps](../basics/first_steps.md)
