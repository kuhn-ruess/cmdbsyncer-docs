# App Configuration

CMDBsyncer ships with sensible defaults defined in `application/config.py`. You should **never edit that file directly** — it is overwritten on updates.

Instead, create or edit `local_config.py` in the root folder. It contains a dictionary called `config` that overrides any key from `application/config.py`. If the file does not yet exist, generate it with:

```bash
./cmdbsyncer sys self_configure
```

Minimal example:

```python
"""
Local Config
"""
config = {
    'SECRET_KEY': 'your-secret-key-here',
    'CRYPTOGRAPHY_KEY': 'your-cryptography-key-here',
}
```

---

## General Settings

| Name                  | Default            | Description                                                            |
| :-------------------- | :----------------- | :--------------------------------------------------------------------- |
| `SECRET_KEY`          | `None`             | Key used to sign session cookies. **Must be set.**                     |
| `CRYPTOGRAPHY_KEY`    | `None`             | Key used to encrypt stored passwords. **Must be set.**                 |
| `BASE_PREFIX`         | `'/'`              | URL prefix if the app is mounted at a sub-path, e.g. `'/cmdbsyncer/'`  |
| `SESSION_COOKIE_NAME` | `'syncer'`         | Cookie name — change if running multiple instances on the same host    |
| `ADMIN_SESSION_HOURS` | `2`                | Hours before automatic logout from the admin panel                     |
| `HEADER_HINT`         | `''`               | Free text string shown in the navigation bar                           |
| `TIME_STAMP_FORMAT`   | `'%d.%m.%Y %H:%M'` | Python date format string used in the log                              |
| `HOST_LOG_LENGTH`     | `30`               | Number of log events stored per host object                            |
| `HOST_PAGESIZE`       | `100`              | Number of hosts shown per page in the host list                        |
| `ADVANCED_RULE_DEBUG` | `False`            | Print every condition match result to console (development only)       |

---

## MongoDB Connection

Override any field by setting the matching environment variable before
starting the application, or by adding `MONGODB_SETTINGS` to `local_config.py`:

```python
config = {
    'MONGODB_SETTINGS': {
        'db': 'cmdb-api',
        'host': 'mongo.internal',
        'port': 27017,
        'alias': 'default',
    },
}
```

| Key     | Default     | Env Override               | Description                          |
| :------ | :---------- | :------------------------- | :----------------------------------- |
| `db`    | `cmdb-api`  | `CMDBSYNCER_MONGODB_DB`    | Database name                        |
| `host`  | `127.0.0.1` | `CMDBSYNCER_MONGODB_HOST`  | Hostname or IP of the MongoDB server |
| `port`  | `27017`     | `CMDBSYNCER_MONGODB_PORT`  | TCP port                             |
| `alias` | `default`   | `CMDBSYNCER_MONGODB_ALIAS` | MongoEngine connection alias         |

The Docker Compose setup uses `mongo` as the default host (service name); a
plain `pip` install defaults to `127.0.0.1`.

---

## Hostname and Attribute Handling

| Name                         | Default   | Description                                                                         |
| :--------------------------- | :-------- | :---------------------------------------------------------------------------------- |
| `LOWERCASE_HOSTNAMES`        | `False`   | Force all hostnames to lowercase on import                                          |
| `CHECK_FOR_VALID_HOSTNAME`   | `True`    | Reject imports where object type is Host but the hostname is not RFC-valid          |
| `LOWERCASE_ATTRIBUTE_KEYS`   | `False`   | Store all attribute keys in lowercase                                               |
| `REPLACE_ATTRIBUTE_KEYS`     | `False`   | Apply the `REPLACERS` list to attribute keys as well as values                      |
| `LABELS_ITERATE_FIRST_LEVEL` | `False`   | If an attribute value is a dict, import its first-level keys as separate attributes |
| `LABELS_IMPORT_EMPTY`        | `False`   | Set to `True` to also import attributes with empty values                           |
| `REPLACERS`                  | see below | List of `(from, to)` tuples applied to attribute values during import               |

Default `REPLACERS` list (replaces special characters to produce clean attribute values):

```python
config = {
    'REPLACERS': [
        (' ', '_'),
        ('/', '_'),
        (',', '-'),
        ('&', '-'),
        ('ü', 'ue'),
        ('ä', 'ae'),
        ('ö', 'oe'),
        ('ß', 'ss'),
    ],
}
```

---

## HTTP and SSL

| Name                   | Default | Description                                                              |
| :--------------------- | :------ | :----------------------------------------------------------------------- |
| `HTTP_REQUEST_TIMEOUT` | `30`    | Timeout in seconds for outgoing HTTP requests                            |
| `HTTP_REPEAT_TIMEOUT`  | `3`     | Seconds to wait between retries on failed requests                       |
| `HTTP_MAX_RETRIES`     | `2`     | Maximum number of retries on failed HTTP requests                        |
| `DISABLE_SSL_ERRORS`   | `False` | Globally disable SSL verification (deprecated — use per-account setting) |

---

## Password Policy

| Name                       | Default | Description                                        |
| :------------------------- | :------ | :------------------------------------------------- |
| `PASSWD_MIN_PASSWD_LENGTH` | `9`     | Minimum password length                            |
| `PASSWD_SPECIAL_CHARS`     | `True`  | Require at least one special character             |
| `PASSWD_SPECIAL_DIGITS`    | `True`  | Require at least one digit                         |
| `PASSWD_SEPCIAL_UPPER`     | `True`  | Require at least one uppercase letter              |
| `PASSWD_SEPCIAL_LOWER`     | `True`  | Require at least one lowercase letter              |
| `PASSWD_SPECIAL_NEEDED`    | `3`     | Minimum number of the above rules that must be met |

---

## UI and API

| Name                         | Default                 | Description                                                                             |
| :--------------------------- | :---------------------- | :-------------------------------------------------------------------------------------- |
| `STYLE_NAV_BACKGROUND_COLOR` | `'#000'`                | Background color of the navigation bar                                                  |
| `STYLE_NAV_LINK_COLOR`       | `'#fff'`                | Color of navigation links                                                               |
| `SWAGGER_ENABLED`            | `True`                  | Enable or disable the Swagger UI for the REST API                                       |
| `LABEL_PREVIEW_DISABLED`     | `False`                 | Disable the label preview in the host view                                              |
| `REMOTE_USER_LOGIN`          | `False`                 | Accept the remote user header for SSO authentication                                    |
| `LDAP_LOGIN`                 | `False`                 | Enable LDAP authentication (see [LDAP Login](ldap.md))                                  |
| `FILEADMIN_PATH`             | `/var/cmdbsyncer/files` | Working directory for the Fileadmin (also settable via env `CMDBSYNCER_FILEADMIN_PATH`) |

---

## Module-Specific Settings

- [Checkmk Config Variables](../checkmk/config_vars.md)
- [Logging Configuration](logging.md)
- [LDAP Login](ldap.md)

---

## Netbox-Specific Settings

| Name                   | Default | Description                                             |
| :--------------------- | :------ | :------------------------------------------------------ |
| `NETBOX_IMPORT_NESTED` | `False` | Also import nested/related objects during Netbox import |
