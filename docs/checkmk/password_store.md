# Password Store

The Syncer can create and update entries in the Checkmk Password Manager. This is useful when passwords — such as SNMP communities or service account credentials — are managed in your CMDB and need to be kept in sync with Checkmk.

Go to: _Modules → Checkmk → Manage Password Store_

## How Passwords Are Stored

Passwords entered in the Syncer are encrypted in the database. The encryption key is the `CRYPTOGRAPHY_KEY` from your `local_config.py`. If you change this key, you need to re-enter all stored passwords.

The Syncer decrypts the password internally before sending it to Checkmk — Checkmk never receives the encrypted form.

## Setup

Configure one entry per password. The fields correspond directly to what you would configure in the Checkmk Password Manager. Jinja templating is not yet supported in this module.

## Command Line

```bash
./cmdbsyncer checkmk export_passwords ACCOUNTNAME
```
