# Logging

Logging is a important function for a Application which needs to run in the Background. Therefore, the Syncer Contains multiple options you can use.

## The Web Logging
Every Action creates an Entry inside the Log, which you can find in the GUI. There you find not only Metrics, but also the error on Objects you are exporting. 

Log entries, which contain an error, are also marked with a red sign.

## Flexible Syslog Logging
As of v3.8.2, everything which is logged in the Weblog, and depending on the log level even more, is also logged with the logging module of python. In fact, if you use --debug the log level of this Module is set to Debug, and on your Console you see more this Detailed Output.

You can adapt the behavior to your personal needs, by overwriting the key "LOGGING" from application/config.py, within your local_config.py.

Just make sure, to not break Syncers Behavior. There always needs to by the `console`handler, and the `debug` logger. But the `syslog` handler, you can overwrite to send messages to an external Log Server. 

Some documentation you also find [here](https://docs.python.org/3/howto/logging-cookbook.html#logging-cookbook)

## Monitoring 

To get notified about Problems within the Syncer Processes, you can use a Checkmk Check which you find in the [exchange](https://exchange.checkmk.com/p/cmdb-syncer)

