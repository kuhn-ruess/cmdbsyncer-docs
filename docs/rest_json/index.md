# Rest and Json

The Syncer allows you to directly import Json Files or Simple Rest APIs, which return plain Json and don't have special Authentication.


## Rest API
Everything is configured using an [Account](/basics/account/). The Following Options are available:

| Option             | Description                                                     |
| ------------------ | --------------------------------------------------------------- |
| `auth_type`        | Empty if you want a Header based auth, else `Basic` or `Digest` |
| `cert`             | Path to a Certificate for Certificat Based auth                 |
| `request_headers`  | Send Custom Headers like for Auth or Content Type               |
| `data_key`         | Empty or key where the Data will be found.                      |
| `hostname_field`   | In which field can the Hostname be found                        |
| `rewrite_hostname` | Jinja if you want to rewrite the hostname                       |



## JSON File
Like for Rest API, everthing is configured in an Account.
Here, you just need to set the Path to the File. 
Fields like hostname_field are described above in the description of Rest API

## When Using the  data_key
The data_key can be confusing. Here two examples to see what it's for.

In this Example, data_key needs to be 'results'
```json
{'results': [{data},{data}]}
```

In this case, the data key needs to be empty
``` json
[{data},{data}]
```