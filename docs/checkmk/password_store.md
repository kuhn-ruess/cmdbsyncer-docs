# Password Store

The Syncer can create and update entries in the Checkmk Password Manager. This is useful when passwords — such as SNMP communities or service account credentials — are managed in your CMDB and need to be kept in sync with Checkmk.

Go to: _Modules → Checkmk → Manage Password Store_

## How Passwords Are Stored

Passwords entered in the Syncer are encrypted in the database. The encryption key is the `CRYPTOGRAPHY_KEY` from your `local_config.py`. If you change this key, you need to re-enter all stored passwords.

The Syncer decrypts the password internally before sending it to Checkmk — Checkmk never receives the encrypted form.

## Setup

Configure one entry per password. The fields correspond directly to what you would configure in the Checkmk Password Manager. Jinja templating is not yet supported in this module.

Each entry has a unique **Name**. In Checkmk the entry is stored under the stable ident `cmdbsyncer_<id>`, which is the same on every Checkmk instance you export it to.

## Referencing a password from a Setup Rule

A [Checkmk Setup Rule](rules_management.md) can reference a stored password instead of inlining it, so the secret never lives inside the rule:

```jinja
{{ cmk_password("name") }}
```

This resolves to the entry's Checkmk ident (`cmdbsyncer_<id>`) when the rule is exported. Use it wherever Checkmk expects a *stored* password, e.g. a special agent's `stored_password` value.

The macro only resolves on a Checkmk whose password store already holds the entry, so run `export_passwords` for that account before (or after) exporting the rules — the rule export does **not** push passwords for you. This reference is what lets rules imported from one Checkmk deploy to another without exposing the secret. See [Passwords in Setup Rules](passwords_in_rules.md) for the full workflow and [How To: Use a Stored Password in a Rule Body](recipe_rule_passwords.md) for a step-by-step example.

## Command Line

```bash
# Export every enabled password to an account's password store
./cmdbsyncer checkmk export_passwords ACCOUNTNAME
```
