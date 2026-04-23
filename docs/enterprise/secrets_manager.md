# Secrets Manager

Requires the [Enterprise Edition](index.md).

## What it does

By default, every CMDBsyncer **Account** stores its password in the
application database (Fernet-encrypted at rest using `CRYPTOGRAPHY_KEY`).
The Secrets Manager lets you bind an Account to an entry in an external
vault instead. On every sync run the Account fetches its password from
that vault — so your syncer database never holds the authoritative copy.

Typical reasons to enable it:

- Your organisation already has a central secret store (KeePass,
  Vault, LastPass, AWS Secrets Manager) and compliance requires that
  credentials live there, not in the syncer DB.
- You want credential rotation without editing Account records — rotate
  the value in the vault, next sync picks it up.
- You need different access controls for the syncer app vs. for the
  credentials (vault ACLs are separate from CMDBsyncer admin rights).

## Supported vaults

| Provider                  | Store type     | Extra install                                               |
| ------------------------- | -------------- | ----------------------------------------------------------- |
| KeePass `.kdbx` file      | `keepass`      | `pip install 'cmdbsyncer-enterprise[keepass]'`              |
| LastPass                  | `lastpass`     | `lpass` CLI installed on the syncer host and logged in once |
| HashiCorp Vault (KV v1/v2)| `vault`        | `pip install 'cmdbsyncer-enterprise[vault]'`                |
| AWS Secrets Manager       | `aws_secrets`  | `pip install 'cmdbsyncer-enterprise[aws]'`                  |
| Environment variable      | `envvar`       | none                                                        |

To install all Python dependencies at once:

```bash
pip install 'cmdbsyncer-enterprise[secrets-all]'
```

## How it works

Two new sections appear under **Secrets Manager** in the admin menu:

1. **Secret Stores** — one entry per external vault. Global, reusable.
2. **Account Bindings** — per-account link: *"Account X pulls its
   password from this entry in that store."*

When a plugin asks for `account_data['password']`, CMDBsyncer checks
for a binding on the Account. If one exists, the bound provider is
consulted and the fresh value is returned. If no binding exists, the
locally-encrypted password is used — so you can roll out the feature
gradually, one Account at a time.

All plugins (Checkmk, Netbox, Jira, SQL, Ansible, …) automatically
benefit; no plugin-side configuration is needed.

## Setting up a store

### KeePass

1. Copy the `.kdbx` file onto the syncer host. Make sure the syncer's
   OS user can read it.
2. Choose how the master password reaches the syncer:
    - **Keyfile only** — put the keyfile on the host and leave the
      master password empty; set `keyfile_path` on the store.
    - **Env var** — export `KEEPASS_MASTER` before starting the syncer
      (systemd `EnvironmentFile=`, Docker `--env-file`, Kubernetes
      `envFrom: secretRef`) and set `master_password_env=KEEPASS_MASTER`
      on the store.
    - Both together are supported and recommended for production.
3. Create a *Secret Store* with type **KeePass**:

    | Field                 | Example                                     |
    | --------------------- | ------------------------------------------- |
    | name                  | `central-keepass`                           |
    | type                  | `keepass`                                   |
    | kdbx_path             | `/etc/cmdbsyncer/secrets.kdbx`              |
    | keyfile_path          | `/etc/cmdbsyncer/keyfile.key` *(optional)*  |
    | master_password_env   | `KEEPASS_MASTER` *(optional if keyfile set)*|

4. Reference entries by their KeePass path:
   `Root/Infrastructure/checkmk-prod`.

!!! tip "Rotation without restart"
    KeePass files are cached for 5 seconds and keyed on file mtime —
    editing the `.kdbx` is picked up automatically on the next sync.

### LastPass

