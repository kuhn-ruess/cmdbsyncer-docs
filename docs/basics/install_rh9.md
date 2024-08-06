The most convenient installation of the Syncer is using Docker. There, all Dependencies can simply be satisfied. The biggest problem right now is manually installing the Python Requirements, if the Server is not connected to the Internet, and there is no local Mirror for pip.
Second one is installing the MongoDB Server. For that, an extra Repository needs to be added.

This Guide is based on a Documentation I got from a Consumer. And the plan is to adapt it to make it prefect. I would appreciate your help here.


## Installation Step by Step

### Repos

- subscription-manager repos --enable "codeready-builder-for-rhel-9-$(arch)-rpms"
- dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm
- Mongo DB Repo:
```
EPO_PATH="/etc/yum.repos.d/mongodb-org-7.0.repo"
echo
"[mongodb-org-7.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/9/mongodb-org/7.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://pgp.mongodb.com/server-7.0.asc"
>
$REPO_PATH
```

### Package Installations
dnf install
- uwsgi
- git
- httpd
- mongodb-org
- gcc
- uwsgi-plugin-python3.x86_64
- python-devel







