# Limit Host Export to Folders

Limit the **host export** of a single Checkmk account to a chosen set of
folders. When a scope is set, `checkmk export_hosts <account>` only pushes the
hosts whose target folder is in the selection — every other host is ignored.
Subfolders are included automatically.

Go to: _Modules → Checkmk → Limit Host Export to Folders_

## Why?

A typical use case is populating a **test** Checkmk instance with only a slice
of production: you point a test account at a few folders and its export then
carries just the hosts of those folders, instead of every host. Combined with
[Setup Rule Projects](rule_projects.md) — which stage the *rules* of the same
folders — you get a test instance that holds exactly the rules and the hosts of
the approved folders.

## How it works

The scope is stored as the account custom field **`limit_by_folders`** (a
comma-separated list of folders). During `checkmk export_hosts`, each host's
target folder (the one produced by your
[folder rules](export_rules.md)) is compared against the list:

* no `limit_by_folders` set → the account exports **all** hosts (unchanged
  behaviour);
* `limit_by_folders` set → only hosts whose folder **is, or is below,** one of
  the listed folders are exported.

The match is recursive, so selecting `/test` also covers `/test/linux`,
`/test/linux/web01`, and so on. A folder typed without a leading slash
(`test/linux`) is treated the same as `/test/linux`.

!!! note
    The scope only affects the **one account** it is set on. Production or any
    other accounts are never touched. Hosts that fall out of scope are treated
    like any other no-longer-synced host and are removed from that Checkmk
    instance on the next export (only hosts carrying this account's
    `cmdb_syncer` label — manually created hosts are left alone).

## Configuration on the page

1. Pick the Checkmk account. The dropdown marks each account as *folder scope
   active* or *no scope (all hosts)*.
2. A banner shows clearly whether the scope is **active** (export limited) or
   **disabled** (account exports every host).
3. Tick the folders you want. The list is derived from your configured rules
   (the folders that Setup Rules and `move_folder` / `create_folder` /
   folder-pool rules produce). Jinja-templated folders can't be listed but still
   match at export time.
4. Add any **custom folders** — comma-separated — that no rule produces.
5. **Save folder scope.** The account's host export is now limited to those
   folders.

To disable the scope again, clear the selection (untick everything, empty the
custom field) and save — the account goes back to exporting all hosts.

## Setting it without the page

`limit_by_folders` is a normal account custom field, so you can also set it
directly on the account (see [Account Parameters](accounts.md)), e.g.
`limit_by_folders = /test/linux,/test/windows`. It works together with the
other export limits `limit_by_accounts` and `limit_by_hostnames`.
