# Setup Rule Projects (Test → Approve → Prod)

Rule Projects group [Checkmk Setup Rules](rules_management.md) so you can build
them safely on a **test** Checkmk instance, get them **approved**, and then push
them to **production** as one unit. A project can also be exported and imported
as JSON to move it between separate Syncer instances.

Go to: _Modules → Checkmk → Setup Rule Projects (Test/Prod)_

## Why projects?

Without a project, every enabled Setup Rule is pushed to a single Checkmk
instance on each `checkmk export_rules` run — there is no staging and no
approval. A project gives you:

* a **group** of Setup Rules that belong together,
* its own **test** and **production** Checkmk target,
* a **status workflow** with an audit trail (who approved, when),
* one-click **import** of existing rules from a Checkmk folder,
* **JSON im-/export** for multi-instance setups.

Rules that belong to a project are **excluded from the global
`export_rules`** — they are only ever pushed through the project workflow, so
test rules can never reach production before they are approved.

## Configuration

| Option        | Description                                                        |
| :------------ | :---------------------------------------------------------------- |
| Name          | Unique project name                                               |
| Documentation | Free text                                                         |
| Status        | `draft` → `in_test` → `approved` → `live` (see below)             |
| Test Instance | Checkmk account the project is pushed to for testing             |
| Prod Instance | Checkmk account the project is pushed to for production          |

Assign a rule to a project by picking the project in the **Project** field of a
Checkmk Setup Rule.

## Workflow

The project status advances automatically as you work through it:

1. **draft** — you create the project and assign rules to it.
2. **Push to Test** — pushes the project's rules to its *Test Instance*; the
   status moves to **in_test**.
3. **Approve for Production** — a reviewer marks the project **approved**; the
   approver's e-mail and the timestamp are recorded.
4. **Push to Prod** — pushes to the *Prod Instance*; the status moves to
   **live**. This is **only allowed once the project is approved** — an attempt
   to push an unapproved project to production is refused.

Each action is available in the list view (select one or more projects, then
pick the action from the *With selected* menu).

### Sharing a Checkmk instance between projects

Rules pushed by a project are tagged in Checkmk with a project-specific
ownership marker (`cmdbsyncer_<account_id>_<project>`). Cleanup during a push
only ever touches rules carrying that project's own marker, so **several
projects can push to the same Checkmk instance without deleting each other's
rules** (and without touching the rules of the global `export_rules`, which
keeps the plain `cmdbsyncer_<account_id>` marker).

## Import rules from a Checkmk folder

You can seed a project from rules that already exist in Checkmk:

Select the project → **Import Rules from Checkmk Folder** → choose a Checkmk
account and a folder.

* Every Setup Rule in that folder is imported into the project as a **static
  rule** (its value and conditions are taken over verbatim, so pushing it back
  reproduces the exact same Checkmk rule).
* Tick **Include subfolders** to also import rules from folders below the given
  one.
* Re-running the import **updates the same rules** instead of creating
  duplicates (rules are matched by their Checkmk rule ID).

## Move a project between Syncer instances

Use the list actions **Export as JSON** (downloads the project and all of its
rules) and **Import** (upload such a file). This is useful when you build a
project on one Syncer instance and want to replicate it on another. An imported
project always starts in status **draft** — it never inherits an
`approved`/`live` status from the source instance.

## Command line

```bash
# Push a project's rules to its test or prod instance
./cmdbsyncer checkmk export_project_rules <PROJECT> --stage test
./cmdbsyncer checkmk export_project_rules <PROJECT> --stage prod

# Import all rules of a Checkmk folder into a project
./cmdbsyncer checkmk import_project_rules <PROJECT> <ACCOUNT> <FOLDER> --recursive
```

Both `export_project_rules` (Test/Prod) and `import_project_rules` are also
available as cron jobs.
