# Autocreate Rules

Since version 3.12, the Syncer can automatically create its own rules based on attributes it has discovered. This is useful in dynamic environments where new objects — such as new Checkmk sites — are added regularly, and you want the Syncer to keep its own configuration up to date.

Go to: _Modules → Syncer Rules → Automate Syncer Rule Creation_

## Setup Example

The best way to understand this feature is with a concrete example.

**Scenario:** You have a large number of Checkmk sites. You want to automatically distribute hosts to those sites using Folder Pools. Whenever a new site is added, the Syncer should automatically create the necessary Folder Pool and the matching host assignment rule.

Required steps:

1. Import site information from Checkmk
2. Auto-create a Folder Pool rule for each site
3. Auto-create a host assignment rule for each pool

### Step 1: Import Site Information

Add the command _Checkmk: Import Sites_ to one of your Cronjob Groups. It works with any existing Checkmk account. The import creates one object per configured site, with the labels `site_id` and `alias`. These objects have the type `Cmk Site`, which you can use as an Object Filter later.

### Step 2: Auto-create Folder Pool Rules

Create an Autocreate Rule with:

- **Rule Type:** `CheckmkFolderPool`
- **Object Filter:** `Checkmk Site Object`

**Body:**

```jinja
{
  "name": "Rule for {{ site_id }}",
  "folder_name": "/{{ site_id }}",
  "folder_title": "{{ alias }}",
  "folder_seats": 10,
  "assigned_site_id": "{{ site_id }}",
  "enabled": true
}
```

The `{{ site_id }}` placeholder comes from the site object's labels.

### Step 3: Auto-create Host Assignment Rules

Create another Autocreate Rule with:

- **Rule Type:** `CheckmkRule`
- **Object Filter:** `Checkmk Site Object`

**Body:**

```jinja
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
      "tag": "site_attribute",
      "tag_match_negate": false,
      "value_match": "equal",
      "value": "{{ site_id }}",
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

In conditions, set `match_type` to either `tag` or `hostname`, and fill in only the fields relevant to that type.

## Getting the JSON Structure

The easiest way to get the correct JSON structure for any rule type is to create one example rule manually and then export it using the checkbox and export button in the rules list. Open the exported file in a text editor to find the JSON.

Remove the `_id` field (e.g. `"_id": {"$oid": "..."}`) before using the JSON as a body template. You can use a JSON formatter to make it easier to read.

Then replace the values you want to vary with Jinja placeholders.

!!! important
    The `name` field must result in a unique value per object — the Syncer uses the name to identify whether a rule already exists and needs to be updated, or is new and needs to be created.

## Object Filter

The Object Filter restricts which objects are used as the basis for rule creation. Set the object type in the account settings of the import that provides the source objects. This prevents the Syncer from generating rules for irrelevant objects in the database.
