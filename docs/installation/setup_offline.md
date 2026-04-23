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
./tools/build_offline_bundle.sh --all \
    --python-version 3.11 \
    --platform manylinux2014_x86_64
```

The script produces:

- `offline_bundle/` — directory with `packages/`, the three
  `requirements*.txt` files, an `install.sh` and a `README.txt`
- `offline_bundle.tar.gz` — the same folder as a single archive ready to
  ship

### Script Options

| Flag                   | Purpose                                                            |
| ---------------------- | ------------------------------------------------------------------ |
| `--extras`             | Include `requirements-extras.txt` (LDAP, ODBC, vmware, ...)        |
| `--ansible`            | Include `requirements-ansible.txt` (Kerberos, WinRM, Ansible)      |
| `--all`                | Shortcut for `--extras --ansible`                                  |
| `--include-syncer`     | Also download the `cmdbsyncer` package from PyPI into the bundle   |
| `--python-version`     | Target Python version, e.g. `3.11` — must match the target server  |
| `--platform`           | Target platform tag, e.g. `manylinux2014_x86_64` for typical Linux |
| `--output-dir DIR`     | Override output directory (default: `offline_bundle`)              |
| `--no-archive`         | Skip the tar.gz step; only produce the directory                   |

!!! note
    When `--platform` is set, the script enforces `--only-binary=:all:`
    so pip ships wheels instead of source distributions. Pure-Python
    packages work fine; packages with C extensions must have a matching
    wheel on PyPI. If a wheel is missing, pip will abort with a clear
    error.

!!! tip
    Passing `--include-syncer` additionally downloads the latest
    `cmdbsyncer` release from PyPI and drops it into `packages/`
    alongside the third-party dependencies. The generated `install.sh`
    then installs and upgrades `cmdbsyncer` itself from that wheel, so
    the target server receives the Syncer in one go. Without the flag,
    the bundle contains only the third-party dependencies.

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
python3.11 -m venv ENV
source ENV/bin/activate
/opt/offline_bundle/install.sh
```

The bundled `install.sh` runs, in effect:

```bash
python3 -m pip install --no-index \
    --find-links /opt/offline_bundle/packages \
    -r /opt/offline_bundle/requirements.txt
```

### Next Steps

If you built the bundle with `--include-syncer`, the `cmdbsyncer`
console script is now on your `PATH` — the application behaves exactly
like a regular PyPI install. Continue with
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
source ENV/bin/activate
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
