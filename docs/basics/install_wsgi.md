# Installation with mod_wsgi

The most convenient installation of the Syncer is using Docker. There, all Dependencies can simply be satisfied. The biggest problem right now is manually installing the Python Requirements, if the Server is not connected to the Internet, and there is no local Mirror for pip.
Second one is installing the MongoDB Server. For that, an extra Repository needs to be added.

This Guide is based on a Documentation I got from a Consumer. And the plan is to adapt it to make it prefect. I would appreciate your help here.



## Base Requirements for System
For the Syncer to Run, you need these Dependencies: 

- yum install python3.11
- yum install httpd
- yum install python3.11-mod_wsgi

Also needed is MongoDB, but this is covered later

## Build Requirements to create the Python Environment
The Syncer needs a Python Virutal Environment for his Modules.
To Install that (see default doc) you need the following:

- yum groupinstall "Development Tools"
- yum install httpd-devel  
- yum install python3.11-devel

## Checkout the Repo and create the Environment
Best go to /var/www then [follow this description](setup_code.md)


## Configure Apache
The Default Installation UWSGI is not working on Red Hat. But there is that even better Workaround. It works with the python3-11-mod_wsgi we installed earlier.

Just create the following Config File in /etc/httpd/conf.d/ (May adapt the Vhost Settings if you have Checkmk Installed on the same server)

```
<VirtualHost *>
	ServerName example.com
	WSGIDaemonProcess cmdbsyncer python-home=/var/www/cmdbsyncer/ENV user=apache group=apache threads=5

	WSGIScriptAlias / /var/www/cmdbsyncer/app.wsgi

	<Directory /var/www/cmdbsyncer>
		WSGIProcessGroup cmdbsyncer
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
	</Directory>
</VirtualHost>
```


## Mongodb

Best would be to enable a repo with MongoDB in the Subscription Manger.
But you can also work with the officiall open-source one, described here: 
 [https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-red-hat/](Mongo on Readhat)
    
The File for /etc/ym.repos.d/mongodb.repo:

```
[mongodb-org-7.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/9/mongodb-org/7.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://pgp.mongodb.com/server-7.0.asc
```

Then you can install Mongodb
_yum install -y mongodb-org_


# Final
If you get Access Denied messages in the Apache Log, you need to configure or disable SELINUX. If you configure it, I would be happy to get the info how to do that for this documentation.




