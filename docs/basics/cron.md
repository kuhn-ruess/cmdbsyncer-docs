# Cronjobs

The Syncer manages all its automation cronjobs internally. You define which modules to run, in what order, and for which accounts — all from the UI.

## Cronjob Groups

Go to: _Cronjobs → Cronjob Groups_

A Cronjob Group defines:

- An **interval** — how often the group should run
- A **time range** — the window during which the group is allowed to run
- An ordered list of **jobs** to execute

Jobs inside a group run sequentially. If any job fails, the entire group stops. This is intentional — for example, you do not want hosts to be deleted from Checkmk if the import step failed beforehand.

## State Table

Go to: _Cronjobs → State Table_

The State Table keeps one entry per group, showing:

- When the group will run next
- The result of the last run
- Any error messages

To force a group to run immediately or to reset its state, delete or edit its State Table entry.

## Running the Scheduler

The Syncer does not have a built-in scheduler daemon. Instead, call the run command periodically from your system cron — every 5 to 10 minutes is typical:

```bash
./cmdbsyncer cron run_jobs
```

**Full example with environment activation:**

```bash
*/5 * * * * cd /opt/cmdbsyncer && source ./venv/bin/activate && ./cmdbsyncer cron run_jobs
```

**PyPI install** (the `cmdbsyncer` binary lives inside the venv created by [`pip install cmdbsyncer`](../installation/setup_pip.md); `cd` into the deployment directory so `local_config.py` is picked up):

```bash
*/5 * * * * cd /opt/cmdbsyncer && /opt/cmdbsyncer/venv/bin/cmdbsyncer cron run_jobs
```

If running from a different cwd is unavoidable (e.g. a system cron without `cd`), point the binary at the deployment directory explicitly:

```bash
*/5 * * * * CMDBSYNCER_CONFIG_DIR=/opt/cmdbsyncer /opt/cmdbsyncer/venv/bin/cmdbsyncer cron run_jobs
```

**Docker:**

```bash
*/5 * * * * docker exec CONTAINER_ID /srv/cmdbsyncer cron run_jobs
```

**Docker Compose:**

```bash
*/5 * * * * docker compose -f /opt/cmdbsyncer/docker-compose.yml exec -T cmdbsyncer /srv/cmdbsyncer cron run_jobs
```
