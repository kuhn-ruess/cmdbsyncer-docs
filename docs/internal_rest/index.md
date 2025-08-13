The cmdbsyncer provides REST API endpoints for various functions. You can explore them using the integrated Swagger GUI when accessing /api/v1.

For authentication, create an account of the type "Internal Rest API". Specify a Username and the password. This combination is sent as a header: `x-login-header: user:password`

## Ansible Endpoints
These endpoints can be used to access the Ansible Inventory of the cmdbsyncer from different servers. You find an example of how it can be used with `ansible-playbook` in the ansible Subfolder.


## Syncer Endpoints
These endpoints are used to monitor syncer operations. The official Checkmk Syncer Monitoring Plugins are using them.


## Objects Endpoints
With the provided `GET`/`POST`/`DELETE` endpoints it's possible to change hosts or objects inside the Syncer, and also to retrieve them. Please note that there is no `PUT` method, since you don't need to check if an object already exists before you update it. The Syncer gets or creates host objects from his database to simplify the operations.