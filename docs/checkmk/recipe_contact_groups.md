# Manage Contact Groups

This guide shows how to create Checkmk Contact Groups from host attributes and set up the corresponding assignment rules — all managed by the Syncer.

## Overview

Three things are needed:

1. Hosts with the attributes that should become group names
2. Group creation rules (see [Groups Management](groups_management.md))
3. Assignment rules (see [Manage Checkmk Setup Rules](rules_management.md))

## Step 1: The Attributes

Import the attributes you want to use as group names. In this example, the hosts have `os` and `location` attributes.

![Host attributes in the Syncer](img/recipe_cg_1.png)

## Step 2: Create the Group Rule

Go to: _Modules → Checkmk → Manage Host-/Contact-/Service-Groups_

Create a rule for the `location` attribute:

- **Group Name:** Contact Groups
- **Foreach Type:** Foreach Attribute
- **Foreach:** `location`

Optionally, use Rewrite to control the group ID and title:

- **Rewrite:** `cg_{{name|lower}}`
- **Rewrite Title:** `{{name|capitalize}}`

![Group creation rule](img/recipe_cg_2.png)

After exporting, the groups appear in Checkmk:

![Groups in Checkmk](img/recipe_cg_3.png)

![Where to find the groups](img/recipe_cg_4.png)

!!! tip
    If your values follow a pattern like `contact_1`, `contact_2`, use `contact_*` as the Foreach value to match all values starting with that string.

## Step 3: Find the Ruleset Parameters

To create the assignment rule, you need the Checkmk ruleset ID and value format.

Navigate to the rule in Checkmk to find the ruleset name:

![Ruleset name](img/recipe_cg_5.png)

Then use the Checkmk API to get the value format. Open the API documentation and look up an existing rule of that type:

![API value format step 1](img/recipe_cg_6.png)

![API value format step 2](img/recipe_cg_7.png)

## Step 4: Create the Assignment Rule

Go to: _Modules → Checkmk → Create Checkmk Setup Rules_

Create a rule that assigns hosts to the contact group. Use `{{ location }}` to reference the host attribute as the condition label value:

![Assignment rule configuration](img/recipe_cg_8.png)

Repeat for the `os` attribute.

## Step 5: Export and Verify

Run the export and check the result in Checkmk:

![Export command](img/recipe_cg_9.png)

![Result in Checkmk](img/recipe_cg_10.png)

Activate the changes in Checkmk — done.
