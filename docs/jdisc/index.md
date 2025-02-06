# Jdisc

Starting with Version 3.8 the Syncer has support to Import Data from [JDisc](https://jdisc.com).

It's possible to Import Devices, Applications and Executables.
The needed GraphQL Queries are already hardcoded into the Syncer so no need to worry.


## How to Set it Up
1. Create an [Account](/basics/accounts/) of type JDisc Devices
3. Import the Data needed using a [Cron Job](/basics/cron/) or from the command line (./cmdbsyncer jdisc import_XXX ACCOUNTNAME)

## The Account Settings
In the Account Settings, you just need to set up the URL and Credentials to JDisc. Depending on which command you run later, the objects are imported automatically into the right category.


## Rewrite Fields like role
You may notice that fields like roles come as a list.
That means they have the following Format:
['DeviceRole', 'value']. This is not useful if you want to export that, since you need a String Value not a list. But you can fix that with the Syncer, which Supports Jinja. Use the Rewrite Attributes Part for the Module you use to export like the following example.

![](./attachments/Pasted%20image%2020241011170657.png)

In This Example for the Attribute Name, I change it from roles to role and for the value, I convert the list to use the first value if existing, if not, fall back to undefined. The [helper get_list()](/advanced/jinja_functions) is used.