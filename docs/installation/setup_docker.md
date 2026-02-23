# Docker

The Project is not in the Docker Library yet, but you can run it after Checkout the Code.

The Docker Compose File there contains all the needed dependencies.
The Dockerfile you found already in the Main Directory of the repo.

And if you develop with the syncer, you may want to look into the ./helper command,
which provides you an environment with live refresh after code changes.

## Docker behind proxy
If you plan to use Docker behind a proxy, then you have two possibilities to get it running.

### Modify docker-compose.local.yml
Currently, we do not add proxy settings and provide following setup:
```dockerfile
api:
    build:
      dockerfile: Dockerfile.local
    environment:
      config: compose
      FLASK_DEBUG: 1
    ports:
      - 5003:5003
    volumes:
      - ./:/srv
```

You can add your proxy configuration like this:
```dockerfile
  api:
    build:
      dockerfile: Dockerfile.local
    args:
      HTTPS_PROXY: PROTOCOL://SERVERNAME:PORT
    environment:
      config: compose
      FLASK_DEBUG: 1
    ports:
      - 5003:5003
    volumes:
      - ./:/srv
```
### Add proxy to user environment
If you want to add the proxy for the user, which is used for Docker, then you can add it directly to his environment. Please use `~/.docker/config.json`:
```json
{
  "proxies": {
    "default": {
      "httpProxy": "PROTOCOL://SERVERNAME:PORT",
      "httpsProxy": "PROTOCOL://SERVERNAME:PORT",
      "noProxy": "EXCLUDE1,EXCLUDE2,127.0.0.0/8"
    }
  }
}
```

## Things to Consider

### Config
You need to have a local_config.py. This file is created by __./cmdbsyncer sys self_configure__ (which runs with every update). Make sure this file is not inside you container. It contains keys and if you loose it, you loose all stored passwords.

### MongoDB
The project always needs his MongoDB, like the docker-compose.yml also defines. 


### Access to the container
Most things can be done in the web interface. But for debugging the CLI is helpfull.

### Cron Jobs
The Syncer Needs Cron Jobs. These need to be triggered using the docker exec command. If you're using the provided Dockerfile, this will happen automaticly.

### External Files
If you want to import external Files into the Syncer, make sure to define a volume where you can place it.
Configure this Path then for the Fileadmin in order to access these files in the GUI.


### Resources
The Syncer does not need many Resources, mainly Disk Space. And at least two CPUs.
But if you have many rules, you will benefit from more CPUs since the Syncer uses for Calculations Multiprocessing all available cores. 

### UWSGI/ NGINX
Inside the Container you will find a Python Application. Normally, they are accessed using UWSGI. And many Containers then also contain an NGINX in Front of this UWSGI.  The CMDB Syncer Container has no Nginx, since it would be redundant. Most likely, the Reverse proxy in Front of the Container will be a Nginx anyway. And so, your Reverse Proxy can speak directly UWSGI with the Container on the exposed port.

