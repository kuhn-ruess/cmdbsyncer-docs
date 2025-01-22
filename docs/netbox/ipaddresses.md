#IPAM IP Addresses

This Module Targets the IP Address management in Netbox.
If you used the Syncer to export the Interfaces, you can easily also match the IP Addresses to the correct Interface.

In this case, you will find two Attributes with your Hosts:
For DCIM Interfaces its: `Netbox_dcim_interfaces` and for the Virtual Interfaces is `Netbox_virt_interfacs`

This is, what it looks like:

``` python
[
 {'port_name': 'sysname lo0',
  'netbox_if_id': 1462,
  'ipv4_addresses': ['127.0.0.1/8'], 
  'ipv6_addresses': []},
 {'port_name': 'sysname en0; Product: Virtual I/O Ethernet Adapter (l-lan)', 
  'netbox_if_id': 1461,
  'ipv4_addresses': ['172.30.71.204/24', '172.30.71.154/28'],  
  'ipv6_addresses': []
 }
]
```


The Name always depends on the Account Name you're using for Netbox. In this Example, it is set to "Netbox".

From there it's easy to access the Data.
That is to set in Modules → Netbox → IPAM IP Addresses.

![](attachments/Pasted%20image%2020250122174729.png)

Here the Feature [List Mode](../basics/list_mode.md) is used. It allows you to iterate over a Variable quite Easily.

