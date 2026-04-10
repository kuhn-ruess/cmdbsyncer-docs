# Update Notes

<!-- NOTICES -->

Before every update, check this page for breaking changes that require manual action.

After every update, always run:

    ./cmdbsyncer sys self_configure

This automatically adapts configuration changes and adds missing default values to `local_config.py` — for example, the `CRYPTOGRAPHY_KEY`.

---

## MongoDB

The MongoDB used by CMDBsyncer also needs updates from time to time.

If you are using the Docker Compose files provided by us and do not skip Syncer versions, no action is required.

If you manage your own installation or your own Docker config, keeping MongoDB up to date is your responsibility. CMDBsyncer has no hard requirement for a specific MongoDB version, but updates fix bugs and improve performance.
