As of Syncer 3.12 there is a function that the Syncer can create his own rules, based on Attributes he has discovered.

## Setup Example
But best explain this with an Example.
Imaging, you have a high amount of Checkmk Sites. You want then automatically distribute your hosts with that sites. Anytime you add a new site, you want the Syncer to find that site and create the necessary configuration.

You need the following steps:
1) Get the Site Information from Checkmk
2) Create Folder Pools for each Site you found
3) Create an Assignment Rule for each Pool Folder, only assigning matching hosts.

### Getting the Site Information from Checkmk
Use the Module "Checkmk: Import Sites" as one of your Cronjobs. It can be used with the normal Account you use to connect Checkmk. The Import will create one object for all of your configured sites. The Entry will contain the labels site_id and alias, which you then can use in your rules. Of course, you can also assign Custom Attributes to this Objects if needed. The Object will have the Type "Cmk Site" which you then later can use to filter.

### Create Folder Pool Rules
_Modules -> Syncer Rules -> Automate Syncer Rule Creation_

Use:
  - Rule Type: "CheckmkFolderPool"
  - Object Filter: "Checkmk Site Object"

Body:

``` jinja
{"name": "Rule for {{ site_id }}",
 "folder_name": "/{{ site_id }}", 
 "folder_title": "Hallo {{ alias }}", 
 "folder_seats": 10, 
 "assigned_site_id": "{{ site_id }}",
 "enabled": true}

```
Note the ```{{ site_id }}``` which we get from the Objects Label.

### Create Checkmk Host Rules

The Checkmk Attributes rule works same:

Use:
  - Rule Type: "CheckmkRule"
  - Object Filter: "Checkmk Site Object"

Body:

``` jinja
{
  "name": "Move to Pool {{ site_id }}",
  "documentation": "",
  "condition_typ": "all",
  "conditions": [
    {
      "match_type": "tag",
      "hostname_match": "equal",
      "hostname": "",
      "hostname_match_negate": false,
      "tag_match": "equal",
      "tag": "attribte_x",
      "tag_match_negate": false,
      "value_match": "equal",
      "value": "true",
      "value_match_negate": false
    }
  ],
  "outcomes": [
    {
      "action": "folder_pool",
      "action_param": "{{ site_id }}"
    }
  ],
  "last_match": false,
  "enabled": true,
  "sort_field": 10
}
```

The only thing special here, is the Condition. You have to set the __match_type__ to either tag or hostname, and then fill only the needed host or tag condition attributes, but ignore the other ones. 



## Background
The function needs the JSON Structure of the Rule you want created. 
The Simple way to get this, his to create one rule for example and export this rule using the Checkbox and the Export Button. If you open the file then in a text editor,
you will find a structure like this:

``` JSON
{"_id": {"$oid": "69830885190e633552ec9ef4"}, "name": "Move to Pool cmk", "documentation": "", "condition_typ": "all", "conditions": [{"match_type": "tag", "hostname_match": "equal", "hostname": "", "hostname_match_negate": false, "tag_match": "equal", "tag": "attribte_x", "tag_match_negate": false, "value_match": "equal", "value": "true", "value_match_negate": false}], "outcomes": [{"action": "folder_pool", "action_param": "cmk"}], "last_match": false, "enabled": true, "sort_field": 10}
```

Just remove the ```"_id": {"$oid": "69830885190e633552ec9ef4"}, ``` _id part and you are good to go. You may want to use a Json Styler to copy that, then as the Rule Body, into the Syncer configuration. 

Now replace using Jinja all necessary settings. Always make sure that the name field end up as unique because this is how the Syncer will identify if the rule already exists.

The Object Filter is needed that you can limit on which Hosts or Object you base the Rule Creation on. If you import your Data, just set the Type in the Account Settings.