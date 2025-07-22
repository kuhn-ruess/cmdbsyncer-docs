
# YML Account Settings


| Field                    | Description                                                                                                                                               |
| :----------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `auth_type`              | Basic or digest auth with Username/ Password                                                                                                              |
| `cert`                   | HTTP Authentication via Certificate instead of user/password (set auth_type to false then)                                                                |
| `verify_cert`            | Enable/ Disable Certificate Verification for the HTTP Request                                                                                             |
| `request_headers`        | Custom Request Header                                                                                                                                     |
| `name_of_hosts_key`       | In which Variable can we find the List of Hosts                                                                                                           |
| `name_of_variables_key`  | In which Variable can we find the list of Variables, which you added to the same group of hosts                                                           |
| `path`                   | Path to the YML is provided als local file instead from a http request.                                                                                   |
