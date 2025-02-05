# Syncronise IP Prefixes to Netbox

To Sync IP Prefixes to Netbox, find the Module:
_Modules → Netbox → IPAM Prefix_


## Single Attribute to Prefix
Set at least the Action Prefix as a Field.
In Param, you can use Jinja. From there we need the format IP/SUBNET which can come from multiple Attributes of the Host.
The System automatically makes sure, that there a no duplicate Updates


## Convert an IP with Subnet to Prefix
If you know the IP and the Subnet, you don't need to calculate the Prefix.
The Syncer has a helper Function for that.  

```python
'{{get_ip_network(ip+'/'+subnet)}}'
```
In the example is given that you have an attribute called ip, and one called subnet.

## Export a List of Prefixes per Object
If you have more than one IP, you can build a List in the Param Field. The Syncer will automatically detect if you try to build a Python List.

A list looks like this:
``` python
['entry1','entry2']
```

So if you have an Attribute with an list of IP and Subnets, it could look like this:

``` python
[{% for ip in attribute %}
	'{{get_ip_network(ip)}}',
{% endfor %}]
```

Note the `[` add the beginning, and the `]` add the end'
Also every entry is wrapped in ticks, and have a comma at the end.

## Iterate a List Variable with multiple IPs
If you use the Syncer to add the IPs and Interfaces to Netbox, the objects will have helper Variables with all the Data you need.

They always start with the Name of the Account you use, in this Example it's "Netbox"

For DCIM Interfaces its: `Netbox_dcim_interfaces` and for the Virtual Interfaces is `Netbox_virt_interfacs`

This Fields looks like this:

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

As you see, the key ipv4_addresses contain also a list. So a List in the List of Interfaces.

Now we combine two features, the Export a List as described before. And the 'Use List Variable Name'. First activate it, by check "Use list Variable". Then enter the Variable Name to iterate over.
In the "Param" Field, you then can use the Placeholder `LIST_VAR` to access the Loop Variable of the iteration of the list. 

Here the full example using the explained helper variable:

![](attachments/Pasted%20image%2020250122174134.png)

To copy:
``` python
[{% for ip in LIST_VAR['ipv4_addresses'] %}
'{{get_ip_network(ip)}}',
{% endfor %}]
```
Find all documentation about the List Feature [here](../basics/list_mode.md).
