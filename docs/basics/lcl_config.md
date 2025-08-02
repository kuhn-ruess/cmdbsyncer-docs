# APP Configuration

The application comes with some default Settings, for example to set the URL prefix or MongoDB Connection. The setting of this is important, if some links in the Backend won't work.
All what's set, you will find in _application/config.py_, but you should not change something in this file.
Instead, use the file _local_config.py_ in the root folder. It contains at least a dictionary called config. It it not yet exists, create it with __./cmdbsycer sys self_configure__  With the Keys of this Dictionary, you can overwrite every key from application/config.py, or you can add all the settings the Framework Flask has.

```
"""
Local Config
"""
config = {
    'LOWERCASE_HOSTNAMES' : True,
    'BASE_PREFIX' : '/cmdbsyncer/'
}
```


## Global Config Vars

| Name                       | Function                                                                                       |
| -------------------------- | ---------------------------------------------------------------------------------------------- |
| LOWERCASE_HOSTNAMES        | (bool) Force Hostnames to be Lowercase                                                         |
| STYLE_NAV_BACKGROUND_COLOR | Background Color for the Navigation Bar                                                        |
| SYLE_NAV_LINK_COLOR        | Color of the Navigation Links                                                                  |
| HEADER_HINT                | Free String shown in the Navigation                                                            |
| HTTP_REQUEST_TIMEOUT       | Timeout for HTTP Requests made by Plugins                                                      |
| SECRET_KEY                 | Key used to encrypt the session cookie                                                         |
| CRYPTOGRAPHY_KEY           | Key used to encrypt stored passwords                                                           |
| TIME_STAMP_FORMAT          | Python Formatstring for Date in log                                                            |
| HOST_LOG_LENGTH            | Number of Events logged to Hosts objects                                                       |
| CHECK_FOR_VALID_HOSTNAME   | Make sure that if object type is host, the hostname is valid (RFC)                             |
| ADMIN_SESSION_HOURS        | Hours bevore logout from Admin Panel                                                           |
| BASE_PREFIX                | Start part for the Url prefixed in links                                                       |
| SESSION_COOKIE_NAME        | Name of the login Cookie in syncer. Important if running multiple instances                    |
| LOG_LEVEL                  | Python Log Level, numeric or logging.DEBUG                                                     |
| LOG_CHANNEL                | Log Chanel, default: logging.StreamHandler()                                                   |
| PASSWD_MIN_PASSWD_LENGTH   | Min Password in case of Password Change                                                        |
| PASSWD_SPECIAL_CHARS       | `True or False`, Does Password needs Special Charts                                            |
| PASSWD_SPECIAL_DIGITS      | `True or False`, Does Password needs Digits                                                    |
| PASSWD_SEPCIAL_UPPER       | `True or False`, Does Password needs Uppercase Chars                                           |
| PASSWD_SEPCIAL_LOWER       | `True or False`, Does Password needs Lowercase Chase                                           |
| PASSWD_SPECIAL_NEEDED      | `int` Number of neede Special Chars of all groups.                                             |
| REPLACE_ATTRIBUTE_KEYS     | Also replace Keys of Attributes with given Replacers                                           |
| LOWERCASE_ATTRIBUTE_KEYS   | Store Attributes only with Lowercase Keys                                                      |
| LABELS_ITERATE_FIRST_LEVEL | IF Attribute contains value is a dict, the first keys of the dict will get seperate attributes |
| LABELS_IMPORT_EMPTY        | `True of False`, Set False to no loger import Labels which have no Value                       |
| REPLACERS                  | List of Tuples for Replacments                                                                 |
| DISABLE_SSL_ERRORS         | Ignore SSL Errors for HTTP Requests                                                            |
| HTTP_REQUEST_TIMEOUT       | Timeout for HTTP Requests                                                                      |
| HTTP_REPEAT_TIMEOUT        | Timeout between the Retries                                                                    |
| HTTP_MAX_RETRIES           | Number of Retries on failed HTTP Requests                                                      |
| SWAGGER_ENABLED            | `True or False` Disable or Enable the API Swagger for the Rest API                             |
| FILEADMIN_PATH             | Path for the Working Folder used in the GUIs Fileadmin                                         |
| ADVANCED_RULE_DEBUG        | For Development only: If enabled all Condition Matches will print if they match or not         |
## Modul Specific Config

- [Checkmk Config](../checkmk/config_vars.md)
