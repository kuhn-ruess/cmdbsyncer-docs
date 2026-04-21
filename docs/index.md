# CMDBsyncer

CMDBsyncer is a **rule-based, modular synchronization hub** for host and configuration data. It connects your source systems — CMDBs, asset management tools, APIs, CSV files — with your target systems like Checkmk, Netbox, or I-Doit, and keeps them in sync automatically.

Every connection to an external system is configured through an [Account](basics/accounts.md). Rules control what gets synchronized, how attributes are transformed, and which hosts are included.

![Rules overview](img/index_rules.png)

---

## Key Features

- **Web Interface** with login, 2FA, and user management — all configuration after installation is done in the UI
- **Rule Engine** to control synchronization based on host attributes, with rewrite, filter, and condition support
- **Jinja support** throughout rules and configuration fields
- **Built-in CMDB mode** for managing objects, hosts, and templates directly in CMDBsyncer
- **Plugin API** to integrate custom data sources with minimal code
- **Cron management** to schedule sync jobs from the UI
- **REST API** for external automation
- **Ansible support** as a dynamic inventory source
- **Encryption** of stored credentials
- **Debug tooling** via CLI and web-based debug views
- **Monitoring integration** via Checkmk Exchange check

---

## How it Works

CMDBsyncer imports hosts and attributes from one or more sources, processes them through the rules engine, and exports the result to the configured targets. Sources and targets can overlap — a system like Checkmk or Netbox can be both.

→ [How it Works](basics/how_it_works.md)

---

## Supported Integrations

### Full-Featured Modules

| Module | Import | Export | Notes |
| :----- | :----: | :----: | :---- |
| [Checkmk](checkmk/index.md) | ✓ | ✓ | Full host lifecycle, rules, tags, labels, groups, BI, DCD, agents, sites — tested with 140,000+ hosts |
| [Netbox](netbox/index.md) | ✓ | ✓ | Devices, VMs, interfaces, IPAM, contacts, sites |
| [I-Doit](i-doit/index.md) | ✓ | ✓ | Template-based device sync |
| [Ansible](ansible/index.md) | — | ✓ | Dynamic inventory source, Checkmk agent and site management |
| [CMDB Mode](cmdb/index.md) | ✓ | ✓ | Use CMDBsyncer itself as a lightweight CMDB |

### Import Sources

| Module | Description |
| :----- | :---------- |
| [REST API / JSON](rest_json/index.md) | Import from any REST API or JSON file structure |
| [CSV](csv/index.md) | Import hosts or enrich attributes from CSV files |
| [LDAP](ldap/index.md) | Import objects from LDAP directories |
| [JDisc](jdisc/index.md) | Import devices from JDisc Discovery |
| [Jira](jira/index.md) | Import objects from Jira (on-prem and cloud) |
| [Cisco DNA](ciscodna/index.md) | Import devices and interface information |
| BMC Remedy | Limited import from BMC Remedy |
| PRTG | Import objects from PRTG |
| VMware | Import and export attributes for VMware VMs |
| [MySQL](sql/index.md) | Import and inventorize MySQL database tables |
| [MSSQL / ODBC](sql/index.md) | Import from any ODBC-compatible database (FreeTDS, MSSQL, etc.) |

---

## Getting Started

1. Install CMDBsyncer: [Docker](installation/setup_docker.md) or [Apache/WSGI](installation/install_wsgi.md)
2. [Understand how it works](basics/how_it_works.md)
3. [Create your first Account](basics/accounts.md)
4. [Set up an Import](basics/import.md)
5. [Configure Rules](basics/conditions.md)
6. [Export to a target system](basics/export.md)
