# Bake and Sign Agents

In some cases, you may want to automate the Bake and Sign of the Checkmk Agents in the Bakery. This could be after you crated them via the RestAPI, or also when they are discovered via the Network scan.

As usual, you can use the Command Line Option to do that:

`./cmdbsyncer checkmk bake_and_sign_agents ACCOUNTNAME`

or you just configure it as job inside the cron manger.

## Requirements
You need to configure the Agent Signing ID and Password inside the Account settings of the CMDBsyncer. The Key ID you find on the Page with Signing keys directlyin Checkmk.

In the Account, you need to set the Fieldnames like this:

 - bakery_key_id
 - bakery_passphrase

If these Keys do not exist already as custom_fields, just create them. With Syncer Version 3.9 just save the Account once, to automatically create them.

