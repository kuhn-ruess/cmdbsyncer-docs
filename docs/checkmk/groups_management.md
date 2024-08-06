# Groups Management

The Group Management Feature let you create contact-, Host- and Service-Groups based on Attributes you get from your Hosts.

The Syncer has a local Cache for all groups he created. That can be found in Rules → Checkmk → Object Cache. This is needed in order that the Syncer know which groups he can safely remove from Checkmk. So groups you created yourself are not touched. 
If you would delete the Cache Entry, the Syncer only takes over the groups with the next sync, if they are provided from your source again.

Also note, Checkmk has the Limitation that you can't have groups with the same name, even if it's another type. So, you can't have Contact Groups with the same name as Hostgroups. Use the Rewrite feature when needed.





## Rule Parameters
The Rule to configure everything you find in:

**Modules → Checkmk → Manage Host-/Contact-/Service - Groups**<br>


| Option        | Description                                                                                                                                             |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Group Name    | Create Contact Group, Host Groups or Service Groups                                                                                                     |
| Foreach Type  | Iterate either an Attribute, values of an Attribute, or Objects                                                                                          |
| Foreach       | The Attribute or Value, depending on Foreach Type. <br> If you use by Value, you can use a * to indicate<br>every Value starting with. Example:  dhcp*  |
| Rewrite       | Rewrite the id of the Group, by Using Jinja.  {{name}} will refer to the found value                                                                    |
| Rewrite Title | Same, but for the Group's Title                                                                                                                          |


## Example
Let's say you Hosts have an attribute **application** stating their job.  Then How to set all that **application** attributes to become a Checkmk Contact Group, and use cg_ as a prefix in their Name.

Set __Group Name__ to *Contact Groups*, **Foreach Type** to *Foreach Attribute*, and as **Foreach** you set *application* (application is the attribute your Hosts have). If you just want the attribute value, you're done. But since we want the prefix, we set **Rewrite** to *cg_{{name}}* and **Rewrite Title** just to *{{name}}*. That's it, now "Commit Changes" and export the Groups to Checkmk.

## Export from Commandline
If you want to export the groups to checkmk manually, not using Cron you can do:

**./cmdbsyncer checkmk export_groups ACCOUNTNAME**