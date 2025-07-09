# Accounts

The Syncer uses accounts, which enables you to pass all kinds of information to your plugins. Here you will find how they work. Refer to the Module Account Sections to find about all the needed options.

You will find the settings in Accounts

## Basic Fields

| Field         | Description                                                           |
| :------------ | :-------------------------------------------------------------------- |
| Name          | Reference Name for the Account, used also in CI                       |
| Typ           | Typ of Account, only checks validation                                |
| Is Master     | This Account can overwrite other accounts when import data            |
| Is Object     | Will not be exported as host, but attributes can be used in the rules |
| Object Type   | For future function to help filter objects in a better way            |
| Address       | URL or Hostname to the System, depending on the Module                |
| Username      | Username for the Account                                              |
| Password      | Password or Secret for the Account                                    |
| Custom Fields | Extra Fields used by plugins                                          |

Hint: Maybe you don't need all the Fields. So, an API for example, could only need a Secret, so you would only need Name, Address and Password.

## About Objects and Object Types
The flag `is Object`, basically does not add the imported Object into the Hosts view, but the Object view. But all Attributes of the Objects can still be accessed in Rule. 
Currently also a object is not exported as Host to other Systems, but with the in 3.8 introduced "Objects Filter" (see below) you can filter that more flexible.

### The Object Types
Object Types are assigned also on import. They help you later to better filter objects on exports, but some have even more functions.

If the Object Type is set to Host, then the import will not save objects, which would have an invalid Hostname but log an error instead. 


## Additional Configurations
![](attachments/Pasted%20image%2020241126165050.png)
In some cases, like when you create an Account for CSV Files or JSON Files, you need some special Model-Specific fields for the Parameters. In this case, just save the account once, and the Fields will appear automatically.

### Documentations by Account Type
 - [Checkmk](../checkmk/accounts.md)
 - [Netbox](../netbox/account.md)
 - [Jira](../jira/index.md)
 - [Inventorize Options](host_labels_inventory.md/#account-options-for-inventorize-scripts)

### (Almost) Global Available Options

| Field                              | Description                                                                                                                                                                                                                                                               |
| :--------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| delete_host_if_not_found_on_import | Enter a  Mongoengine Filter for a Field in Format fieldname:value to instant delete hosts on import operations from the syncer, if the matching host not longer is part of this import. A Docu for Filters [click here](https://docs.mongoengine.org/guide/querying.html). You cann add multiple Filters by seperating them with two pipes (\|\|). They are connected by AND then. |

## Extra Plugin Options
In this section you can set plugin-based account options. That means even when you use the same account for different actions, you can still used action specific parts which you can configure here.

### Object Filter
When set, the Plugin only uses objects with the given types for the operation.

![](attachments/Pasted%20image%2020241126165023.png)




## Reference Fields
In your configuration, you can reference to Fields you set here. So, you can hide Passwords, for example. You just have to use the {{ACCOUNT:...}} Macro.
Syntax is:
```
{{ACCOUNT:<ACCOUN_TNAME>:<ACCOUNT_FIELD_NAME>}}
```




# Config Child's

A config Child is just the Child of a Normal Account. It inherits every setting from there, but overwrites the Custom Fields and the Plugin Config (if set)

In this way, you don't need to create multiple Accounts in the case you need e.g. multiple Filters or Plugin Settings for different Situations.

 