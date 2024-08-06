# Manage Checkmk Setup Rules

Out of the box, it's possible in Checkmk to create Rules with not much effort. This applies to Threshold Rules and also to for Rules which activate Active Checks, for example. But as soon every Check needs a custom Parameter, it gets harder to set up.

The CMDB Syncer can help here in two Ways. He can add custom Attributes to your Hosts, which you then can use in some of the rules. This is described [here](cmk_attributes.md)

As alternative, you can use this Feature of Syncer, to create a bigger bunch of rules. And the best here, the Syncer also deletes the rules again, if not needed.

## Configuration Options
**Modules → Checkmk →Create Checkmk Setup Rules**<br>


| Option                  | Description                                                          |
| ----------------------- | -------------------------------------------------------------------- |
| Ruleset                 | Checkmk's Ruleset ID                                                 |
| Folder                  | Folder in Checkmk (Jinja Support)                                    |
| Folder Index            | Index of Rule in Folder                                              |
| Comment                 | Rules Comment                                                        |
| Value Template          | Jinja for the Rules Value (check in CMK)                             |
| Conditon Label Template | Syntax: label:value, you can use Jinja. {{HOSTNAME}} also available  |
| Condition Host          | Comma seperated List of Hosts, Jiunja Support including {{HOSTNAME}} |


# Full Examples

- [Manage Contact Groups](recipe_contact_groups.md).  Check this Example to see how the Feature can be setup.


