# Site Pools

Site Pools distribute hosts automatically across a set of Checkmk monitoring sites — useful when a location is split across several remote sites for load reasons and you want the hosts spread evenly, without mapping each host to a site by hand.

Go to: _Modules → Checkmk → Pools → Site Pools_

## How It Works

A Site Pool is a named group of Checkmk **site ids**. When a host matches a Site Pool rule, the Syncer places it on the site of that pool with the **fewest hosts** (least-loaded). The assignment is **sticky**: once a host is on a site it keeps it on later syncs, so hosts do not move around between sites. When a host no longer matches the pool rule, its seat is freed automatically.

The site is written to the host's `site` attribute in Checkmk — the same attribute the **Monitored on Site** action sets, just picked automatically and balanced across the pool.

## Configuration

Create a Site Pool entry with:

- **Name** — used to reference the pool in export rules
- **Member Sites** — the Checkmk site ids that make up the pool (e.g. `berlin_1`, `berlin_2`, `berlin_3`). Import your sites first (`Import Sites`) so you know the exact ids.
- **Enabled** — only enabled pools hand out sites

The *hosts taken* counter next to each member site is maintained by the Syncer and is read-only.

## Using a Pool in Export Rules

In an export rule, use the **Site Pool** action and reference the pool by name:

```text
berlin
```

The action parameter supports Jinja, so you can build the pool name from host attributes (e.g. `{{location}}`). When you pick the action, the rule form suggests the pools you have already defined as one-click chips — or warns you when none exist yet.

!!! note
    Make sure a host matches only one Site Pool rule. Use the **Last Match** option to prevent unintended stacking with other site assignments.

## Sync Command

The seat counters are kept up to date on every export. To recount them from the current host assignments without running a full export (for example after manual changes):

```bash
./cmdbsyncer checkmk sync_sitepools
```

This also runs as the cron job _Checkmk: Sync Site Pools_.

## Reset the Assignments

Because the assignment is sticky, hosts stay on their site even after you changed the member sites of a pool or the rules that assign it. To throw the whole distribution away and let the next export calculate it from scratch:

```bash
./cmdbsyncer checkmk reset_sitepools
```

This clears the site of every host, resets the seat counters and drops the cached rule results. The next export spreads all hosts across the pools again — which means hosts can move to a different site, so plan it like any other site change.

To redistribute only a few hosts, select them in the host list and use the action _Redistribute Site Pool_.

## Site Pools vs. Folder Pools

Both spread hosts for load balancing, but on different axes:

- **[Folder Pools](folder_pools.md)** distribute hosts across Checkmk **folders** (by seat count), which you then link to sites in Checkmk.
- **Site Pools** distribute hosts directly across Checkmk **sites** (least-loaded), independent of the folder a host lands in.

Pick Site Pools when you want to balance the site attribute itself and keep your folder structure driven by other rules.
