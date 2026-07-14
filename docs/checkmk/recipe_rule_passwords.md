# How To: Use a Stored Password in a Rule Body

A concrete example of writing a Setup Rule whose value carries a secret, using a
reference to the Syncer [Password Store](password_store.md) instead of an inline
password — and how to convert a rule body you copied out of Checkmk where the
password was **explicit**. For the concepts, see
[Passwords in Setup Rules](passwords_in_rules.md).

## The rule body

A [Checkmk Setup Rule](rules_management.md) in the Syncer carries, per outcome, a
**Value** — the Checkmk `value_raw`, written as a Python literal (a dict). It is
rendered with Jinja before it is sent to Checkmk, so you can use macros inside it.

For a value that holds a secret, write the password field as a **stored_password**
reference to a Syncer password entry:

```python
('cmk_postprocessed', 'stored_password', ('{{ cmk_password("NAME") }}', ''))
```

* `NAME` is the **Name** of a `CheckmkPassword` entry in the Syncer.
* `{{ cmk_password("NAME") }}` resolves, on export, to that entry's Checkmk
  password-store ident (`cmdbsyncer_<id>`) — the same on every Checkmk instance.
* The second tuple element stays an empty string `''` (a stored password carries
  no value in the rule).

## Step 1 — Create the password in the Syncer

_Modules → Checkmk → Manage Password Store → Create_:

| Field    | Value                        |
| :------- | :--------------------------- |
| Name     | `my-api` (used in the macro) |
| Title    | `My API user` (label in Checkmk) |
| Password | the **real** secret          |
| Enabled  | ticked                       |

## Step 2 — Write the rule body

_Modules → Checkmk → Manage Checkmk Setup Rules → Create_. Pick the ruleset and
folder, and put the body in the outcome's **Value**. A minimal special-agent
example:

```python
{
    'user': 'svc-monitoring',
    'password': ('cmk_postprocessed', 'stored_password', ('{{ cmk_password("my-api") }}', '')),
    'port': 443,
}
```

Save. That is all — the secret never appears in the rule.

## Adapting a rule body copied from Checkmk

Often you already have a working rule in Checkmk and want the Syncer to manage it.
Copy its `value_raw` (Setup → the rule → *Export for API*, or the REST API's
`value_raw`) into the outcome Value, then fix up the password.

If that password was entered **explicitly** in Checkmk, its body looks like this —
note Checkmk returns the secret **masked as `******`**, so it is useless to
copy as-is:

```python
# copied from Checkmk — password was explicit, value is masked
{
    'user': 'svc-monitoring',
    'password': ('cmk_postprocessed', 'explicit_password', ('uuid-7f3c…', '******')),
    'port': 443,
}
```

Replace the `explicit_password` tuple with a `stored_password` reference:

```python
# managed by the Syncer — real secret lives in the password store
{
    'user': 'svc-monitoring',
    'password': ('cmk_postprocessed', 'stored_password', ('{{ cmk_password("my-api") }}', '')),
    'port': 443,
}
```

Concretely, for each secret field:

1. Change `'explicit_password'` → `'stored_password'`.
2. Replace the inner `('uuid…', '******')` with `('{{ cmk_password("NAME") }}', '')`.
3. Leave every other field (ports, proxies, options) exactly as Checkmk returned
   it.

## Step 3 — Make the password available and export

The rule only resolves on a Checkmk whose password store already holds the entry,
and the rule export does **not** push passwords for you. So push the password
once per target (and again after a rotation), then export the rules:

```bash
./cmdbsyncer checkmk export_passwords my-cmk
./cmdbsyncer checkmk export_rules my-cmk
```

Activate changes in Checkmk. The rule now uses the password from that site's own
store.

## Troubleshooting

* **Checkmk reports an unknown password / the rule fails to create** — the macro
  name has no matching `CheckmkPassword`, or the entry is disabled or was never
  exported. Only that rule fails; fix the name / enable the entry, run
  `export_passwords`, then `export_rules` again.
* **The password shows as `******` in Checkmk** — you left the `explicit_password`
  tuple in the body. Swap it for the `stored_password` reference as shown above.
