# Checkmk

The Checkmk Module of Syncer overtakes Automation for Functions in Checkmk.
Based on your Hosts and their Attributes, you control how to sync your Hosts to Checkmk, and sort them in automatically created folders.

Furthermore, you can create [Contact-, Host-, Service Groups](groups_management.md) based on Attributes, all types of [rules](rules_management.md) or control the Bake and Sign of Agents or the Activate Changes from your Command line.

See the Recipes Section for more Step by Step docs.



## Labels

When the Syncer takes over, you should no longer set manual labels directly to hosts in Checkmk anymore. If you still need to do that, which is not recommended, you can work with prefixes to solve this.  But better if all direct labels could come from the Syncer. 
Direct Labels means, the ones directly with the Host. Not the ones that are set via Checkmk Rule, or the ones that are discovered or set on folders. These you can still use in any case.

Inside the Syncer you will find many attributes and you can create Custom Attributes or Rewriten them. But as of default, none of them will be exported to Checkmk as a label. To export them, you need to whitelist them in Checkmk -> Filter. The Only exception are labels starting with cmdbsyncer/. These are internal labels for helper functions the syncer uses to optimize, e.g Checkmk rule creation.







