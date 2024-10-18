# Accounts

The Syncer uses accounts, which enables you to pass all kinds of information to your plugins. Here you will find how they work. Refer to the Module Account Sections to find about all the needed options.

You will find the settings in Accounts

## Basic Fields

| Field | Description |
|:----|:-----------|
| Name | Reference Name for the Account, used also in CI |
| Typ |  Typ of Account, only checks validation |
| Is Master | This Account can overwrite other accounts when import data |
| Is Object | Will not be exported as host, but attributes can be used in the rules |
| Address | URL or Hostname to the System, depending on the Module |
| Username | Username for the Account |
| Password | Password or Secret for the Account |
| Custom Fields | Extra Fields used by plugins |

Hint: Maybe you don't need all of the Fields. So, an API for example, could only need a Secret, so you would only need Name, Address and Password.

## Additional Configurations
In some cases, like when you create an Account for CSV Files or JSON Files, you need some special Modul-Specific fields for the Parameters. In this case, just save the account once, and the Fields will appear automatically.


## Reference Fields
In your configuration, you can reference to Fields you set here. So, you can hide Passwords, for example. You just have to use the {{ACCOUNT:...}} Macro.
Syntax is:
```
{{ACCOUNT:<ACCOUN_TNAME>:<ACCOUNT_FIELD_NAME>}}
```





