# Jdisc

Starting with Version 3.8 the Syncer has support to Import Data from [JDisc](https://jdisc.com)

## How to Set it Up
1. Create an [Account](/basics/accounts/) of type JDisc Devices
2. Set the Fields  or Mode how you want to import. May use the GraphQL API. The How-to you find below
3. Import the Data using a [Cron Job](/basics/cron/) or from the command line (./cmdbsyncer jdisc import_hosts ACCOUNTNAME)
## The Account Settings
![](Pasted%20image%2020241016180411.png)
If you don't want to import devices as hosts, but as Objects instead, then make sure to set `is_object` and choose an Object type. Just let both settings empty in the normal case of importing hosts.

You have then multiple Ways of how specifying the Data you want to get from jdisc.
Save the Account just once, in order to see the default "Addional Configuration"


### Default Mode
In the Default mode, a Default Query is used for devices. It is configured like this:
![](Pasted%20image%2020241016175755.png)

The Keywords Matter, mode net to be set to devices and fields to default.
### Custom Fields
In this Mode, you set for fields the comma separated list of fields you want to get, and in mode the "table" from which.

### Custom Query
In the Custom Query mode, you can set of course every Graphql Query you want. Just make sure, to also set a matching `mode` field, otherwise the Syncer will fail to read the response.
Example like this:
![](Pasted%20image%2020241016180129.png)

## About Fields and Queries
To Figure out which Fields or query you want to use, enter JDiscs GraphiQL Interface and Play around with a query like this:


![](./attachments/Pasted%20image%2020241011165354.png)




## Rewrite Fields like role
You may notice that fields like roles come as a list.
That means they have the following Format:
['DeviceRole', 'value']. This is not useful if you want to export that, since you need a String Value not a list. But you can fix that with the Syncer, which Supports Jinja. Use the Rewrite Attributes Part for the Module you use to export like the following example.

![](./attachments/Pasted%20image%2020241011170657.png)

In This Example for the Attribute Name, I change it from roles to role and for the value, I convert the list to use the first value if existing, if not, fall back to undefined. The [helper get_list()](/advanced/jinja_functions) is used.



