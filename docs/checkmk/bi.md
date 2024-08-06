# Checkmk Business Intelligence

Checkmks BI Feature can fully be automated by these Rules. To Set-up the Config, just create One example in Checkmk, then Fetch it with the API. Place the JSON Response into the Syncer, and there you can replace where needed with Jinja.

Checkout: __Modules →Checkmk →Manage Business Intelligence__ 

## BI Aggregations

In the Interactive API GUI of Checkmk, look for GET /objects/bi_aggregation/{aggregation_id}
An Example would look like:

```json
{
  "pack_id": "default",
  "id": "default_aggregation",
  "comment": "",
  "customer": null,
  "groups": {
    "names": [
      "Hosts"
    ],
    "paths": []
  },
  "node": {
    "search": {
      "type": "host_search",
      "conditions": {
        "host_folder": "",
        "host_label_groups": [],
        "host_tags": {
          "tcp": "tcp"
        },
        "host_choice": {
          "type": "all_hosts"
        }
      },
      "refer_to": {
        "type": "host"
      }
    },
    "action": {
      "type": "call_a_rule",
      "rule_id": "host",
      "params": {
        "arguments": [
          "$HOSTNAME$"
        ]
      }
    }
  },
  "aggregation_visualization": {
    "ignore_rule_styles": false,
    "layout_id": "builtin_default",
    "line_style": "round"
  },
  "computation_options": {
    "disabled": true,
    "use_hard_states": false,
    "escalate_downtimes_as_warn": false,
    "freeze_aggregations": false
  }
}
```
Set this now as Rule Template, and replace needed parts with attributes you have from Hosts or Objects. Full Flexibility of Jinja is Available. 

## BI Rules
In the Interactive GUI, look for GET /objects/bi_rule/{rule_id}

The Example her:
```json
{
  "pack_id": "default",
  "id": "filesystem",
  "nodes": [
    {
      "search": {
        "type": "empty"
      },
      "action": {
        "type": "state_of_service",
        "host_regex": "$HOSTNAME$",
        "service_regex": "fs_$FS$$"
      }
    },
    {
      "search": {
        "type": "empty"
      },
      "action": {
        "type": "state_of_service",
        "host_regex": "$HOSTNAME$",
        "service_regex": "Filesystem$FS$$"
      }
    },
    {
      "search": {
        "type": "empty"
      },
      "action": {
        "type": "state_of_service",
        "host_regex": "$HOSTNAME$",
        "service_regex": "Mount options of $FS$$"
      }
    }
  ],
  "params": {
    "arguments": [
      "HOSTNAME",
      "FS"
    ]
  },
  "node_visualization": {
    "type": "none",
    "style_config": {}
  },
  "properties": {
    "title": "$FS$",
    "comment": "",
    "docu_url": "",
    "icon": "",
    "state_messages": {}
  },
  "aggregation_function": {
    "type": "worst",
    "count": 1,
    "restrict_state": 2
  },
  "computation_options": {
    "disabled": false
  }
}
```

As before, add this to the Rule Template and replace with Jinja.

## Export on Command Line
If you now wan't to export the rules, use

*./cmdbsyner checkmk export_bi_aggregations ACCOUNT*
AND:
*./cmdbsyncer checkmk export_bi_rules ACCOUNT*

