#Hosts, Labels and Inventory

CMDB Syncer works with Hosts, Labels and Inventory. So far so simple, but what is what?

## Hosts
A Host is any kind of Device. It's identified by his hostname, bound to a source and contains
Labels and Inventory


## Labels and Inventory
Labels and Inventory are mostly the same, but have an important difference.
They both are Key:Value pairs, can be used in all Rules, Rewritten and Filtered.

The difference is only how they are dealt with their creation.
While the Labels are imported and fully under control of the Import Plugin,
can inventory data come from multiple sources. Inventory Keys share their sources identify, as a prefix on their name.

Example:

- csv__ipaddress:127.0.0.1
- csv__alias:Test Server
- srctest__service_name: Test Service

In this example, you see Inventory Data of two sources, one is csv, the other is srctest.
So, the plugin using the key csv, will control all keys with csv/ and the plugin with srctest as key, the others.


## Account Options for Inventorize Scripts
To get the Inventory, every Module has an Inventorize Endpoint. This Endpoint is configured using the Account. For Example you can use the same Checkmk Account to Export and to Inventorize, but it needs some more Options then.


| Option                      | Description                                                                                                                                                                                               |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| inventorize_key             | Which prefix should be used for the attributes names                                                                                                                                                      |
| inventorize_match_by_domain | (not everywhere available yet) if true, the Inventory Data <br>will match by domain Name                                                                                                                  |
| inventorize_match_attribute | Set an attribute name, then the wanted value.<br> e.g. application=dns. The Data is then only added to this hosts <br>inventory, if the hosts has an application attribute containing dns.          |
| inventorize_collect_by_key  | Enter an Attribute name.<br> If this Attribute Name is found on the Host, and Contains <br>the Name of another Host, this other Host<br> gets the Attribute added (numerated)<br> containing his hostname |



