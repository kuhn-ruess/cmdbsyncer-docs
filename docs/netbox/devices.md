
# DCIM Devices
If you want to sync your Devices to Netbox, you find all information how to set this up here.


## Fields
With Version 3.8 the Syncer exports all Fields by their name. No need to know any Netbox IDs anymore. Every field supports Jinja. So you only need to write your Attributes in Jinja Style as Variables. So don't forget to add the brackets around.
Here are some advanced Examples including Jinja Code Examples for more advanced problems.

![](attachments/Pasted%20image%2020241126153035.png)

Some fields are always required in order that the call can work.
Therefore, all fields with * in front of the Name need to be set.


## Fields which need Reference
In Some cases, the Data Model of Netbox requires references to differnd Objects. Like a Device needs a Device Type, a Device Type needs a Manufacturer. The Syncer creates these objects as well, up to three levels deep, fully automatically.


## Netbox Api Versions
WARNING: Netbox did a Change in their API and changed a Field from device_role to just role.
Please note that you need to update your syncer if you run in a problem about missing device_role payload.
The Syncer in default always works with the current Netbox Version.
To support older Versions, a chance to make this work is to Downgrade the pynetbox module used by syncer