# Installation and License

The Enterprise Edition is a separate Python package, `cmdbsyncer-enterprise`,
that is installed **next to** your existing CMDBsyncer and unlocked by a
signed license file. Nothing in the core product has to be replaced or
reconfigured.

Three steps:

1. [Install the package](#install-the-package) into the environment that runs CMDBsyncer
2. [Place the license file](#place-the-license-file)
3. [Restart and verify](#restart-and-verify)

## Get a License

Licenses are issued by Kuhn & Ruess GmbH. Contact
[info@kuhn-ruess.de](mailto:info@kuhn-ruess.de) with the features you need
(see the [feature overview](index.md)) and you receive a `license.jwt` file.

The file is a signed token — it can be copied, backed up and version-managed
like any other config file, but it cannot be edited: any change breaks the
signature and the package refuses to load it.

## Install the Package

The package is published on PyPI and needs the **same Python environment** as
CMDBsyncer itself. Installing it into a different interpreter or virtualenv is
the single most common reason for a "Community Edition" surprise after the
restart.

### pip install

```bash
cd /opt/cmdbsyncer
source venv/bin/activate
pip install cmdbsyncer-enterprise
```

### Docker / container

Install into the running container, then restart it:

```bash
docker exec -it <container_name> pip3 install cmdbsyncer-enterprise
docker restart <container_name>
```

!!! warning "Rebuilds drop the package"
    An install made with `docker exec` lives in the container's writable
    layer only. As soon as the image is rebuilt (`docker compose up --build`,
    an update, a new release) the package is gone. For a permanent setup, add
    it to your image instead:

    ```dockerfile
    RUN pip3 install --no-cache-dir cmdbsyncer-enterprise
    ```

    The license file stays outside the image — mount it, as described below.

### Offline / air-gapped

The [offline bundler](../installation/setup_offline.md) downloads the
enterprise wheel alongside the community one when called with
`--include-enterprise`:

```bash
./tools/build_offline_bundle.sh --include-syncer --include-enterprise
```

The bundle installs the enterprise package on top of the core. The license
file is **not** part of the bundle and has to be placed on the target server
separately.

### Optional vault dependencies

Only relevant with the [Secrets Manager](secrets_manager.md) feature. The
providers lazy-import their SDKs, so nothing unused is pulled in:

```bash
pip install 'cmdbsyncer-enterprise[keepass]'
pip install 'cmdbsyncer-enterprise[vault]'
pip install 'cmdbsyncer-enterprise[aws]'
pip install 'cmdbsyncer-enterprise[secrets-all]'   # all three
```

## Place the License File

CMDBsyncer looks for `license.jwt` in the **same directory as your
`local_config.py`** — the directory you already use for runtime config:

```text
<dir of local_config.py>/license.jwt
```

To use a different path, set the `CMDBSYNCER_LICENSE` environment variable.
It always wins over the default location:

```bash
export CMDBSYNCER_LICENSE=/srv/cmdbsyncer/license.jwt
```

In a container, mount the file in and point the variable at it, so it
survives image rebuilds:

```yaml
services:
  cmdbsyncer:
    environment:
      CMDBSYNCER_LICENSE: /etc/cmdbsyncer/license.jwt
    volumes:
      - ./license.jwt:/etc/cmdbsyncer/license.jwt:ro
```

The file must be readable by the user that runs the application (the uWSGI
user in container deployments).

### Upload through the web UI

Instead of copying the file by hand, a global admin can open
**Profile → License** and use the *Upload License* form at the bottom of the
page. The signature is verified against the installed public key **before**
the file is written, and the write is atomic — a malformed or wrongly signed
upload never overwrites a working license. The page shows the exact
destination path it will write to.

Restart the application afterwards; an uploaded license is only picked up on
the next start.

## Restart and Verify

Enterprise features are wired up at import time, so the application has to be
restarted after installing the package or changing the license:

```bash
docker restart <container_name>       # container
systemctl restart cmdbsyncer          # systemd / uWSGI
```

Open **Profile → License** in the web UI:

| What you see                                          | Meaning                                                              |
| :---------------------------------------------------- | :------------------------------------------------------------------- |
| **Enterprise Edition** with license details           | License active. The *Features* row lists the unlocked feature keys.  |
| **Community Edition**                                 | The `cmdbsyncer_enterprise` package is not installed in this environment. |
| **Enterprise package installed, but license not active** | Package found, license could not be loaded. The `Load status` field names the reason. |

At startup one line is written to stderr (visible in `docker logs` or the
systemd journal):

```text
[cmdbsyncer-enterprise] package loaded successfully
[cmdbsyncer-enterprise] package not installed — running Community Edition
[cmdbsyncer-enterprise] package installed but failed to activate ...: <reason>
```

## What the License Contains

| Claim        | Meaning                                                                 |
| :----------- | :---------------------------------------------------------------------- |
| `license_id` | Unique license identifier issued by Kuhn & Ruess                        |
| `customer`   | Licensee name                                                           |
| `features`   | The feature keys this license unlocks — only these are registered       |
| `max_hosts`  | Soft cap on the number of hosts; `0` means unlimited                    |
| `iat`        | Issued-at timestamp                                                     |
| `exp`        | Expiry timestamp                                                        |

Everything on the License page comes from these claims — there is no
phone-home, no license server, and no outbound connection of any kind.

### Expiry and host cap never cause an outage

Both limits are deliberately **warnings, not switches**:

- **Expired license** — every feature keeps working. The License page shows
  an expiry warning, starting 30 days before the date so there is time to
  renew.
- **More hosts than `max_hosts`** — every feature keeps working. The License
  page reports the current host count against the cap.

A lapsed license never locks you out of your own data. Only a *missing*,
*malformed* or *wrongly signed* file stops the package from loading, and even
then CMDBsyncer keeps running as the Community Edition.

## Upgrading

```bash
pip install --upgrade cmdbsyncer-enterprise
```

Restart the application. The license file is unaffected by a package upgrade
and does not need to be reissued.

If pip reports nothing to do, check the installed version and force it:

```bash
pip show cmdbsyncer-enterprise
pip install --force-reinstall cmdbsyncer-enterprise
```

## Troubleshooting

**License page says "Community Edition"**

The package is not installed in the *running* environment. With Docker this
usually means it was installed into the wrong container, or the container was
rebuilt from an image that does not contain it. Re-run the install and
restart. On a pip install, confirm you activated the same virtualenv the
application runs from.

**License page says "Enterprise package installed, but license not active"**

Read the `Load status` field on that page:

| Status                                              | Cause                                                                                                       |
| :-------------------------------------------------- | :---------------------------------------------------------------------------------------------------------- |
| `failed: Enterprise license not found: [Errno 2]`   | File missing, or `CMDBSYNCER_LICENSE` points to a path that does not exist                                  |
| `failed: Enterprise license invalid: bad_signature` | The public key in the installed package does not match the signer — package and license are out of sync     |
| `failed: Enterprise license not found: local_config.py is not on sys.path` | The default location cannot be resolved — set `CMDBSYNCER_LICENSE` explicitly                |

**A feature I bought is missing from the menu**

The *Features* row on the License page lists exactly what the license
unlocks. If the key is not there, the license predates the purchase — request
a reissued file. If the key is there but the menu entry is not, restart the
application: admin views are registered at startup.

## Uninstalling

To go back to the Community Edition:

```bash
pip uninstall cmdbsyncer-enterprise
```

Restart the application. The License page then shows the Community Edition
notice. The license file can stay where it is — it has no effect without the
package.
