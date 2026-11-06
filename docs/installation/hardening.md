# Security Hardening

What an operator has to protect around the Syncer itself.

## Protect the database and its backups

Account passwords are stored encrypted with the `CRYPTOGRAPHY_KEY`. That does not hold for
everything derived from them: a rule that uses `{{ACCOUNT:name:field}}` stores its finished
result in the [cache](../basics/caching.md) of each host, and that result contains the value in
plain text. The cache lives in the MongoDB collection of the hosts. This is deliberate, as large
exports would otherwise get much slower.

So treat the database and every backup or dump of it like a password store:

- Enable authentication on MongoDB and don't expose it to the network.
- Only give people access to the database who may also see the account credentials.
- Store and transfer backups encrypted, with the same access limits as the database.

In the web interface the cached values in **View Cache Details** need the Account Management
permission.

## Masking on the debug page

The debug page of a host, the debug page of a Setup Rule, the preview of the Checkmk user
generation and the Checkmk folder pages hide account fields by a fixed list of names: `password`,
`password_crypted`, `api_token` and `bakery_passphrase`. Every other field stays readable, so a
secret in a custom field of your own, such as `my_token`, is shown there. Keep secrets in the
password field of the account or in the [Secret Store](../basics/secret_store.md), and only give
the debug page to users who may see the remaining account fields.
