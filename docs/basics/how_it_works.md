# How it Works

CMDBsyncer acts as a **central hub** between your source systems and your target systems. It imports host and configuration data from one or more sources, normalizes and enriches it using rules, and then synchronizes the result to any number of targets — fully automated and on a schedule.

``` mermaid
graph LR
    SD[Source Database]
    SC[Source CSV]
    R[REST API]
    O[Other Sources]

    S[(CMDBsyncer DB)]

    RE[Rules Engine]

    C[Checkmk]
    N[Netbox]
    I[I-Doit]
    X[Other Targets]

    SD --> S
    SC --> S
    R  --> S
    O  --> S

    C  --> S
    N  --> S
    I  --> S

    S  --> RE

    RE --> C
    RE --> N
    RE --> I
    RE --> X
```

## The Three Stages

### 1. Import

During import, CMDBsyncer connects to one or more source systems via [Accounts](accounts.md) and pulls in hosts along with their attributes — IP addresses, contacts, tags, hardware details, or any other key-value data. All of this is stored in the local CMDBsyncer database.

Sources can be databases, REST APIs, CSV files, Netbox, Checkmk, and more. Multiple sources can be imported in parallel and merged into a unified host inventory.

→ [Import documentation](import.md)

### 2. Rules Engine

Once data is in the database, the rules engine takes over. Rules allow you to:

- Add [custom attributes](custom_attributes.md) to hosts based on conditions
- [Rewrite](rewrite_attributes.md) or transform existing attribute values
- [Rewrite hostnames](rewrite_hostnames.md) to match naming conventions of the target system
- Use [conditions](conditions.md) to control which hosts are exported at all

The goal is to shape the data so that it fits the target system exactly — without touching the original source data.

### 3. Export

After the rules engine has processed the data, CMDBsyncer exports the result to the configured target systems. What exactly gets written depends on the target module — for example, Checkmk receives hosts with folders, tags, and labels, while Netbox receives device records with custom fields.

If a host disappears from all import sources, it is removed from the CMDBsyncer database after a grace period and subsequently deleted from the export targets as well.

→ [Export documentation](export.md)

## Bidirectional Sync

Some systems, like Checkmk or Netbox, can serve as **both** a source and a target at the same time. CMDBsyncer handles this cleanly: each direction is configured independently via its own account and job.

## Debugging

Before running a live sync, you can inspect all computed outcomes using the **command line interface**. This lets you verify which attributes and rules apply to each host without writing anything to the target system. Some modules, like Checkmk, also offer a web-based debug view directly in the UI.

→ [Debug documentation](debug.md)

## Architecture

CMDBsyncer is a **plugin-based** Python application. Every integration — whether for import or export — is implemented as a plugin with a straightforward API. The built-in plugins cover the most common systems out of the box; custom plugins can be added without modifying the core.

| Component       | Technology                                                     |
| :-------------- | :------------------------------------------------------------- |
| Application     | Python                                                         |
| Local database  | MongoDB                                                        |
| Admin interface | Flask-Admin                                                    |
| Deployment      | Native or [Docker](../installation/setup_docker.md)            |

→ [Build your own plugin](../advanced/own_plugins.md)
