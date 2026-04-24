# Scheduled Backups

Requires the [Enterprise Edition](index.md).

## What it does

Encrypted, rotated `mongodump` backups pushed on a schedule to any
S3-compatible object storage:

- **AWS S3**
- **Google Cloud Storage** (via S3-compat interop)
- **Azure Blob** (via S3-compat endpoint)
- **MinIO** / **Ceph Object Gateway**
- **Backblaze B2**, **Wasabi**, **DigitalOcean Spaces**

Pipeline:

```
mongodump --archive  →  gzip  →  [gpg --encrypt]  →  S3 PutObject
```

Everything streams — a 10 GB dump never lands on disk. Multi-part
uploads are handled by boto3. Retention is enforced after each
successful upload (old objects beyond `retention_days` are deleted).

## Setup

1. Install the optional dependency:
    ```bash
    pip install 'cmdbsyncer-enterprise[backup]'
    ```
2. Make sure `mongodump` (and `mongorestore` for restores, and `gpg`
   if you enable encryption) are on PATH of the syncer OS user.
3. Create a Syncer Account for the S3 destination:

    | Field         | Example                                                      |
    | ------------- | ------------------------------------------------------------ |
    | name          | `s3-backups`                                                 |
    | address       | *(blank for AWS; e.g. `https://s3.eu-central-003.backblazeb2.com` for B2)* |
    | username      | `<access-key-id>` *(blank to use the default AWS credential chain / IAM role)* |
    | password      | `<secret-access-key>`                                        |
    | custom_fields | `region: eu-central-1`                                       |

4. Under **Backups → Configs → Create**, fill in:

    | Field          | Example                                             |
    | -------------- | --------------------------------------------------- |
    | name           | `prod-daily`                                        |
    | bucket         | `cmdbsyncer-backups`                                |
    | prefix         | `prod/`                                             |
    | account        | `s3-backups`                                        |
    | s3_sse         | `AES256` *(optional server-side encryption header)* |
    | compression    | `gzip`                                              |
    | encryption     | `gpg`                                               |
    | gpg_recipient  | `ops-backups@example.com`                           |
    | retention_days | `30`                                                |

5. Test it: select the config in the list, **Run backup now** bulk
   action. Watch the *Backups → History* view for the result.

## Scheduling

The feature registers a new cronjob task named **`enterprise-backup_run`**.
Wire it into a normal CronGroup:

1. Create an OSS *Account* of type `cmdb` whose **name matches the
   BackupConfig name** (e.g. `prod-daily`). The name is how the
   cron task picks the right config.
2. Create a CronGroup (e.g. *Daily Backup 03:00*):
    - interval: `daily`
    - timerange_from / timerange_to: pick the off-hours window
    - Tasks:
        - command: `enterprise-backup_run`
        - account: the account you just created

Now the backup runs on the chosen schedule, obeys the existing
cron retries / `continue_on_error` flag, writes cron stats like
any other group, and feeds the [Prometheus metrics](prometheus_metrics.md)
and [Audit Log](audit_log.md).

## Encryption

- **None** — relies on the object storage's at-rest encryption
  (AWS SSE, GCS CMEK, Azure). Simplest; no key management needed.
- **GPG** — the archive is wrapped for a recipient public key in
  the syncer OS user's keyring. Only holders of the private key
  can restore.

Manage the keyring with `gpg --import` as the syncer user. In
containers, mount `~/.gnupg` as a secret / volume.

## Restore

Restore-path mirrors the backup pipeline:

```
S3 GetObject  →  [gpg --decrypt]  →  gunzip  →  mongorestore --archive --drop
```

From the CLI:

```bash
./cmdbsyncer enterprise backup list prod-daily
./cmdbsyncer enterprise backup restore prod-daily \
    prod/prod-daily/20260420T030000Z.gz.gpg
```

!!! warning
    `mongorestore --drop` wipes each collection before restoring it.
    Always restore to a scratch / staging database first (change
    `MONGODB_HOST` in `local_config.py` to a non-production URI),
    verify the restore, then cut over.

## Retention

After each successful upload the runner calls `list_objects_v2`
with the config's prefix and deletes anything older than
`retention_days`. Set to `0` to keep forever.

Deletions are batched (1000 per call) and show up in the audit
log (`backup.succeeded` metadata → `pruned`).

## Observability

- **Audit Log**: `backup.succeeded` / `backup.failed` with size,
  duration, and object key.
- **Notifications**: same events route into the notifications
  dispatcher, so you can wire up Slack alerts on failure or a
  digest channel on success. Dedup key is `backup:<name>:success`
  / `backup:<name>:failure`.
- **Prometheus Metrics**: the *CronGroup metrics* already cover
  backup runs since the backup runs **as** a cron group. Watch
  `cmdbsyncer_cron_group_last_success_timestamp_seconds{group="Daily Backup"}`
  and alert on age.
- **History view**: *Backups → History* lists every attempt
  (running / success / failure) with size, duration, S3 key and
  error message. Read-only, CSV-exportable.

## Multi-destination

Create multiple `BackupConfig` rows — e.g. daily to AWS S3, weekly
to Backblaze B2 for geo-redundancy. Each one runs on its own
CronGroup. Retention is per-config.

## Restore into a clean install

When rebuilding a syncer from backups:

1. Install CMDBsyncer + Enterprise package as usual.
2. Place `local_config.py` and `license.jwt` from the source
   install (or issue a fresh license).
3. Run `cmdbsyncer enterprise backup restore …` pointing at the
   latest archive.
4. Restart the app and the cron runner.

The restored database contains *everything* — accounts, rules,
users, cron schedules, audit history, secret bindings. No manual
re-entry needed.
