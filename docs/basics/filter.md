# Filter Hosts and Whitelist

Every module has a filter section. Here you can blacklist or whitelist the hosts you want to export, and do the same for the labels/attributes you want to export along with them.

The Syncer may have hundreds of attributes for a host. Normally, you don't want to export them all, for example as labels in Checkmk. Therefore, you need to whitelist them here.

## Account Filter Negation

Since Version 3.12.2, account filters can be negated by prefixing the value with `!`. This allows you to exclude specific values instead of whitelisting them.