1. Install the [`lpass` CLI](https://github.com/lastpass/lastpass-cli).
2. As the **syncer OS user** (not as you), run:
    ```bash
    lpass login admin@example.com
    ```
   The CLI caches an encrypted session; the syncer reuses it.
3. Create a *Secret Store* with type **LastPass** and set
   `lastpass_username` to the same address. The store does not hold a
   password.
4. Reference entries by their LastPass entry name or id, e.g.
   `checkmk-prod`. Non-password fields: append `#username` or
   `#<field>`.

!!! warning
    `lpass` sessions expire (default: 60 min idle). For a production
    syncer, increase the agent timeout:
    ```bash
    lpass config set agent.timeout 604800   # 7 days
    ```

### HashiCorp Vault

1. Provision a token with read access to the KV paths you need (AppRole
   is recommended over root tokens).
2. Export it on the syncer host: `export VAULT_TOKEN=…` (use systemd
   / Docker / K8s secret injection in production).
3. Create a *Secret Store* with type **Vault**:

    | Field              | Example                     |
    | ------------------ | --------------------------- |
    | vault_url          | `https://vault.example.com` |
    | vault_token_env    | `VAULT_TOKEN`               |
    | vault_namespace    | *(Vault Enterprise only)*   |
    | vault_mount_point  | `secret` *(default)*        |
    | vault_kv_version   | `2` *(default, `1` for legacy)* |

4. Reference entries by their KV path plus the JSON key to use:
   `kv/prod/checkmk#password`.

### AWS Secrets Manager

1. Give the host (or task / pod) IAM permission
   `secretsmanager:GetSecretValue` on the relevant secrets. Prefer
   instance / task roles over static keys.
2. Create a *Secret Store* with type **AWS Secrets Manager**:

    | Field       | Example                                   |
    | ----------- | ----------------------------------------- |
    | aws_region  | `eu-central-1`                            |
    | aws_profile | *(blank = default credential chain)*      |

3. Reference entries by SecretId/ARN. For JSON-encoded secrets, append
   the field key: `prod/checkmk#password`. Plain-string secrets can be
   referenced without `#field`.

### Environment variable

The simplest option — no external service involved, values travel via
the syncer's own process environment:

1. Create a *Secret Store* with type **Environment variable**. No
   fields need filling in.
2. Reference entries by the env var name: `CMK_PROD_PASSWORD`.

Useful for:

- Kubernetes / Docker where secrets are already mounted as env vars.
- CI pipelines that export values before running `cron run_jobs`.
- Migrations — proof-of-concept without setting up a real vault.

## Creating an Account Binding

1. Go to *Secrets Manager → Account Bindings → Create*.
2. Pick the **Account**, the **Store**, and enter the **Entry path**
   (format depends on the store, see the tables above).
3. Save. The next sync run will read the password from the vault.

The Account's own *Password* field in the normal Accounts view is
ignored while a binding is active. You can leave the field blank, or
clear it after migration — it is never read anymore.

## Rotation

- **KeePass** — edit the entry in KeePass, the file's mtime changes,
  the syncer picks it up within 5 seconds.
- **LastPass** — edit the entry in LastPass. The `lpass` CLI re-reads
  on every call.
- **Vault / AWS** — update the KV / SecretString. The syncer reads
  live on every Account lookup; no caching beyond what the upstream
  SDK does for its auth tokens.
- **envvar** — restart the syncer with the new value.

## Troubleshooting

**Account Binding saved but syncs still use the old password**  
The binding's *enabled* flag or the Store's *enabled* flag might be
off. Check both. Also check the syncer application log — binding
errors are written there with the exception from the provider.

**KeePass: "pykeepass is required"**  
Install the extra: `pip install 'cmdbsyncer-enterprise[keepass]'`.

**LastPass: "lpass is not logged in"**  
Run `lpass login <user>` as the syncer OS user on the syncer host (not
as yourself). In Docker this is usually the `uwsgi` user inside the
container.

**Vault: "Vault token rejected"**  
The env var points to an invalid/expired token. Re-issue via
AppRole, ensure it is set before the syncer process starts, and
restart the app.

**AWS: "Unable to locate credentials"**  
Default credential chain found nothing. On EC2/ECS attach an IAM
role; locally set `AWS_PROFILE` or run with `aws_profile` on the
store.

**Resolution error on one account only**  
Errors are logged per Account name under source `*Secrets*`; the
Secret Log view filters to it.
