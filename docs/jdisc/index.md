# Jdisc

Starting with Version 3.8 the Syncer has support to Import Data from [JDisc](https://jdisc.com)

## How to Set it Up
1. Create an [Account](/basics/accounts/) of type JDisc Devices
2. Set the Fields you want to import from Devices. Used is the GraphQL API. The How to you find below
3. Import the Data using a [Cron Job](/basics/cron/) or from command line (./cmdbsyncer jdisc import_hosts ACCOUNTNAME)

## The Fields
In the Account you need to configure the Comma Separated Lists of Fields you would like to import. A default is, of course, set when you save the Account. To Figure out which Fields you need, enter JDiscs GraphiQL Interface and Play around with a query like this:


![](./attachments/Pasted%20image%2020241011165354.png)

Marked on the Screenshot, you find the Fields you need to Enter.
Example Account where some Fields are set.

![](./attachments/Pasted%20image%2020241011165737.png)

## Rewrite Fields like role
You may notice that fields like roles come as a list.
That means they have the following Format:
['DeviceRole', 'value']. This is not useful if you want to export that, since you need a String Value not a list. But you can fix that with the Syncer, which Supports Jinja. Use the Rewrite Attributes Part for the Module you use to export like the following example.

![](./attachments/Pasted%20image%2020241011170657.png)

In This Example for the Attribute Name, I change it from roles to role and for the value, I convert the list to use the first value if existing, if not, fall back to undefined. The [helper get_list()](/advanced/jinja_functions) is used.



