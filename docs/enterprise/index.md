# Enterprise Edition

CMDBsyncer follows an **open-core** model. The core product is open source and fully functional on its own. A separate `cmdbsyncer-enterprise` package adds commercial features and is activated by a signed license.

If the enterprise package is not installed — or its license is missing or invalid — CMDBsyncer continues to run as the Community Edition. Enterprise-only hooks silently fall back to no-ops.

!!! tip "Getting started"
    [Installation and License](installation.md) walks through installing the package, placing the license file, and verifying that it took effect.

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

A license unlocks exactly the features it lists. **Profile → License** in the web UI shows which ones are active on your installation.

## How It Works

The core imports the enterprise package inside a guarded import. On a valid license, the package registers each licensed feature with the core's hook registry; core call sites then use that hook instead of their default behaviour. Without the package — or without a matching feature in the license — the hook is simply absent and the core keeps its Community behaviour.

That means:

- No enterprise code runs unless the package is installed **and** the license lists the feature.
- The license is verified locally against a public key shipped with the package. There is no license server and no outbound connection.
- Removing the package returns the installation to the Community Edition without any data migration.

See [Installation and License](installation.md) for setup, verification and troubleshooting.
