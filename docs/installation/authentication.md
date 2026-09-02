# Local Users

To log in, you first need to create a local user. The command to create one is:

```bash
./cmdbsyncer sys create_user mail@example.com
```

You can manage users in the UI under **Settings → User**.

## Permissions (roles)

A user is either a **global admin** (full access to everything) or is granted individual
permissions. Each permission unlocks the matching part of the UI:

| Permission | Grants access to |
|------------|------------------|
| Hosts / Objects | the Host and Objects lists |
| Account Management | the Accounts views |
| Projects <span class="since">Since 4.3</span> | the Projects views |
| Cron <span class="since">Since 4.3</span> | the Cron groups + status views |
| Data Quality <span class="since">Since 4.3</span> | the Data Quality dashboard |
| Generic Rules | Filter, Rewrite and Custom Attribute rules |
| Approvals | the critical-label approval queue |
| Log View, Files, User Management, … | the matching views |
| Checkmk / Netbox / Ansible / … | the per-module menus |
| Checkmk: Data Quality Check <span class="since">Since 4.3</span> | only the Checkmk Data Quality Check page, without the rest of the Checkmk menu |

!!! note "Since 4.3"
    Users without any Settings-area permission no longer see the **Settings** menu at all.
    "Projects" and "Cron" are now their own permissions (Projects used to require the Checkmk
    permission).

## API roles

Separately from the UI permissions, a user has **API roles** that gate the
[REST API](../internal_restapi/index.md). A role grants every endpoint below its path — e.g.
`objects` grants `/api/v1/objects/*`, `syncer` grants `/api/v1/syncer/*`; `all` grants
everything. Without a matching role the API returns 401.

## Personal API tokens
<span class="since">Since 4.3</span>

Every user can generate personal API tokens under **Profile → API Tokens** to authenticate
against the REST API instead of sending their password. A token carries the user's own API
roles and account scope, is shown once on creation, can be labelled and given an optional
expiry, and can be revoked any time. See
[REST API → Personal API tokens](../internal_restapi/index.md#personal-api-tokens).

## Read-only users
<span class="since">Since 4.3</span>

Ticking **Read only** on a user under **Settings → User** turns their account into a
look-but-don't-touch account. It works the other way round from the permissions above and
beats all of them, global admin included: the user keeps every view their roles open up and
can change nothing.

This covers both ways into the syncer:

* **Web interface** — no Create, Edit or Delete buttons, no bulk actions, no Commit button,
  no import or clone. Lists, detail pages, the log and the CSV export stay available.
* **REST API** — every reading call works as before, every writing one is answered with
  `403`. A [personal API token](#personal-api-tokens) authenticates as its owner and carries
  the flag, so it is no way around the restriction.

Two things stay open, because they are the user's own account rather than syncer data: their
password, 2FA, theme and API tokens, and their own saved searches.

!!! note "Read only cannot be lifted from inside"
    A read-only user cannot edit users either, so they cannot clear the flag on themselves.
    Another admin has to do it.

## Restricting a user to accounts
<span class="since">Since 4.3</span>

Under **Settings → User → Restrict to accounts** you can limit a user to one or more accounts.
When set, the user only sees and can act on hosts bound to those accounts — both in the REST
API and in the web-UI **Host** and **Objects** lists (and the bulk *Set Account* action only
offers those accounts). Leave it empty for full access.

## Restricting a user to CMDB templates
<span class="since">Since 4.3</span>

Under **Settings → User → Restrict to templates** you can limit a user to one or more CMDB
templates. It works like the account restriction, only on the template side: the user sees
just the hosts carrying one of those templates — in the web-UI **Host**, **Objects** and
**Archive** lists as well as over the REST API — and can only assign those templates, in the
host form and on the Checkmk Data Quality page. Leave it empty for full access.

Both restrictions can be combined: a user carrying an account *and* a template allowlist only
reaches hosts that satisfy each of them.

!!! note "Data Quality Check"
    On the Checkmk **Data Quality Check** page a restricted user also sees the hosts no
    template has claimed yet — those are the ones they may take over with their own template.
    Hosts carrying somebody else's template stay invisible, and creating hosts there requires
    picking one of their templates, so a newly created host does not disappear from its
    creator.
