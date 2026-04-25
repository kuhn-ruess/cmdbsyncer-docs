# Ansible Projects

Ansible rules — Filter, Rewrite, Custom Variables and Playbook Fire — used to live in one global pool. Every inventory render walked every enabled rule, and there was no way to say "for this playbook, only use these rules". **Projects** add that dimension.

A project is a named group of rules. Each enabled project automatically becomes its own [inventory provider](inventory_providers.md), so the same selection mechanism that picks between `ansible` and `cmk_sites` now also picks between `prod-linux`, `dev-windows`, or whatever rule sources you define.

## What changes for existing installs

**Nothing breaks.** Rules without a project assignment keep working through the existing `ansible` provider — that's the legacy / global behaviour. There is no migration step. Projects are an opt-in layer on top: create a project, point some rules at it, point a playbook at the project, done.

## When to use a project

| Situation | Recommendation |
| :-------- | :------------- |
| One Ansible target system, all hosts feed the same rules | Stay project-less. Use the default `ansible` provider. |
| Two distinct rule worlds (prod vs. dev, Linux vs. Windows, customer-A vs. customer-B) that must not bleed into each other | Create one project per world; assign rules accordingly; pick the matching provider per playbook. |
| One shared rule set with a few project-specific overrides | Today: duplicate the shared rule into both projects. (Cascade is on the wishlist; no project = global is the only built-in cascade.) |

## Creating a project

**Modules → Ansible → Projects → Create**:

| Field | Notes |
| :---- | :---- |
| Name | Unique, alphanumeric (plus `_`, `-`, `.`). Cannot collide with built-in providers (`ansible`, `cmk_sites`). The provider name **is** the project name. |
| Description | Free text shown in the list view. |
| Enabled | Disabled projects are excluded from the resolver — their playbooks/rules go offline without losing the records. |

The new project is reachable as a provider immediately — no app restart:

```bash
cmdbsyncer inventory list-providers
ansible
cmk_sites
prod-linux              # ← the new project
```

## Assigning rules to a project

Every rule editor in the Ansible section has a **Project** dropdown in the Main Options card. Leave it blank to keep the rule global (served by `ansible`); pick a project to make it part of that project's isolated rule source.

The four rule types covered:

- **Filter** — only applies inside the chosen project's renderer.
- **Rewrite Attributes** — only applies inside the chosen project's renderer.
- **Ansible Attributes** (Custom Variables) — only applies inside the chosen project's renderer.
- **Playbook Fire Rules** — project is metadata for organization; firing happens project-wide via the cron command.

## Pointing a playbook at a project

Use the manifest's `inventory:` field to bind a playbook to the project's provider:

```yaml
# ansible/playbooks.local.yml
playbooks:
  - file: prod_linux_onboarding.yml
    name: "Prod Linux: Onboarding"
    inventory: prod-linux         # ← provider name = project name
```

The Run Playbook UI now dispatches that playbook against the inventory rendered by the `prod-linux` project's rules only. `dev-windows` rules are invisible to that run.

## Strict isolation

By design, a project's provider sees **only** rules with `project = <that project>`. Rules with `project = None` (global) are **not** mixed in. If you want a "common defaults plus project-specific overrides" model, duplicate the common rule into each project. We may add a cascade option later if there is demand.

## CLI / HTTP

Both transports are project-aware automatically — the resolver lives below them:

```bash
# Local CLI
cmdbsyncer inventory ansible prod-linux --list

# REST API
curl -H "x-login-user: USER:SECRET" \
  https://syncer/api/v1/inventory/ansible/prod-linux
```

The full provider listing exposes both static and dynamic (project-backed) names:

```bash
cmdbsyncer inventory list-providers
curl https://syncer/api/v1/inventory/ansible
```

## What about Playbook Fire Rules?

Fire rules carry a project field for organization, but the bundled `cmdbsyncer ansible fire_playbook_rules` command currently dispatches **all** enabled rules across **all** projects. Per-project firing would be a small follow-up (a `--project NAME` CLI flag); shout if you need it.
