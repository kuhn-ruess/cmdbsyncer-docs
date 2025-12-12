# How to Setup for Production using UWSGI and Apache

!!! warning
    This Documentation is not working with RedHat 9. Also a bit outdated because you can use [apache mod_wsgi](install_wsgi.md) without the need to setup UWSGI.
    But if you don't use apache, and want to go with uWSGI here you go.

## Requirements
- Python Version >= 3.11 must be installed
- MongoDB Server must be Installed
- Apache Mod UWSGI must be Installed and activated
- uWSGI and the python3 Plugin of uWSGI must be installed in version at least 3.9

## First Steps:
[Checkout](setup_code.md) the Code into /var/www/cmdbsyncer.
We will define a Path in Apache which will be proxy to the uWSGI daemon. For this Example: /cmdbsyncer
Update/ Create a local_config and adjust the BASE_PREFIX to that path. For example, https://checkmk-server.de/cmdbsyncer would be 'BASE_PREFIX': '/cmdbsyncer/'. You find [here](lcl_config.md) how to do that.

## Setup uWSGI
In ./deploy_configs you will find the example_apache/ Folder. Use the uwsgi-config.ini and copy it to /etc/uwsgi.d/ or depending on your Linux Distribution, to the Folder for the config files. You should rename the file like cmdbsyncer.ini
If you used different Paths, you need to update them the ini file.

Please note that in the uwsgi-config.py you find a plugin = python3.
This has maybe a different Name on your OS. You could need for example python311

Restart UWSGI with service uwsgi restart.

## Setup Apache
Also in the example_apache folder, there is an apache_config.conf. Copy it, depending on your Linux Distribution, to /etc/apache2/conf.d, /etc/httpd/conf.d or so on. 
In this file, you can change the Path for the Application. Make sure to adjust the BASE_PREFIX as described before in case of changes.
Also rename it as you need and Restart Apache.

## Final
If you left all examples as they are, it would be http[s]://servername/cmdbsyncer/admin where you can access the Frontend


# Known Problems

## uWSGI Python Version to old on Redhat or Centos
For Redhat, best use the solution descripted [here](install_wsgi.md), but if you want to go the way do this:

-   yum -y install gcc libcap-devel libuuid-devel make openssl-devel python311-devel pcre-devel uwsgi-devel
-   if needed: yum install rpm-config (if redhat-hardened missing)
-   cd /usr/src/uwsgi/NUMMER
-   PYTHON=python3.11 /usr/sbin/uwsgi --build-plugin "plugins/python python311"
-   cp plugin to /usr/lib64/uwsgi
  

## Filesocket no right for Apache:

-  Add Apache user to uwsgi group
-   Disable SELinux


