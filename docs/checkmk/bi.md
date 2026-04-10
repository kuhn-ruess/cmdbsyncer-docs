# Business Intelligence

Checkmk's BI feature can be fully automated using the Syncer. The recommended workflow is to create one example aggregation or rule in Checkmk, fetch its JSON structure via the API, paste it as a template in the Syncer, and replace the variable parts with Jinja placeholders.

Go to: _Modules → Checkmk → Manage Business Intelligence_

## BI Aggregations

In the Checkmk interactive API (Swagger), look up:

`GET /objects/bi_aggregation/{aggregation_id}`

Example response:

```json
{
  "pack_id": "default",
  "id": "default_aggregation",
  "comment": "",
  "customer": null,
  "groups": {
    "names": ["Hosts"],
    "paths": []
  },
  "node": {
    "search": {
      "type": "host_search",
      "conditions": {
        "host_folder": "",
        "host_label_groups": [],
        "host_tags": {"tcp": "tcp"},
        "host_choice": {"type": "all_hosts"}
      },
      "refer_to": {"type": "host"}
    },
    "action": {
      "type": "call_a_rule",
      "rule_id": "host",
      "params": {"arguments": ["$HOSTNAME$"]}
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

Paste this JSON as the rule template and replace the relevant parts with Jinja placeholders using host attributes.

## BI Rules

In the Checkmk interactive API, look up:

`GET /objects/bi_rule/{rule_id}`

Example response:

```json
{
  "pack_id": "default",
  "id": "filesystem",
  "nodes": [
    {
      "search": {"type": "empty"},
      "action": {
        "type": "state_of_service",
        "host_regex": "$HOSTNAME$",
        "service_regex": "fs_$FS$$"
      }
    }
  ],
  "params": {"arguments": ["HOSTNAME", "FS"]},
  "node_visualization": {"type": "none", "style_config": {}},
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
  "computation_options": {"disabled": false}
}
```

Add this to the rule template and replace the variable parts with Jinja.

## Command Line

```bash
./cmdbsyncer checkmk export_bi_aggregations ACCOUNTNAME
./cmdbsyncer checkmk export_bi_rules ACCOUNTNAME
```
