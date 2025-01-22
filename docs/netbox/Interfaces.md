# DCIM Interfaces

The Syncer can create Interfaces in Netbox. 
This can be set in Modules -> Netbox -> DCIM Interfaces.

As in other Syncer Functions, you can match your Host Attributes to Netbox Attributes.  Here you will find some Examples.

The "ID of Assigned Device" for example, can be found in an Attribute like "accountname_device_id". This attribute is automatically set when you used the device export of the Syncer. But the name depends on the Account Name you used. The part accountname is replaced by this Accounts Name. 

An example value, if the Account's name is netbox, would be `{{netbox_device_id}}` The Brackets are the Jinja Syntax for Variables.

Like the Device Export, also this Interface Export will automatically add information to the Host inside the Syncer. This then can be used to Export IP Addresses.

## Full Example

### Hosts Attributes
In the Example, the Host as the Attribute `mainip4transport` with the following Value:
``` json
{'hostnames': [], 'ipAddress': '172.30.50.121', 'subnetMask': '255.255.255.0', 'networkInterface': {'physicalAddress': '00:50:56:96:25:0c', 'index': 2, 'extendedDescription': 'ens192', 'operationalStatus': 'Up', 'speed': 10000000000}, 'network': {'name': None, 'nameManuallyConfigured': None, 'networkBaseAddress': '172.30.50.0', 'subnetMask': '255.255.255.0'}}
```

And Some others which you see here:
![](./attachments/Pasted%20image%2020241025172319.png)

### Accessing Host Attributes
The Following Functions can be used, to Access these Attributes:

![](./attachments/Pasted%20image%2020241025171047.png)

To get the Examples Description:
```json
{{mainip4transport['networkInterface']['extendedDescription']}}
```


### Accessing IP and Convert Subnet.
Our Example contains a IP Address and a Subnet Mask. But that does not meat Netbox Requirements for the IP Address. We need the form `127.30.50.121/32`. Luckly the Syncer has a helper to convert that:
`get_ip4_network()`

We just pass the IP Address and the Subnet Mask to it.
In the Example, the fields `mainipaddress` and `mainip4transport` to create a String (`+`) to create `127.30.50.21/255.255.255.0` and from there it's passed to the Helper:

```json
{{ get_ip_interface(mainipaddress+"/"+mainip4transport['subnetMask']) }}
```



## Use List Variables
This Rule can also use [List Mode](../bascis/list_mode.md). Here are some Examples for fields. The Information of course need to Exist on the Syncer Objects.

### For Name:

``` python
{{HOSTNAME }} 
{% if LIST_VAR['extendedDescription'] %}
 {{LIST_VAR['extendedDescription']}}
{%else%}
 {{LIST_VAR['description']}}
{% endif %}
```
Here the Interface name Starts with the Host's Name, then if existing the extended description, else the normal description.

### Interfaces Address

```python
{% for ip in LIST_VAR['ip4Transports'] %}
{% set ip_address = ip['ipAddress'] %}
{% set subnet_mask = ip['subnetMask'] %}
{% if not subnet_mask%}
{% set subnet_mask = "255.255.255.0" %}
{% endif %}
{{ get_ip_interface(ip_address+'/'+subnet_mask) }},
{% endfor %}
```
To helper Variables are used, to store the IP to `ip_address`, and the subnet to `subnet_mask`. And then there is a Fallback if `subnet_mask` is empty.