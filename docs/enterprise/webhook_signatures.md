# Webhook Signatures

Requires the [Enterprise Edition](index.md).

## What it does

Hardens the community `POST /api/v1/syncer/cron/trigger/<group>`
endpoint with cryptographic request signing (HMAC-SHA256),
replay-protection via a timestamp window, and per-group IP
allowlists.

Without the feature, the trigger endpoint only checks a static
`X-Webhook-Token`. With it, each group can require **signed**
requests — the same pattern GitHub, Stripe, and Slack use for
their webhooks.

Enforced only on groups that have an enabled **Webhook Policy**
attached, so the feature can be rolled out group-by-group without
breaking existing integrations.

## Setup

1. Open **Cronjobs → Webhook Policies → Create**.
2. Pick the target CronGroup. The `signing_secret` is generated
   automatically; copy it into your webhook sender.
3. Configure the policy:

    | Field                        | Meaning                                        |
    | ---------------------------- | ---------------------------------------------- |
    | `require_signature`          | Reject requests without HMAC signature         |
    | `signing_secret`             | Auto-generated; **Regenerate signing secret** bulk action rotates it |
    | `timestamp_window_seconds`   | Max clock skew accepted (default 300 = 5 min)  |
    | `ip_allowlist`               | Comma-separated IPv4/IPv6 CIDRs; blank = any   |

## Signing a request

The sender computes the signature over `<timestamp>.<body>`:

```python
import hmac, hashlib, time, requests

secret = "paste-signing-secret-here"
body = b""                                 # trigger endpoint has no body
timestamp = str(int(time.time()))
signed = f"{timestamp}.".encode() + body
signature = hmac.new(
    secret.encode(), signed, hashlib.sha256
).hexdigest()

requests.post(
    "https://syncer.example.com/api/v1/syncer/cron/trigger/prod-cmk",
    data=body,
    headers={
        "X-Timestamp": timestamp,
        "X-Signature-SHA256": f"sha256={signature}",
    },
)
```

Server-side verification rejects with `401` if:

- `X-Timestamp` or `X-Signature-SHA256` is missing or malformed
- `X-Timestamp` is older or newer than `timestamp_window_seconds`
- HMAC of `<timestamp>.<body>` does not match (constant-time
  comparison)

## IP allowlist

Set `ip_allowlist` to a comma-separated list of sources — CIDRs
and single addresses, IPv4 or IPv6:

```
10.0.0.0/8, 192.168.1.42, 2001:db8:abcd::/48
```

Blank means "any source".

The allowlist is checked **before** the signature — a request from
an unlisted address gets a plain `403`, not a signature-mismatch
`401`, so an attacker cannot probe source-IP restrictions by
trying different payloads.

## Rotation

The **Regenerate signing secret** bulk action replaces the stored
secret. All clients using the old value immediately start failing
signature validation.

For stricter environments, consider regenerating on a schedule
(via a small cron job + API) and rolling the new value into the
sending system through your normal secret distribution path.

## Audit trail

All validation outcomes are recorded in the [Audit Log](audit_log.md)
when that feature is present:

- `webhook.triggered` with `metadata.auth = 'signature'` on success
- `webhook.rejected` with `metadata.reason` matching the reject
  reason (`Invalid signature`, `X-Timestamp outside the allowed window`,
  `IP not in allowlist`, …)

## Compatibility

Groups **without** a WebhookPolicy keep their plain token-auth
behaviour — existing integrations don't break. Migration is:

1. Create a policy for the group you want to harden.
2. Update the sender to emit signed requests.
3. Verify via the audit log that `signature`-auth'd triggers arrive.
4. (Optional) Disable the legacy `webhook_token` on the CronGroup
   so only signed requests are accepted.
