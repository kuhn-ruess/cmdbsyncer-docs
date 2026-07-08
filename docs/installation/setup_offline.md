# Offline Installation (Air-Gapped Servers)

This guide is for customers whose target server has **no internet access**
and **cannot reach the Python Package Index** directly. The idea: build a
self-contained bundle on an internet-connected machine, transfer it to the
target server, and install from local files only.

## When to Use This Method

Use this approach when:

- The target server lives in an isolated network segment.
- Outbound HTTPS to `pypi.org` is blocked by a firewall or proxy policy.
- You need a reproducible, ship-once-install-anywhere artifact for a
  customer handover.

For internet-connected hosts, prefer the
[PyPI install](setup_pip.md) or the
[Git-based install](setup_code.md) — they are simpler.

## Overview

```mermaid
graph LR
A[Build Host with Internet] --> B[Download Wheels] --> C[Create tar.gz] --> D[Transfer to Target] --> E[pip install --no-index]
```

Two machines are involved:

| Role          | Needs Internet | Purpose                                          |
| ------------- | -------------- | ------------------------------------------------ |
| Build host    | Yes            | Downloads all wheels and builds the bundle       |
| Target server | No             | Receives the bundle and installs offline via pip |

!!! warning
    The build host should match the target's Python version and Linux
    platform. Wheels are Python-version- and platform-specific — a bundle
    built on macOS for Python 3.12 will not install on a Linux server
    running Python 3.11.

## Build the Bundle

On the build host, clone the repository and run the helper script. It
lives in `tools/` and wraps `pip download` plus a bit of packaging:

```bash
git clone https://github.com/kuhn-ruess/cmdbsyncer
cd cmdbsyncer
./tools/build_offline_bundle.sh --include-syncer --include-enterprise \
    --with-extras --with-ansible \
    --python-version 3.11 \
    --platform manylinux2014_x86_64
```

The bundle **always ships the base Python dependencies**
(`requirements.txt`). The optional requirement sets are **opt-in** via the
`--with-*` flags, so a bundle only carries what the target deployment needs:
`--with-extras` (LDAP / SQL / MCP / vmware), `--with-ansible` (Ansible for
Linux/SSH targets plus the playbook collection) and `--with-ansible-windows`
(WinRM + Kerberos/NTLM for Windows targets, implies `--with-ansible`). The
script produces:

- `offline_bundle/` — directory with `packages/`, the three
  `requirements*.txt` files, the bundled `ansible/` playbook tree, an
  `install.sh` and a `README.txt`
- `offline_bundle.tar.gz` — the same folder as a single archive ready to
  ship

### Script Options

| Flag                       | Purpose                                                                                  |
| -------------------------- | ---------------------------------------------------------------------------------------- |
| `--with-extras`            | Also bundle the optional extras (`requirements-extras.txt`: LDAP / SQL / MCP / vmware). Not needed for normal operation. |
| `--with-ansible`           | Also bundle Ansible for Linux/SSH targets (`requirements-ansible.txt`) and the playbook collection |
| `--with-ansible-windows`   | Also bundle the Ansible Windows deps (WinRM + Kerberos/NTLM); implies `--with-ansible`   |
| `--syncer-only`            | Bundle ONLY the `cmdbsyncer` package (no dependencies) and install it with `--no-deps`, keeping the dependencies already installed on the target. Defaults to downloading the released wheel from PyPI (add `--syncer-from-git` to build the local checkout); ignores the `--with-*` flags. |
| `--include-syncer`         | Also download the `cmdbsyncer` package from PyPI into the bundle                         |
| `--syncer-from-git`        | Build the `cmdbsyncer` wheel from the current local checkout instead of PyPI (see below). Mutually exclusive with `--include-syncer` / `--syncer-version`. |
| `--include-enterprise`     | Also download the `cmdbsyncer-enterprise` package from PyPI                              |
| `--syncer-version VER`     | Pin `cmdbsyncer` to exactly this version (e.g. `4.1.0.dev3`). Required for pre-releases. |
| `--enterprise-version VER` | Same idea for `cmdbsyncer-enterprise`                                                    |
| `--python-version VER`     | Target Python version, e.g. `3.11` — must match the target server                        |
| `--platform TAG`           | Target platform tag, e.g. `manylinux2014_x86_64` for typical Linux                       |
| `--output-dir DIR`         | Override output directory (default: `offline_bundle`)                                    |
| `--no-archive`             | Skip the tar.gz step; only produce the directory                                         |

!!! note
    When `--platform` is set, the script enforces `--only-binary=:all:`
    so pip ships wheels instead of source distributions. Pure-Python
    packages work fine; packages with C extensions must have a matching
    wheel on PyPI. If a wheel is missing, pip will abort with a clear
    error.

!!! tip "Bundling pre-releases"
    Pre-release builds (`.devN`, `aN`, `bN`, `rcN`) are not picked up
    by an unpinned `cmdbsyncer` request — pip ignores them by default.
    Always pass `--syncer-version` (and `--enterprise-version` if you
    bundle Enterprise too) for a pre-release build:

    ```bash
    ./tools/build_offline_bundle.sh \
        --include-syncer    --syncer-version 4.1.0.dev3 \
        --include-enterprise --enterprise-version 0.3.9.dev1 \
        --python-version 3.11 --platform manylinux2014_x86_64
    ```

    Without the version flags the bundle ships the latest stable
    release. Either way the generated `install.sh` pins to the same
    exact wheel, so the customer's pip never has to make a resolution
    decision in the field.

