# DCD Rules
Starting with Checkmk 2.3, you can export DCD Rules to Checkmk. But compared to the Other Checkmk API Endpoints, the DCD Endpoint is still a bit limited. So the export in this Case is not a Sync as in other Modules, but can Create and Delete Rules.


Go to: **Modules →Checkmk →Manage DCD Rules**

The Rules work the same way as the other Syncer Rules do. You can create DCD Rules, with the Outcomes, and use Jinja Template Power in almost every Field.

The Options 1 to 1 reflect the options, like you would set up a DCD Rule directly in Checkmk


## Command Line
To Export the DCD Rules using the CLI, use the following Command:

**./cmdbsyncer checkmk export_dcd_rules ACCOUT**

