# Enterprise Edition

CMDBsyncer follows an **open-core** model. The core product is open source and fully functional on its own. A separate `cmdbsyncer-enterprise` package adds commercial features and is activated by a signed license.

If the enterprise package is not installed — or its license is missing or invalid — CMDBsyncer continues to run as the Community Edition. Enterprise-only hooks silently fall back to no-ops.

## Enterprise Features

| Feature         | License claim | Description                                          |
| :-------------- | :------------ | :--------------------------------------------------- |
| Remote User SSO | `remote_user` | Trusted-header SSO login (e.g. Keycloak, mod_auth_*) |

## Installation

The enterprise package is published on PyPI. Your license file is provided separately by Kuhn & Ruess GmbH.

Install into the same Python environment that runs CMDBsyncer:

```bash
pip install cmdbsyncer-enterprise
```


Restart the application (`docker restart <container>` or reload apache) so the new package is loaded.

To upgrade to a newer release later:

```bash
pip install --upgrade cmdbsyncer-enterprise
```

## License File

By default, CMDBsyncer looks for it at:

```text
/etc/cmdbsyncer/license.jwt
```

To use a different path, set the `CMDBSYNCER_LICENSE` environment variable:

```bash
export CMDBSYNCER_LICENSE=/srv/cmdbsyncer/license.jwt
```

The file must be readable by the user that runs the application (the uWSGI user in container deployments).

The license contains the following claims:

| Claim        | Meaning                                                |
| :----------- | :----------------------------------------------------- |
| `license_id` | Unique license identifier issued by Kuhn & Ruess       |
| `customer`   | Licensee name                                          |
| `features`   | List of enabled feature names (e.g. `["remote_user"]`) |
| `iat`        | Issued-at timestamp                                    |
| `exp`        | Expiry timestamp (enforced at startup)                 |


## Verifying the License

After a restart, open **Profile → License** in the web UI.

- **Enterprise Edition** block with license details → license is active.
- **Community Edition** → the `cmdbsyncer_enterprise` package is not installed.
- **Enterprise package installed, but license not active** → the package is there but the license could not be loaded. The `Load status` field on that page shows the exact reason.

At application startup, a single line is written to stderr (visible in `docker logs` or your systemd journal):

```text
[cmdbsyncer-enterprise] package loaded successfully
[cmdbsyncer-enterprise] package not installed — running Community Edition
[cmdbsyncer-enterprise] package installed but failed to activate ...: <reason>
```

## Troubleshooting

**License page says "Community Edition"**

The package is not installed in the running environment. In Docker, this usually means the package was not installed in the correct container, or the container was rebuilt from an image that doesn't include it. Re-run the install step and restart.

**License page says "Enterprise package installed, but license not active"**

Read the `Load status` field on the page. Typical values:

| Status                                              | Cause                                                                                                       |
| :-------------------------------------------------- | :---------------------------------------------------------------------------------------------------------- |
| `failed: Enterprise license not found: [Errno 2]`   | File missing or `CMDBSYNCER_LICENSE` points to a non-existent path                                          |
| `failed: Enterprise license invalid: expired_token` | License `exp` is in the past — request a renewal                                                            |
| `failed: Enterprise license invalid: bad_signature` | Public key in the installed package doesn't match the signer — package and license versions are out of sync |

**Version upgrades**

Use `pip install --upgrade cmdbsyncer-enterprise` and restart the application. If pip skips the update, check the installed version with `pip show cmdbsyncer-enterprise` and force a reinstall with `pip install --force-reinstall cmdbsyncer-enterprise`.

## Uninstalling the Enterprise Package

To revert to the Community Edition, uninstall the package:

```bash
pip uninstall cmdbsyncer-enterprise
```

Restart the application. The License page will then show the Community Edition notice. The license file itself can stay in place — it has no effect without the package.