!!! tip "Shipping your current checkout instead of a PyPI release"
    When you want to bundle the exact state of your local Git checkout —
    for example an unreleased branch or a hotfix that is not on PyPI yet —
    use `--syncer-from-git` instead of `--include-syncer`:

    ```bash
    ./tools/build_offline_bundle.sh --syncer-from-git \
        --python-version 3.11 --platform manylinux2014_x86_64
    ```

    The script builds a `cmdbsyncer` wheel from the checkout, drops it in
    `packages/`, and pins `install.sh` to that exact version. The two
    sources are mutually exclusive — pass either `--include-syncer`
    (PyPI) or `--syncer-from-git` (local), not both. The bundle's
    `README.txt` records which source was used.

!!! tip "Updating only the syncer (keep installed dependencies)"
    To update the Syncer on a host whose dependencies are already installed —
    for example a locked-down server that cannot reach PyPI to (re)download
    dependencies — use `--syncer-only`. By default it takes the released
    `cmdbsyncer` wheel from PyPI:

    ```bash
    # released version from PyPI
    ./tools/build_offline_bundle.sh --syncer-only

    # or the current local checkout instead
    ./tools/build_offline_bundle.sh --syncer-only --syncer-from-git
    ```

    Build this on a host **with** PyPI access, then transfer the archive. The
    bundle contains **only** the `cmdbsyncer` wheel; its `install.sh` installs it
    with `pip install --no-deps --upgrade`, so every existing dependency on the
    target is left untouched. No requirement files are downloaded or shipped.

## Transfer the Bundle

Copy `offline_bundle.tar.gz` to the target server using whatever
out-of-band channel is available — SCP over a jump host, a USB drive,
an internal artifact repository, a support ticket attachment:

```bash
scp offline_bundle.tar.gz user@target-server:/tmp/
```

## Install on the Target Server

On the target server, extract the archive, create a virtual
environment, and run the bundled installer:

```bash
cd /opt
tar -xzf /tmp/offline_bundle.tar.gz
python3.11 -m venv venv
source venv/bin/activate
/opt/offline_bundle/install.sh
```

The bundled `install.sh` installs every requirement file from the
`packages/` directory and copies the bundled Ansible playbook collection
to `/opt/cmdbsyncer/ansible`.

### Customising the install

The installer respects a few environment variables — set them before
running `install.sh`:

| Variable                      | Effect                                                                          |
| ----------------------------- | ------------------------------------------------------------------------------- |
| `ANSIBLE_TARGET=/path`        | Where the playbook collection lands (default: `/opt/cmdbsyncer/ansible`). An existing directory is replaced. |
| `SKIP_ANSIBLE=1`              | Skip the playbook copy entirely (you already manage the playbooks elsewhere)    |

The pip and Ansible steps run independently — a failure in one is
reported but never silently swallows the other.

After install, point cmdbsyncer at the playbook directory by exporting
`CMDBSYNCER_ANSIBLE_DIR=<path>` in the service environment, or by adding
`ANSIBLE_DIR=<path>` to `local_config.py`.

### Next Steps

If you built the bundle with `--include-syncer` or `--syncer-from-git`,
the `cmdbsyncer` console script is now on your `PATH` — the application
behaves exactly like a regular PyPI install. Continue with
[Installation from PyPI](setup_pip.md#initialize-the-application) to
initialize the application (`cmdbsyncer sys self_configure`), point it
at MongoDB, and set up a WSGI server.

If you built the bundle without `--include-syncer`, the Syncer source
code is not part of the bundle — ship the repository separately (e.g.
as a tarball or Git archive) and follow the
[Installation from Code](setup_code.md#configure-defaults) guide from
the `./cmdbsyncer sys self_configure` step onwards, using the venv you
just populated.

## Upgrades

For every new release, rebuild the bundle on the internet-connected
host, transfer the new archive, and re-run `install.sh`. pip will pick
up newer wheels from `packages/` and upgrade in place. After the
install, re-run `self_configure` so new default values are seeded:

```bash
cd /opt/cmdbsyncer
source venv/bin/activate
./cmdbsyncer sys self_configure
```

## Troubleshooting

**`ERROR: Could not find a version that satisfies the requirement ...`**
The wheel for that package is missing from `packages/`. Verify that
`--python-version` and `--platform` on the build host match the target
server. Rebuild with matching values.

**`ERROR: ... is not a supported wheel on this platform`**
Same root cause — the bundle was built for a different interpreter or
CPU architecture. A common trap is building on macOS (`macosx_*` tags)
for a Linux target. Always pass `--platform manylinux2014_x86_64` for
typical Linux servers.

**Dependency conflict warnings from a previously installed
`cmdbsyncer`**
An older Syncer version in the venv pins older dependency versions. Run
`pip uninstall cmdbsyncer` first, or upgrade the Syncer itself to the
matching release.

**Packages with C extensions fail to build**
Some integrations (notably `python-ldap`) need system headers
(`libldap2-dev`, `libsasl2-dev`, ...) if no wheel is available. Install
them via the distribution package manager on the target server, or make
sure the build host has matching wheels available on PyPI.
