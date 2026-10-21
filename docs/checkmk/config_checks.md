# Configuration Checks
<span class="since">Since 4.5</span>

A Checkmk site collects leftovers over the years: rules nobody needs any more,
two checks doing the same job, migrations that were started and never finished.
The Configuration Checks look at the setup of a site and list these problems,
each with the rules involved and what to do about it. The list can be exported
as a PDF report.

Go to: _Modules → Checkmk → Data Quality → Configuration Checks_.

!!! note
    The checks only read from Checkmk. They never change, delete or activate
    anything. Cleaning up is up to you, with the report in hand.

## Permissions

The page belongs to the Data Quality area: users with the `Checkmk` right or
the role `Checkmk: Data Quality Check (this area only)` can open it.
Account-restricted users only see their own accounts.

## Run checks

1. Pick the Checkmk account.
2. Tick the checks to run. All of them are ticked by default.
3. **Run checks** shows one card per check.

Each card is split by topic, one topic per kind of problem:

- At the top, the numbers of what the check looked at (rules, endpoints, ...)
  and a **summary** with the number of findings per topic and in total. A click
  on a topic jumps to its section.
- Then one **section per topic**: its title with the number of findings, what
  the topic means, what to do about it, and a table with the columns that fit
  this topic (a failing service has host, state and output, a duplicate has URL,
  scope and the checks involved). Topics without findings show "No findings".

Every rule involved is given with its id, to find it in Checkmk.

## Export as PDF

**Export PDF** runs the selected checks again and downloads the result as a PDF
file, named after the account and the date, e.g.
`checkmk-config-checks-cmk01-2026-10-21.pdf`. The report is in the design of
your Syncer installation (logo on a band in the color of the navigation bar),
A4 landscape, with the same summary and sections per topic as on the page.

The PDF export needs the Python package `fpdf2`, which is part of the extras:

```bash
pip install 'cmdbsyncer[extras]'   # or just: pip install fpdf2
```

The Docker image installs the extras already. Without the package the page and
the checks work as usual; only the **Export PDF** button is disabled and says
which package is missing.

## HTTP web service checks (check_httpv2)

Checkmk replaced the old active check `check_http` by `check_httpv2` (rule
_Check HTTP web service_). The old check needed one rule for the web page and a
second rule for the certificate. The new one checks both in a single endpoint,
but `cmk-migrate-http` turns every old rule into a new rule of its own. After the
migration a site therefore often has two checks per URL where one is enough.

The check reads the rules of `active_checks:httpv2` and `active_checks:http`
and the state of the HTTP check services. Disabled rules are skipped.

### Failing checks

Every HTTP check service, new `check_httpv2` as well as old `check_http`, that
is **WARN, CRIT or UNKNOWN** in the monitoring right now is listed first, the
worst state on top: host, service, state and the output of the check. The rule
behind the service is named when the service name of an enabled rule matches
(for an old rule `HTTP` or `HTTPS` plus its name). Service names built from
macros such as `$HOSTNAME$` cannot be traced back to a rule; the report says so.
Nothing is acknowledged or changed in Checkmk.

### When two endpoints check the same thing

Each endpoint of each rule is compared with its effective settings: the
standard settings of the rule, overwritten by the individual settings of the
endpoint (the same way Checkmk combines them). Two endpoints check the same
target when

- their rules are in the same folder,
- their rules have the same conditions,
- their URLs are equal (scheme and host name in any case, with or without the
  default port 80 or 443 and a trailing `/`),
- and they connect to the same server (the setting _Connect to specific host_).

Endpoints in different folders or with different conditions are never compared,
even if their hosts overlap.

### Topics

The report has these sections, in this order:

| Topic | Meaning | What to do |
| :---- | :------ | :--------- |
| HTTP checks not OK | HTTP check services that are WARN, CRIT or UNKNOWN right now (see above). Columns: host, service, state, output, rule. | Fix the web service, or the rule if it checks something that is not there any more. |
| Duplicate checks | Two or more endpoints with identical settings check the same target. Only the service name may differ. | Keep one, remove the others. |
| Website and certificate checked separately | One endpoint only checks the certificate, another one checks the web page of the same target. | Set _Certificate validity_ of the web page check to _Check certificate_ with the levels of the certificate check, then remove the certificate check. If the web page check already checks the certificate, just remove the certificate check. The table says which applies. |
| Several checks on the same URL | More than one endpoint with different settings on the same target, e.g. two different expected texts. Often intended, so this is information only. | Check whether all of them are needed. |
| Migration not finalized | Old rules that `cmk-migrate-http` already migrated, but the migration was not finalized: old and new rule both run. | Finalize the migration with `cmk-migrate-http finalize` or disable the old rules. |
| Old check_http rules not migrated | Old rules without a migrated counterpart, e.g. ones the migration skipped. | Migrate them. |

An endpoint counts as a **certificate check** when it checks the certificate
with expiry levels (_Certificate validity_ set to _Check certificate_ with fixed
levels) and sets none of _Response time_, _Response_ (status codes),
_Content_ or a _Document_ option other than ignoring the body. Every other
endpoint counts as a **web page check**.

When the certificate check uses other connection settings than the web page
check, the report names the settings that differ (never their values), so you
can carry them over when merging.

## Adding a check

The checks are modules in `application/plugins/checkmk/config_checks/`. A new
check is a class derived from `ConfigCheck` with a `name`, `title`,
`description`, its `topics` and an `analyze(cmk)` method that returns the
problems found (`Finding`) and a few numbers about what it looked at.

Each `Topic` declares its title, what it means, what to do and the columns of
its table (`Column` with a key and a type: text, code, state or a list of
rules). A `Finding` names its topic and carries one value per column. The page
and the PDF report build the summary and the sections from that, so a new check
or a new topic needs no template change. Registered with `@register_check` and
imported in the package's `__init__.py`, the check shows up on the page.
