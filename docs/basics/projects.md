# Projects

Projects group syncer objects — currently **Checkmk Setup Rules**, **DCD
rules** and **hosts** — and **limit which accounts they are exported to**.
A project can also be exported and imported as JSON to move it between
separate Syncer instances.

Go to: _Projects_ (top-level menu entry, next to _Modules_)

!!! note
    Projects are a generic concept, but today they are evaluated by the
    **Checkmk exports** only (Setup rules, DCD rules and the host export).
    Other modules will follow.

## Why projects?

Normally every enabled Setup Rule is exported to whichever Checkmk account you
run `checkmk export_rules` against, and every host to whichever account you run
`checkmk export_hosts` against. A project lets you:

* **group** rules and hosts that belong together, and
* **restrict** them to specific accounts via the project's account filters.

A project's members are exported through the normal export runs — there is no
separate push and no approval workflow.

## The account filters

Each project has two account lists:

* **Exported to Accounts** (`limit_by_accounts`) —
  empty means no restriction (the members are exported to **every** account);
  with entries, the members are exported **only** to those accounts.
* **Never export to Accounts** (`deny_by_accounts`) —
  the members are **never** exported to these accounts. The exclusion always
  wins over "Exported to Accounts".

So you can build a set of rules and hosts, keep them scoped to a lab/test
account while you try them out, and roll them out to the remaining accounts by
removing the filter — or keep single accounts permanently excluded via the
deny list.

!!! note
    A single `checkmk export_rules <account>` run always writes the account's
    global rules **plus** the rules of every project whose filters allow that
    account, under the account's normal ownership marker
    (`cmdbsyncer_<account_id>`). If an account later drops out of a project's
    filters, that project's rules are removed from it on the next export.

## Assign rules

Assign a Setup Rule or DCD rule to a project by picking the project in the
**Project** field of the rule's edit form.

## Assign hosts

Hosts can be assigned to a project in two ways:

* the **Project** field on the host edit form, or
* the **Assign Project** bulk action in the host list (select hosts →
  _With selected → Assign Project_).

The Checkmk host export then only pushes these hosts to the accounts the
project's filters allow — on excluded accounts the hosts are treated like any
other filtered host (not created, and cleaned up if they already exist there).

The bulk assignment is a plain field update: it never converts an imported
host into a CMDB object and does not touch any other host data.

## Configuration

| Option                   | Description                                                        |
| :----------------------- | :----------------------------------------------------------------- |
| Name                     | Unique project name                                                |
| Documentation            | Free text                                                          |
| Exported to Accounts     | Accounts the project's members are limited to (empty = all)        |
| Never export to Accounts | Accounts the members are never exported to (wins over the allow list) |

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
[Password Store](../checkmk/password_store.md) — a `{{ cmk_password("name") }}`
macro — and tells you which entry names it used.

Create a matching Checkmk Password in the Syncer, export it to each target Checkmk
(`export_passwords`), then export the rules. The full explanation is in
[Passwords in Setup Rules](../checkmk/passwords_in_rules.md), with a step-by-step
example in [How To: Use a Stored Password in a Rule Body](../checkmk/recipe_rule_passwords.md).

## Move a project between Syncer instances

Use the list actions **Export as JSON** (downloads the project and all of its
rules) and **Import** (upload such a file). This is useful when you build a
project on one Syncer instance and want to replicate it on another.

## Updating from 4.2.5 or earlier

Projects used to be "Setup Rule Projects" inside the Checkmk menu. After the
update, run

```bash
./cmdbsyncer sys self_configure
```

once — it migrates the existing projects to the new storage so they appear
under the new top-level _Projects_ entry.

## Command line

```bash
# Import all rules of a Checkmk folder into a project
./cmdbsyncer checkmk import_project_rules <PROJECT> <ACCOUNT> <FOLDER> --recursive

# Export rules (global + the projects whose filters allow this account)
./cmdbsyncer checkmk export_rules <ACCOUNT>

# Export hosts (project-assigned hosts only reach allowed accounts)
./cmdbsyncer checkmk export_hosts <ACCOUNT>
```
