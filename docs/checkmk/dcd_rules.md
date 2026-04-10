# DCD Rules

Starting with Checkmk 2.3, you can manage DCD (Dynamic Configuration Daemon) rules via the Syncer. Unlike most other Checkmk modules, the DCD API currently supports creating and deleting rules but not updating them in place — so this module creates and deletes rules rather than syncing them.

Go to: _Modules → Checkmk → Manage DCD Rules_

DCD rules are configured using the same Syncer rule system as all other modules. You can use Jinja templates in almost every field. The available options mirror what you would configure directly in the Checkmk DCD UI.

## Command Line

```bash
./cmdbsyncer checkmk export_dcd_rules ACCOUNTNAME
```
