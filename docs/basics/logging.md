# Logging

CMDBsyncer logs in two places simultaneously: the **web log** in the GUI and the **Python logging system** for console and external log targets.

## Web Log

Every sync run creates an entry in the web log, accessible under **Log** in the admin panel. It shows:

- Metrics per run (hosts processed, errors, duration)
- Per-host errors highlighted in red
- Which account and command was involved

This is the most practical place to monitor ongoing syncs without needing shell access.

## Python Logging

CMDBsyncer uses the Python `logging` module for console and syslog output. The configuration follows the standard [Python logging dict config](https://docs.python.org/3/howto/logging-cookbook.html) format and can be fully overridden via the `LOGGING` key in [local_config.py](lcl_config.md).

Two loggers are always required and must not be removed:

- **`debug`** — used internally for debug output to the console
- **`syslog`** — used for structured output to an external destination

The `LOG_LEVEL` key is a quick shortcut to change the log level without replacing the full config.

### Example: Change log level only

```python
config = {
    'LOG_LEVEL': 'DEBUG',  # one of: DEBUG, INFO, WARNING, ERROR, CRITICAL
}
```

### Example: Log to remote syslog server (UDP)

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
                'address': ['192.168.1.10', 514],  # remote syslog host and port
                'facility': 'local6',
                'formatter': 'syslog',
            },
        },
        'loggers': {
            'debug':  {'handlers': ['console'], 'level': 100,    'propagate': 'True'},
            'syslog': {'handlers': ['syslog'],  'level': 'INFO', 'propagate': 'True'},
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
            'debug':  {'handlers': ['console'], 'level': 100,    'propagate': 'True'},
            'syslog': {'handlers': ['syslog'],  'level': 'INFO', 'propagate': 'True'},
        },
    },
}
```

### Example: Log to file

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
            'debug':  {'handlers': ['console'], 'level': 100,    'propagate': 'True'},
            'syslog': {'handlers': ['syslog'],  'level': 'INFO', 'propagate': 'True'},
        },
    },
}
```

## Monitoring

To get notified about problems within CMDBsyncer processes, a Checkmk check is available on the [Checkmk Exchange](https://exchange.checkmk.com/p/cmdb-syncer).
