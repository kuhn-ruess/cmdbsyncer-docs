# How To: Deploy a Rule with a Password from Test to Prod

A concrete, click-by-click walkthrough of the recommended way to handle a secret
in a Setup Rule. For the concepts behind it, see
[Passwords in Setup Rules](passwords_in_rules.md).

**Scenario.** You have an Azure special-agent rule in your **test** Checkmk and
want the same rule in **production**, managed by the Syncer, without the secret
ever living inside the rule.

**Prerequisites.**

* Two enabled Checkmk (cmkv2) accounts in the Syncer, e.g. `test-cmk` and
  `prod-cmk`.
* A [Setup Rule Project](rule_projects.md) to hold the rule (e.g. `azure`).

---

## Step 1 — Import the rule from test

_Modules → Checkmk → Setup Rule Projects_ → open the **azure** project →
**Import Rules from Checkmk Folder**.

* **Checkmk account:** `test-cmk`
* **Folder:** `/azure`
* Click **Import**.

You get two messages:

* `Imported 1 rule(s) from folder '/azure' (account test-cmk)`
* `These rules reference password store entries: secret. Create a Checkmk
  Password in the syncer with each name (real secret), then run the password
  export …`

The imported rule now stores the secret as a reference, not the password:

```python
'secret': ('cmk_postprocessed', 'stored_password', ('{{ cmk_password("secret") }}', ''))
```

## Step 2 — (optional) Give the macro a clearer name

The default macro name is the field (`secret`). To use a nicer name, open the
rule under _Modules → Checkmk → Manage Checkmk Setup Rules_, and in the value
change `cmk_password("secret")` to e.g. `cmk_password("azure-prod")`. **Save.**

A later re-import of the folder keeps your renamed macro.

## Step 3 — Create the password in the Syncer

_Modules → Checkmk → Manage Password Store_ → **Create**.

| Field    | Value                                            |
| :------- | :----------------------------------------------- |
| Name     | `azure-prod` — **must match the macro**          |
| Title    | `Azure Prod Secret` (free label shown in Checkmk)|
| Password | the **real** secret                              |
| Enabled  | ticked                                           |

**Save.**

## Step 4 — Push the password to both Checkmks

The rule export does **not** push passwords for you, so do it once per target
(and again whenever you rotate the secret):

```bash
./cmdbsyncer checkmk export_passwords test-cmk
./cmdbsyncer checkmk export_passwords prod-cmk
```

Check in Checkmk under _Setup → Passwords_: an entry `cmdbsyncer_<id>` appears —
the same id on both sites.

## Step 5 — Export the rules

```bash
./cmdbsyncer checkmk export_rules test-cmk
./cmdbsyncer checkmk export_rules prod-cmk
```

Then **activate changes** in each Checkmk. Both sites now have the identical
rule, each resolving its **own** stored secret through the shared
`cmdbsyncer_<id>` reference.

---

## Rotating the secret

Edit the entry under _Manage Password Store_ and re-run the password export for
each target:

```bash
./cmdbsyncer checkmk export_passwords test-cmk
./cmdbsyncer checkmk export_passwords prod-cmk
```

The ident does not change, so the rules do **not** need re-exporting.

## Troubleshooting

* **A rule fails to deploy / Checkmk reports an unknown password** — the macro
  name has no matching `CheckmkPassword`, or the entry is **disabled** or was
  never exported. Only that one rule fails; the rest of the export continues.
  Fix the name / enable the entry, run `export_passwords` for the target, then
  `export_rules` again.
* **The rule still shows `******`** — you deployed before rewriting/creating the
  password. Re-import the folder (or edit the rule to add the macro), create the
  password, export it, and export the rule again.
