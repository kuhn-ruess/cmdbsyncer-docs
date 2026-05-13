# Update Notes

<!-- NOTICES -->

Before every update, check this page for breaking changes that require manual action.

After every update, always run:

    ./cmdbsyncer sys self_configure

This automatically adapts configuration changes and adds missing default values to `local_config.py` — for example, the `CRYPTOGRAPHY_KEY`.

---

## Upgrading from 3.x to 4.x: `CRYPTOGRAPHY_KEY` recovery

In versions before 3.12.4, `application/config.py` shipped with a hardcoded
default `CRYPTOGRAPHY_KEY`. If your `local_config.py` did **not** define
`CRYPTOGRAPHY_KEY` (or defined it under a typo'd name, e.g.
`CRYPTO__GRAPHY_KEY`), your account passwords were silently encrypted
using that built-in default.

Starting with 3.12.4 the default is `None`. After the upgrade, decrypting
existing account passwords fails with:

    cryptography.fernet.InvalidToken

To recover your existing passwords, add the **old default key** to your
`local_config.py` (note the `b''` prefix — it must be `bytes`, not `str`):

```python
config = {
    ...
    'CRYPTOGRAPHY_KEY': b'nto4ioGgQDlJ-r5jqvyEtTpUQC2fkOAG4Df-E8OlVm8=',
    ...
}
```

After that, the syncer can decrypt all stored passwords again.

### Rotating to your own key afterwards

If you want to replace the well-known default with your own fresh key,
write the **current** key as a plain string (no `b''` prefix) into
`local_config.py`:

```python
'CRYPTOGRAPHY_KEY': 'nto4ioGgQDlJ-r5jqvyEtTpUQC2fkOAG4Df-E8OlVm8=',
```

Back up MongoDB, then run:

    ./cmdbsyncer sys self_configure

`self_configure` detects the string form, generates a new key,
re-encrypts every account password with it, and writes the new key back
to `local_config.py` in the proper `bytes` form.

---

## MongoDB

The MongoDB used by CMDBsyncer also needs updates from time to time.

If you are using the Docker Compose files provided by us and do not skip Syncer versions, no action is required.

If you manage your own installation or your own Docker config, keeping MongoDB up to date is your responsibility. CMDBsyncer has no hard requirement for a specific MongoDB version, but updates fix bugs and improve performance.
