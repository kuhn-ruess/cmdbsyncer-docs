# Ansible Endpoints

Base path: `/api/v1/ansible` — needs the API role `ansible` or `all`.

These endpoints expose the Ansible inventory of the CMDBsyncer so it can be used
directly as a dynamic inventory source from other servers. They render the same
data as `cmdbsyncer ansible inventory <provider>` on the command line, so HTTP
and CLI never drift apart. See [Inventory Providers](../ansible/inventory_providers.md)
for how providers are defined.

---

## `GET /api/v1/ansible/inventory`

The names of all registered inventory providers.

```bash
curl -u "user:password" \
     https://cmdbsyncer.example.com/api/v1/ansible/inventory
```

```json
{"providers": ["ansible", "cmk_sites"]}
```

---

## `GET /api/v1/ansible/inventory/<provider>`

The full inventory of one provider, in the JSON shape Ansible expects from a
dynamic inventory script.

```bash
curl -u "user:password" \
     https://cmdbsyncer.example.com/api/v1/ansible/inventory/ansible
```

```json
{
  "_meta": {"hostvars": {"srv-web01": {"ansible_host": "10.0.0.1"}}},
  "linux": {"hosts": ["srv-web01"]}
}
```

| Parameter | Description |
|---|---|
| `host` | Return only this host's variables, the `--host` mode of a dynamic inventory |

```bash
curl -u "user:password" \
     "https://cmdbsyncer.example.com/api/v1/ansible/inventory/ansible?host=srv-web01"
```

An unknown provider or host answers `404` with a `message` field.

For a user [restricted to accounts or templates](index.md#restricting-a-user-to-accounts)
both the host variables and every group's host list are pruned to the hosts that
user may reach.

## Use it from Ansible

You do not have to call the endpoint yourself: the `cmdbsyncer-inventory`
dynamic inventory plugin talks to exactly this URL in its `http` mode and hands
the result to `ansible-playbook` — see
[cmdbsyncer-inventory Plugin](../ansible/cmdbsyncer_inventory.md).
