# Folder Pools

Folder Pools distribute hosts automatically across a set of predefined folders — useful when you want to spread hosts across multiple Checkmk remote sites or when you need balanced folder sizes.

Go to: _Modules → Checkmk → Folder Pools_

## How It Works

Each Folder Pool has a **seat count** that defines the maximum number of hosts the folder can hold. The Syncer assigns incoming hosts to folders that still have available seats. When a host is removed or its pool assignment no longer matches, its seat is freed automatically.

The Syncer creates the folders in Checkmk automatically. Link them to your remote sites in Checkmk to distribute monitoring across sites.

## Configuration

Create a Folder Pool entry with:

- **Name** — used to reference the pool in export rules
- **Folder Name** — the Checkmk folder path
- **Seat Count** — maximum number of hosts in this folder
- **Assigned Site ID** — (optional) the Checkmk site ID to associate with this pool

## Using a Pool in Export Rules

In an export rule, use the **Pool Folder** action and reference the pool by name. If you leave the action parameter empty, the Syncer queries from all available pools. To restrict assignment to specific pools, provide a comma-separated list of pool names:

```text
pool_site_a,pool_site_b
```

This ensures a host is only placed in one of the listed pools, ignoring any others.

!!! note
    Folder Pool rules stack with other folder rules. Use the **Last Match** option on the pool rule to prevent unintended stacking with other folder assignments.

## Sync Command

To recount the used seats from the current host assignments without running a full export:

```bash
./cmdbsyncer checkmk sync_folderpools
```

## Reset the Assignments

A host keeps its pool folder until it no longer matches a Folder Pool rule, so changed pools or changed rules never move a host that is already assigned. The host debug page points this out whenever a host holds such an assignment. To throw the whole distribution away and let the next export calculate it from scratch:

```bash
./cmdbsyncer checkmk reset_folderpools
```

This clears the folder of every host, resets the seat counters and drops the cached rule results. The next export distributes all hosts again — hosts can end up in a different folder, so plan it like any other folder move. The older `./cmdbsyncer sys reset_folder_pools` does the same, but asks for confirmation first.

## Auto-creating Pools with Autocreate Rules

For environments where the set of sites changes frequently, you can use the [Autocreate Rules](../basics/auto_rules.md) feature to generate Folder Pool entries automatically based on imported site objects.
