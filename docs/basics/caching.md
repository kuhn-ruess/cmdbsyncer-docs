# Caching

CMDBsyncer caches the result of rule evaluation per host. This makes a significant difference in large environments — instead of recalculating all rules on every request, the result is read from the cache in milliseconds.

In a real-world example, caching reduced Ansible inventory response time from **171 seconds to 2 seconds**.

## How the Cache Works

The cache is stored per host in the database. Each plugin or operation that evaluates rules writes its result into a named cache slot (e.g. `ansible`, `checkmk`).

The cache is **automatically invalidated** for a host whenever its attributes are updated by an import. You only need to clear it manually when you change rules.

## Clearing the Cache After Rule Changes

When you modify rules, the cached outcomes for existing hosts are stale. Clear the cache in one of two ways:

**Via the web interface:**  
Click **Commit Changes** in the top-right navigation bar.

**Via the CLI:**

```bash
./cmdbsyncer sys delete_cache
```

To clear only the cache for a specific plugin (e.g. after changing Checkmk rules only):

```bash
./cmdbsyncer sys delete_cache checkmk
```

The optional argument filters by cache key prefix — only entries whose key starts with the given name are removed.

## Pre-Building the Cache

On the first run after a cache clear, exports take slightly longer while the cache is rebuilt on the fly. For most operations this is acceptable, but for time-sensitive endpoints — like the Ansible dynamic inventory, which has a strict HTTP timeout — you should pre-build the cache before it is needed:

```bash
./cmdbsyncer ansible update_cache
```

This processes all hosts upfront and stores the Ansible inventory result in the cache. Subsequent inventory requests return instantly.

The cache build can also be scheduled as a [Cron job](cron.md) — the Ansible plugin registers it automatically as **"Ansible: Build Cache"** in the cronjob list.

## Summary

| Situation                        | Action                                          |
| :------------------------------- | :---------------------------------------------- |
| Import updated host attributes   | Cache cleared automatically                     |
| You changed rules                | Click **Commit Changes** or run `delete_cache`  |
| Ansible inventory times out      | Run `ansible update_cache` before the next call |
| Scheduled cache rebuild          | Add "Ansible: Build Cache" as a cron job        |
