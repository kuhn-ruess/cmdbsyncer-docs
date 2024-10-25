#IPAM IP Addresses

This Module Targets the IP Address management in Netbox.
If you used the Syncer to export the Interfaces, you can easily also match the IP Addresses to the correct Interface.

In this case, you will find the following Attribute with your host:

![](./attachments/Pasted%20image%2020241025173114.png)

The Name always depends on the Account Name you're using for Netbox. In this Example, it is set to "netbox".

From there it's easy to access the Data.
That is to set in Modules -> Netbox -> IPAM IP Addresses.

![](./attachments/Pasted%20image%2020241025173329.png)

The Syntax exmpained:

`get_list()` converts the Attribute back into the list it's it. Lists are covered in brackets: `[LIST]`. Inside this List, there is a Dictionary which you can access now. It's on the first postition, therefore `[0]`. And from there `used_ip` is access:

```
{{get_list(netbox_interfaces)[0]['used_ip']}}
```

