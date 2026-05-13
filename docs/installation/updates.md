# Update CMDBsyncer

## Update Process

!!! tip "Which branch should I pull?"
    For production, stay on the **`lts/3.12`** branch. It receives only security fixes and general bugfixes backported from `main` — no new features — so `git pull` on `lts/3.12` only moves forward when a reviewed maintenance release is available. Avoid pulling `main` directly, which contains unreleased, in-development changes and new features. Full policy: [RELEASE.md on GitHub](https://github.com/kuhn-ruess/cmdbsyncer/blob/main/RELEASE.md).

Pull the latest LTS code from git:

```bash
cd /opt/cmdbsyncer
git checkout lts/3.12     # only needed the first time
git pull
```

If you want to pin to a specific release instead of tracking `lts/3.12`, check out the tag:

```bash
git fetch --tags
git checkout v3.12.13     # replace with the desired release tag
```

If you are using Docker, rebuild your image and restart the container after pulling.

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
source venv/bin/activate
pip install -r requirements.txt
```

Docker users will not encounter this — all dependencies are installed automatically when rebuilding the image.
