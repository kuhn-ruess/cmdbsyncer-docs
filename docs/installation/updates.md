# Update CMDBsyncer

## Update Process

Pull the latest code from git:

```bash
cd /opt/cmdbsyncer
git pull
```

If you are using Docker, rebuild your image and restart the container.

If you have a UWSGI-based installation, reload UWSGI:

```bash
service uwsgi reload
```

Then run the self-configuration to apply any new config defaults:

```bash
./cmdbsyncer sys self_configure
```

!!! warning "Check for breaking changes first"
    Always review the [Update Notes](../updates/update_notes.md) before updating to check for changes that require manual action.

## Dependency Updates

If the application fails to start after an update, check the UWSGI logs in `/var/log`. A missing or outdated Python module is the most common cause. Update all dependencies with:

```bash
cd /opt/cmdbsyncer
source ENV/bin/activate
pip install -r requirements.txt
```

Docker users will not encounter this — all dependencies are installed automatically when rebuilding the image.
