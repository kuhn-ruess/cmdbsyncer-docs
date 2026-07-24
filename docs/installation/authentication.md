# Local Users

To log in, you first need to create a local user. The command to create one is:

```bash
./cmdbsyncer sys create_user mail@example.com
```

You can manage users in the UI under **Profile → Users**.

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

## Restricting a user to accounts
<span class="since">Since 4.3</span>

Under **Profile → Users → Restrict to accounts** you can limit a user to one or more accounts.
When set, the user only sees and can act on hosts bound to those accounts — both in the REST
API and in the web-UI **Host** and **Objects** lists (and the bulk *Set Account* action only
offers those accounts). Leave it empty for full access.
