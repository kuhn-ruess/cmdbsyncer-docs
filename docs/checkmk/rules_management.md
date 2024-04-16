# Manage Checkmk Rules

Out of the box, it's possible in Checkmk to create Rules with not much effort. This applies to Threshold Rules and also to for Rules which activate Active Checks, for example. But as soon every Check needs a custom Parameter, it gets harder to set up.

The CMDB Syncer can help here in two Ways. He can add custom Attributes to your Hosts, which you then can use in some of the rules. This is described [here](cmk_attributes.md)

As alternative, you can use this Feature of Syncer, to create a bigger bunch of rules. And the best here, the Syncer also deletes the rules again, if not needed.

## Configuration Options
**Rules → Checkmk → CMK Rules Management**<br>
Below you find the Description for the Parameters found in the Admin Panel:












# Recipes
- [Manage Contact Groups](recipe_contact_groups.md). Example of course works for all kind of groups.
