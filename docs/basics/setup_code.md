# Installation from Code

The most common way to use the application without Docker is direct from Code. This is easy if the server has an Internet Connections. Updates are easy as git pull then.


## Steps
If you not using docker, that are the steps to make the syncer run:
``` mermaid
graph LR

A[Download Repo] --> B[Create Python Environment] --> C[Install Python Requirements] --> D[Setup Mongodb] --> E[Setup Apache with UWsgi]
```

## Download Repo
You need to check out the Code directly from GitHub.  [Go to the Repo](https://github.com/kuhn-ruess/cmdbsyncer), and copy the Clone URL to example /var/www. In all examples, this Path is used.

[Repo](https://github.com/kuhn-ruess/cmdbsyncer)

![](img/checkout_github.png)

Example:
```
cd /var/www
git clone https://github.com/kuhn-ruess/cmdbsyncer
cd cmdbsyncer
```


## Install Pythons Virtual Environment.
The Syncer Need some Python Libraries. But these we don't want to install into your system.
Instead, we create a virtual environment. Make sure that you have at least python3.10. The Python Interpreter on your system may have a different Name.

Always Make sure you are in /var/www/cmdbsyncer

`python3.11 -m venv ENV`

This Environment needs to be loaded from now on, every time something is done with the syncer, also for every Cronjob which you will run.

`source ENV/bin/activate`

To this Environment, you install the Python Libraries. This is done with just one command:

`pip install -r requirements.txt`

In Case, you plan to use Ansible, also import the Ansible requirements:

`pip install -r requirements-ansible.txt`


Extra Database stuff you find in requirements-extras.txt

## Install Mongodb Server
The Syncer needs the Mongodb. All you need to do is to install it, with your Packet Manager. Then you are ready to go.


## Configure Defaults
When the Database is running, run 

```
./cmdbsyncer sys self_configure
```

This Should also run after you Update the Syncer
## The Web Interface

To take a brief look, you can start the development Server:

`flask run --host 0.0.0.0 --port 8080`

But then you should Setup UWSGI. There is an Example with [UWSGI and Apache](uwsgi_apache.md), but it's even easier with NGINX. Or go with this simpler one, using [mod_wsgi and Apache](install_wsgi.md)


## First Steps

Make the [First Steps](first_steps.md)
