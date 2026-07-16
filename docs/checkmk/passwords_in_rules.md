# Passwords in Setup Rules

Some Checkmk Setup Rules carry a secret — a special agent's password, an API
token, an SNMP community. This page explains how to keep such rules deployable
across several Checkmk instances (for example a **test** and a **production**
site) without ever putting the real secret into the rule.

## The problem: Checkmk masks passwords on read

When a rule stores a password *inline* (an "explicit" password), Checkmk returns
it **masked as `******`** on every read of that rule:

```python
'secret': ('cmk_postprocessed', 'explicit_password', ('uuid…', '******'))
```

So a rule read from one Checkmk carries no usable secret. If you copied that rule
to another Checkmk as-is, you would overwrite its password with `******`. This is
why rules [imported from a Checkmk folder](../basics/projects.md#import-rules-from-a-checkmk-folder)
can't simply be re-deployed with their inline password.

## The solution: reference the Syncer password store

Instead of inlining the secret, a rule references an entry in the Syncer's
[Password Store](password_store.md) with a Jinja macro:

```jinja
{{ cmk_password("name") }}
```

* `name` is the **Name** of a `CheckmkPassword` entry in the Syncer (_Modules →
  Checkmk → Manage Password Store_) — not its title.
* On rule export the macro resolves to that entry's Checkmk password-store ident,
  `cmdbsyncer_<id>`, which is **the same on every Checkmk instance** you export
  the password to.

The real secret lives only in the Syncer (encrypted) and in each Checkmk's own
password store — never inside the rule. A rule exported to test and to prod
resolves each site's own stored secret through the same ident.

## Imported rules are rewritten automatically

When you import Setup Rules from a Checkmk folder, every inline password is
rewritten into such a reference:

```python
# imported
'secret': ('cmk_postprocessed', 'explicit_password', ('uuid…', '******'))
# stored on the rule
'secret': ('cmk_postprocessed', 'stored_password', ('{{ cmk_password("secret") }}', ''))
```

* The default macro name is the value's field (here `secret`). Rename it on the
  rule to match your chosen password entry — a re-import keeps your renamed macro
  instead of reverting it.
* Non-password fields (e.g. an explicit proxy URL) are left untouched.
* After an import that found passwords, the Syncer tells you which names it used,
  in the import result and the log.

## You decide when passwords are pushed

A macro only resolves on a Checkmk instance whose password store already contains
the referenced entry. **The Syncer does not push passwords automatically during a
rule export** — that stays a job you run, so the rule export is not slowed down by
re-writing password-store entries on every run.

Populate a target Checkmk's password store with the password export:

```bash
./cmdbsyncer checkmk export_passwords <account>
```

This writes every *enabled* `CheckmkPassword` entry into that account's Checkmk
password store (creating or updating it).

## Workflow: test → prod

1. Create a **Checkmk Password** in the Syncer — a unique Name, the real secret,
   and **Enabled** ticked.
2. Point the rule at it: make sure the rule's value uses
   `{{ cmk_password("<that name>") }}` (imported rules already carry a macro you
   can rename).
3. Push the password to each target Checkmk once (and again after a rotation):

    ```bash
    ./cmdbsyncer checkmk export_passwords test-cmk
    ./cmdbsyncer checkmk export_passwords prod-cmk
    ```

4. Export the rules as usual:

    ```bash
    ./cmdbsyncer checkmk export_rules test-cmk
    ./cmdbsyncer checkmk export_rules prod-cmk
    ```

   The rules resolve the macro to the ident that now exists in each site's
   password store.

To **rotate** a secret, edit the entry in the Syncer and re-run
`export_passwords` for each target — the ident stays the same, so the rules do
not need re-exporting.

## Missing or disabled entries

If a referenced name has no `CheckmkPassword` entry — or the entry exists but is
**disabled** and was never exported — the macro resolves to a placeholder ident
that Checkmk rejects. Only that one rule fails to deploy (the failure is logged);
the rest of the export continues. Fix it by creating or enabling the entry and
running `export_passwords` for the target.
