# YML

The Syncer can import data directly from YML files. Due to their structure, you need some configuration to do. Here is the file example:

```
all:
    vars:
      checkmk_server_url: "http://localhost:5000"
      checkmk_site: "local"

123-07:
    vars:
      basisservice: local_test1
    host:
       - test_host1
       - test_host2
234-02:
    vars:
      basisservice: local_test2
    host:
       -  test_host3
       -  test_host4
456-01:
    vars:
      basisservice: local_test3
    host:
       -  test_host5
       -  test_host6
```

As you see, there are multiple sections where you have a list of hosts and variables.
These variables we want to add to every host of the following list.

This can be set in the account settings.
Here are the needed values to configure that example:

- **name_of_host_key**: `host`
- **name_of_variable_key**: `vars`

With this config, the test_host1 would get 'basisservice':`local_test1` as well as host test_host2.2
