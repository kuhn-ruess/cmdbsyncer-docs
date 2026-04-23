# Enterprise Edition

CMDBsyncer follows an **open-core** model. The core product is open source and fully functional on its own. A separate `cmdbsyncer-enterprise` package adds commercial features and is activated by a signed license.

If the enterprise package is not installed — or its license is missing or invalid — CMDBsyncer continues to run as the Community Edition. Enterprise-only hooks silently fall back to no-ops.

## Enterprise Features

| Feature                   | Details                                                                  |
| :------------------------ | :----------------------------------------------------------------------- |
| Remote User SSO           | [Remote User SSO](remote_user_sso.md)                                    |
| LDAP Login                | [LDAP Login](ldap_login.md)                                              |
| OIDC Login                | [OIDC Login](oidc_login.md)                                              |
| Secrets Manager           | [Secrets Manager](secrets_manager.md)                                    |
| JSON Logging              | [JSON Logging](json_logging.md)                                          |
| Audit Log                 | [Audit Log](audit_log.md)                                                |
| Audit SIEM Streaming      | [Audit Log → SIEM Streaming](audit_log.md#streaming-to-an-external-siem) |
| Notifications             | [Notification Routing](notifications.md)                                 |
| Webhook Signatures        | [Webhook Signatures](webhook_signatures.md)                              |
| Prometheus Metrics        | [Prometheus Metrics](prometheus_metrics.md)                              |
| Scheduled Backups         | [Scheduled Backups](scheduled_backup.md)                                 |
| 4-Eyes Approval Workflow  | [4-Eyes Approval Workflow](approval_workflow.md)                         |

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

### Offline install

The offline bundler downloads the enterprise wheel alongside the community wheel when called with `--include-enterprise`:

```bash
./tools/build_offline_bundle.sh --include-syncer --include-enterprise
```

The bundle installs the enterprise package on top of the core; the license JWT still has to be placed on the target server separately.

## License File

CMDBsyncer looks for `license.jwt` in the **same directory as your `local_config.py`**. That is the path that pip installs already use for runtime configuration, so no extra directory is needed:

```text
<dir of local_config.py>/license.jwt
```

To use a different path, set the `CMDBSYNCER_LICENSE` environment variable:

```bash
export CMDBSYNCER_LICENSE=/srv/cmdbsyncer/license.jwt
```

The file must be readable by the user that runs the application (the uWSGI user in container deployments).

The license carries the following metadata:

| Field        | Meaning                                                |
| :----------- | :----------------------------------------------------- |
| `license_id` | Unique license identifier issued by Kuhn & Ruess       |
| `customer`   | Licensee name                                          |
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
