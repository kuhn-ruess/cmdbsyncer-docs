# Setup Rule Projects

Rule Projects group [Checkmk Setup Rules](rules_management.md) and **limit which
Checkmk accounts they are exported to**. A project can also be exported and
imported as JSON to move it between separate Syncer instances.

Go to: _Modules → Checkmk → Setup Rule Projects_

## Why projects?

Normally every enabled Setup Rule is exported to whichever Checkmk account you
run `checkmk export_rules` against. A project lets you:

* **group** Setup Rules that belong together, and
* **restrict** those rules to specific Checkmk accounts via an account filter.

A project's rules are exported through the normal `export_rules` run — there is
no separate push and no approval workflow.

## The account filter

Each project has an **Exported to Accounts** list (`limit_by_accounts`):

* **empty** — no restriction: the project's rules are exported to **every**
  account, exactly like ordinary rules;
* **one or more accounts** — the project's rules are exported **only** to those
  accounts. `checkmk export_rules <other-account>` skips them.

So you can build a set of rules, keep them scoped to a lab/test account while you
try them out, and roll them out to the remaining accounts simply by **removing
the filter** (or adding the other accounts to it).

!!! note
    A single `checkmk export_rules <account>` run always writes the account's
    global rules **plus** the rules of every project whose filter allows that
    account, under the account's normal ownership marker
    (`cmdbsyncer_<account_id>`). If an account later drops out of a project's
    filter, that project's rules are removed from it on the next export.

## Configuration

| Option              | Description                                                             |
| :------------------ | :--------------------------------------------------------------------- |
| Name                | Unique project name                                                    |
| Documentation       | Free text                                                              |
| Exported to Accounts | Checkmk accounts the project's rules are limited to (empty = all)     |

Assign a rule to a project by picking the project in the **Project** field of a
Checkmk Setup Rule.

## The project page

Click a project's **name** in the list to open its overview page. It shows the
project's target accounts and lists every Setup Rule assigned to the project —
each with its match condition and the resulting rule value — and offers:

* **Import Rules from Checkmk Folder** (see below),
* **Export as JSON**,
* jump straight to editing a rule, adding a new one, or managing the project's
  rules in the Setup Rule list.

## Import rules from a Checkmk folder

You can seed a project from rules that already exist in Checkmk:

Open the project page → **Import Rules from Checkmk Folder** → choose a Checkmk
account and a folder. (The same action is also on the *With selected* menu in
the project list.)

* Every Setup Rule in that folder is imported into the project as a **static
  rule** (its value and conditions are taken over verbatim, so exporting it back
  reproduces the exact same Checkmk rule).
* Tick **Include subfolders** to also import rules from folders below the given
  one.
* Re-running the import **updates the same rules** instead of creating
  duplicates (rules are matched by their Checkmk rule ID).

### Passwords in imported rules

Checkmk masks an inline (explicit) password in a rule as `******` on every read,
so a rule imported from your test Checkmk carries **no usable secret**. The import
therefore rewrites every inline password into a reference to the Syncer's
[Password Store](password_store.md) — a `{{ cmk_password("name") }}` macro — and
tells you which entry names it used.

Create a matching Checkmk Password in the Syncer, export it to each target Checkmk
(`export_passwords`), then export the rules. The full explanation is in
[Passwords in Setup Rules](passwords_in_rules.md), with a step-by-step example in
[How To: Deploy a Rule with a Password](recipe_rule_passwords.md).

## Move a project between Syncer instances

Use the list actions **Export as JSON** (downloads the project and all of its
rules) and **Import** (upload such a file). This is useful when you build a
project on one Syncer instance and want to replicate it on another.

## Command line

```bash
# Import all rules of a Checkmk folder into a project
./cmdbsyncer checkmk import_project_rules <PROJECT> <ACCOUNT> <FOLDER> --recursive

# Export rules (global + the projects whose filter allows this account)
./cmdbsyncer checkmk export_rules <ACCOUNT>
```
