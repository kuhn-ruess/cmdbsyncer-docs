# Export Rules
Export Rules manage how hosts will export to Checkmk. So, you can control in which Folder they will import and which attribute they will have. Note that the best way for folders is, to extract them from your Attributes.  Rules, who define Folders, are automatically stacked and result in a folder structure like _/this/is/my/folder_ out of all the outcomes.  It makes no difference if just one rule defines multiple outcomes, or multiple rule just define one outcome. At the End, it's just a long list of outcomes in the Order given by the Sort Field. It's recommended to make use of the last_match Option in Rules, to create the wanted Folder Paths. 

The Rules you can find in:
**Rules → Checkmk → CMK Export Rules**

Here you find their options explained:


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



