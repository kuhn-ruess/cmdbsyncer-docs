# Caching
Especially if you have several thousands of hosts, it makes a difference if a process per host takes 1 second or just a few milliseconds. So to speed Syncer processes up, a cache is used.
The cache will automatically be cleared for a host if the import updates its labels. If you change rules, you need to delete this cache.
For that, you will find a "Commit Changes" link in the navigation top right.

From the command line, you can call _./cmdbsyncer sys delete_cache_

For normal operations, everything will be fine. Processes like Export will just take a bit longer the first time, while the cache is being built. But in some cases, that is not enough. For example, if the API endpoints for Ansible take too long, they will run into a timeout. In these cases, you find an option to manually build this cache on the command line.
Example for Ansible: _./cmdbsyncer ansible update_cache_
In a real-world example where this feature was built for, the time went down from 171 seconds to just 2 seconds for the whole process.

