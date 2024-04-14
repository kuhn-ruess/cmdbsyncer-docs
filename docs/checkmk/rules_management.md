# Manage Checkmk Rules

Out of the box, it's possible in Checkmk to create Rules with not much effort. This applies to Threshold Rules and also to for Rules which activate Active Checks, for example. But as soon every Check needs a custom Parameter, it gets harder to set up.

The CMDB Syncer can help here in two Ways. He can add custom Attributes to your Hosts, which you then can use in some of the rules. This is described [here](cmk_attributes.md)

As alternative, you can use this Feature of Syncer, to create a bigger bunch of rules. And the best here, the Syncer also deletes the rules again, if not needed.

## Configuration Options
**Rules → Checkmk → CMK Rules Management**<br>
Below you find the Description for the Parameters found in the Admin Panel:


 |Function     |  Description  |
 | --- | --- |
 |  Move to Folder   |   Hardcode a custom Folder Name in _action_param_ field. <br> You can use Jinja Attributes to Nest a deeper Folder Levels.<br> If a Variable not match, the rule will be ignored.  |
 | Folder by Attribute Name | Pick Attribute by Value and use Key as Foldername |
 | Pool Folder | Matching Host will use a Pool Folder. <br>If not action_param is given, the system will query from all folders.<br>Otherwise you can provide a comma seperated <br>list of Folder Pool Names.<br><br>For more Details, please refer to the [Folder Pool Documentation](folder_pools.md).
 | CMK Atribute by Syncer Attribute | The given Attribute Name will be sent as Checkmk Attribute.<br>This way you can set every Attribute you want<br>like ipaddress of management board.<br>Please refer to the [documentation in Recipes](cmk_attributes.md). |
 | Custom CMK Attributes | You can specify a new Attribute as key value pair,<br>separated by double point. <br>You can use {{HOSTNAME}} as placeholder to create for example:<br>managmentboard:rib-{{HOSTNAME}} as new attribute. <br> Return Multiple Attributes, seperated by Comma<br> Usefull for for-loops.|
 | Cluster | The Matching Host will be created as a Cluster in Checkmk.<br>Since Cluster have Nodes, you need<br>to tell syncer in witch attribute <br>he will findtheir Names. <br>You can add the Attributes comma seperated, <br>and use * as Wildcard add the end of the Name. <br><br>See also the [Documentation](create_cluster.md).|
 | Parents | Set parent, Jinja Support |
 | Move Optout | Matching Host will never be moved after intial creation |
 | Update Optout | Attributes of Matching Host will never be <br> Update after inital creation |
 | Prefix Labels | Every label exported gets the configured prefix |
 | Update only Prefixed Labels | Syncer will only change labels, which have the given prefix |













# Recipes
- [Manage Contact Groups](recipe_contact_groups.md). Example of course works for all kind of groups.

