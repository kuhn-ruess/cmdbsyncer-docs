# Logging

CMDBsyncer logs in two places simultaneously: the **web log** in the GUI and the **Python logging system** for console and external log targets.

## Web Log

Every sync run creates an entry in the web log, accessible under **Log** in the admin panel. It shows:

- Metrics per run (hosts processed, errors, duration)
- Per-host errors highlighted in red
- Which account and command was involved

This is the most practical place to monitor ongoing syncs without needing shell access.

## Python Logging

Besides the web log, every entry a sync run produces is handed to the
Python `logging` module, so it can be forwarded to a console, a syslog
server, a log file or any other log pipeline. The configuration follows
the standard [Python logging dict config](https://docs.python.org/3/howto/logging-cookbook.html)
format and can be fully overridden with the `LOGGING` key in
[local_config.py](lcl_config.md).

Two loggers are always required and must not be removed:

- **`debug`** — the human-readable console output. Muted by default
  (level `100`); switch it on for a single run with `--debug`, or
  permanently with `LOG_LEVEL`.
- **`syslog`** — the external sink. This is the one to point at your log
  destination. It receives *every* entry, exactly like the Log view in
  the interface, and it does not propagate, so the external copy is
  never duplicated onto the console.

!!! note
    A `LOGGING` block in `local_config.py` is applied from version 4.3
    on. Earlier versions built the logging pipeline before the local
    configuration was read and silently discarded the override.

### Example: Change log level only

`LOG_LEVEL` raises the level of both loggers without having to restate
the whole `LOGGING` dict:

```python
config = {
    'LOG_LEVEL': 'DEBUG',  # one of: DEBUG, INFO, WARNING, ERROR, CRITICAL
}
```

### Example: Log to remote syslog server (UDP)

!!! warning
    The `address` has to be a **tuple**, not a list — Python's socket
    layer rejects a list and every log entry ends in a handler error.

```python
config = {
    'LOGGING': {
        'version': 1,
        'disable_existing_loggers': 'False',
        'formatters': {
            'verbose': {'format': '%(levelname)s - %(message)s'},
            'syslog':  {'format': '%(levelname)s - %(message)s'},
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
            'syslog': {
                'class': 'logging.handlers.SysLogHandler',
                'address': ('192.168.1.10', 514),  # remote syslog host and port
                'facility': 'local6',
                'formatter': 'syslog',
            },
        },
        'loggers': {
            'debug':  {'handlers': ['console'], 'level': 100,    'propagate': True},
            'syslog': {'handlers': ['syslog'],  'level': 'INFO', 'propagate': False},
        },
    },
}
```

### Example: Log to local Unix socket (rsyslog on Linux)

```python
config = {
    'LOGGING': {
        'version': 1,
        'disable_existing_loggers': 'False',
        'formatters': {
            'verbose': {'format': '%(levelname)s - %(message)s'},
            'syslog':  {'format': '%(levelname)s - %(message)s'},
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
            'syslog': {
                'class': 'logging.handlers.SysLogHandler',
                'address': '/dev/log',  # local Unix socket
                'facility': 'local6',
                'formatter': 'syslog',
            },
        },
        'loggers': {
            'debug':  {'handlers': ['console'], 'level': 100,    'propagate': True},
            'syslog': {'handlers': ['syslog'],  'level': 'INFO', 'propagate': False},
        },
    },
}
```

### Example: Log to file

The directory has to exist and has to be writable for the user the
Syncer runs as — in a container that means mounting it into the
container as well.

```python
config = {
    'LOGGING': {
        'version': 1,
        'disable_existing_loggers': 'False',
        'formatters': {
            'verbose': {'format': '%(levelname)s - %(message)s'},
            'syslog':  {'format': '%(levelname)s - %(message)s'},
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
            'syslog': {
                'class': 'logging.FileHandler',
                'filename': '/var/log/cmdbsyncer.log',
                'formatter': 'syslog',
            },
        },
        'loggers': {
            'debug':  {'handlers': ['console'], 'level': 100,    'propagate': True},
            'syslog': {'handlers': ['syslog'],  'level': 'INFO', 'propagate': False},
        },
    },
}
```

### Structured output

The handlers above write plain text lines. If the log has to be machine
readable — JSON for Elasticsearch, Loki, Splunk or another collector —
see [JSON Logging](../enterprise/json_logging.md).

## Monitoring

To get notified about problems within CMDBsyncer processes, a Checkmk check is available on the [Checkmk Exchange](https://exchange.checkmk.com/p/cmdb-syncer).
