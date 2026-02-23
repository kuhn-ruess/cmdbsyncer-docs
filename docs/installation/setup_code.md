# Installation from Code

The most common way to use the application without Docker is direct from Code. This is easy if the server has an Internet Connections. Updates are easy as git pull then.


## Steps
If you not using docker, that are the steps to make the syncer run:
``` mermaid
graph LR

A[Download Repo] --> B[Create Python Environment] --> C[Install Python Requirements] --> D[Setup Mongodb] --> E[Setup Apache with UWsgi]
```

## Download Repo
You need to check out the Code directly from GitHub.  [Go to the Repo](https://github.com/kuhn-ruess/cmdbsyncer), and copy the Clone URL to example /opt. In all examples, this Path is used.

[Repo](https://github.com/kuhn-ruess/cmdbsyncer)

![](img/checkout_github.png)

Example:
```
cd /opt/
git clone https://github.com/kuhn-ruess/cmdbsyncer
cd cmdbsyncer
```


## Install Pythons Virtual Environment.
!!! HINT
    You can skip this section, if you are planning to use Docker.



The Syncer needs some Python libraries. But these we don't want to install into your system.
Instead, we create a virtual environment. Make sure that you have at least python3.11. The Python interpreter on your system may have a different name.

Always make sure you are in /opt/cmdbsyncer

`python3.11 -m venv ENV`

This environment needs to be loaded from now on, every time something is done with the Syncer, also for every cron job that you will run.

`source ENV/bin/activate`

To this Environment, you install the Python Libraries. This is done with just one command:

`pip install -r requirements.txt`

In Case, you plan to use Ansible, also import the Ansible requirements:

`pip install -r requirements-ansible.txt`


Extra Database stuff you find in requirements-extras.txt

## Install MongoDB Server
!!! HINT
    You can skip this section, if you are planning to use Docker.
The Syncer needs the Mongodb. All you need to do is to install it, with your Packet Manager. Then you are ready to go.


## Configure Defaults
!!! HINT
    Make sure to either be in the docker container, or to have the environment loaded
When the database is running, run 

```
./cmdbsyncer sys self_configure
```

This Should also run after you Update the Syncer
## The Web Interface

To take a brief look, you can start the development server:

`flask run --host 0.0.0.0 --port 8080`

But then you should setup WSGI. See: [mod_wsgi and Apache](install_wsgi.md)

If you are using docker, you can directly access the containers port. 

## First Steps

Make the [First Steps](../basics/first_steps.md)
