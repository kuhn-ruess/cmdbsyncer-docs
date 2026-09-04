# Data Quality Check
<span class="since">Since 4.3</span>

Someone hands you a list of hostnames — an export from an asset system, a
spreadsheet from a colleague, the servers named in a ticket — and the question
is always the same: are these actually monitored? Does their agent work? Who is
allowed to see them? And what do we do with the ones that are missing?

The Data Quality Check answers that in one page. You give it the list, it asks a
Checkmk account, and it shows you a row per host. From the result you can create
the missing hosts in the Syncer's own CMDB and give the existing ones a CMDB
template.

Go to: _Modules → Checkmk → Data Quality Check_.

!!! note
    Running a check never changes anything in Checkmk. The two actions below the
    report write to the Syncer's CMDB only.

## Permissions

The page has its own permission, `Checkmk: Data Quality Check (this area only)`.
Give it to a user and they get this page and nothing else from the Checkmk
section — useful for a service desk that should look up hosts without being able
to touch rules or exports. Users with the full `Checkmk` right have it anyway.

Account and template restrictions apply here too: an account-restricted user only
sees their own accounts in the dropdowns, and a template-restricted user only
sees, picks and edits hosts carrying one of their templates.

## Check a list of hostnames

Pick a Checkmk account, then provide the hostnames in one of two ways:

- **Paste them** into the text box — one per line, or separated by commas,
  semicolons or spaces.
- **Upload a CSV**. A header cell named `hostname`, `host_name`, `host` or
  `name` picks the column; without such a header the first column is used.

If both are filled the pasted text wins. Duplicates are dropped, order is kept.

**Run check** fetches the account's monitored hosts and their `Check_MK` service
in two API calls and joins your list against them:

| Column | What it shows |
| :----- | :------------ |
| Host | The name as you provided it. |
| Status | `Present`, `Different name` or `Not found` — see below. |
| Name in Checkmk | For `Different name`, the name(s) the host actually has there. |
| Host state | `UP`, `DOWN` or `UNREACHABLE` from the monitoring. |
| Agent | State of the host's `Check_MK` service. `No agent` means the host is monitored but has no such service. Hover for the plugin output. |
| CMDB template | Whether the name is known in the Syncer's CMDB and which templates it carries there. |
| Contact groups | The groups allowed to see the host. |

The three status values:

| Status | Meaning |
| :----- | :------ |
| `Present` | The name exists in Checkmk exactly as given. |
| `Different name` | No exact match, but a host with the same short name — the part before the first dot — is monitored. This catches "created with a different domain" and "given without a domain but monitored with one". |
| `Not found` | Neither an exact nor a short-name match. |

**Copy result** puts the table on the clipboard, **Download CSV** saves it.

## Account-wide checks

The second card needs no host list — it scans everything the chosen account
monitors:

- **Find uppercase names** lists every monitored host whose name contains
  uppercase letters, together with the lowercase spelling it should have.
  Checkmk tells `SRV1` and `srv1` apart, so mixed-case names are a recurring
  source of duplicates.
- **Find hosts without FQDN** lists every monitored host whose name carries no
  dot.

## Create the missing hosts in the CMDB

When the report contains `Not found` rows, a card below it offers to create
them. They are preselected; untick what you do not want.

The hosts are created as regular Syncer-managed hosts with the source `cmdb` —
not as CMDB objects — so they show up in the normal host list and the ordinary
Checkmk export rolls them out. Hosts that already exist in the Syncer are never
overwritten; they are reported as skipped. Created hosts are marked as protected
from automatic deletion.

| Option | Description |
| :----- | :---------- |
| CMDB templates | Any number of them, picked from a filterable list. The new hosts carry all of the ones you tick and inherit their labels and attributes at export time. None means no template. |
| Domain name | Appended to every selected host that has no domain part. Hosts already given as an FQDN stay unchanged. |
| Create the names in lowercase | Lowercases the names before they are created, the appended domain included. <span class="since">Since 4.3.1</span> |

The lowercase toggle is what closes the loop with the uppercase scan above: a
name Checkmk reports as mixed-case can be carried into the Syncer in the
spelling it should have had, instead of importing the problem along with the
host.

!!! note
    A template-restricted user has to pick one of their own templates here.
    Without one the new hosts would be invisible to the person who just created
    them.

## Give an existing host a CMDB template

The last card lists the hosts from the report that are already in the CMDB, with
the ones carrying no template preselected. The chosen template is **added** to
what a host already has — nothing is replaced or removed, and a host that
already carries it stays untouched.

Templates and what they do are described under
[Use as CMDB](../cmdb/index.md).
