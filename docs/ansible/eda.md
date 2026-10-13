# Event Driven Ansible

The Syncer can send events to [Event Driven Ansible](https://www.redhat.com/en/technologies/management/ansible/event-driven-ansible) (EDA). Rules decide which hosts send which event, a cronjob sends them, and a rulebook on the EDA side decides what to run, for example a job template that registers the Checkmk agent.

The module lives under **Modules → Event Driven Ansible**.

## How it works

1. An account of the type **Event Driven Ansible** names the event stream (or `ansible.eda.webhook` source) the events go to.
2. **Event Rules** match hosts with the standard condition engine (hostname, any attribute, any inventory value). Every outcome of a matching rule is one event.
3. The command `eda send_events <account>` (cronjob **"EDA: Send Events"**) walks all hosts, evaluates the enabled rules and posts one JSON event per match.
4. Every event sent is recorded in the **Event History**. A host that still matches sends the same event again only after **Resend after hours** have passed, so a registration that failed on the Ansible side is retried, but the event stream is not flooded on every cron run.

Like the [Playbook Fire Rules](fire_rules.md), sending happens only from the dedicated command, never from an inventory or export run.

## Account

Create an account under **Accounts** with the type **Event Driven Ansible**.

| Field | Value |
| :---- | :---- |
| Address | URL of the event stream, e.g. `https://aap.example.com/eda-event-streams/api/eda/v1/external_event_stream/<uuid>/post/`, or the URL of an `ansible.eda.webhook` source, e.g. `http://eda.example.com:5000/endpoint` |
| Username / Password | With a username, the request uses Basic Auth. Without a username, the password is the token. |
| auth_header | Header the token is sent in, default `Authorization` |
| auth_prefix | Put in front of the token, default `Bearer` (what `ansible.eda.webhook` with `token:` expects). Empty sends the bare token, for an event stream credential that compares the header with the token as is. |
| verify_cert, ca_cert_chain, ca_root_cert | TLS settings as for every account |

## Event Rules

| Field | Meaning |
| :---- | :------ |
| Conditions | Which hosts send the event |
| Event | Name of the event, the rulebook matches on `event.payload.event`. Jinja with the host attributes is allowed. |
| Extra Vars | YAML `key: value` pairs, Jinja with the host attributes is allowed. Sent as `event.payload.vars`. |
| Resend after hours | Send again after this many hours while the host still matches (default 24). `0` sends once and never again. |

An event looks like this:

```json
{
  "source": "cmdbsyncer",
  "event": "register_agent_tls",
  "hostname": "srv01",
  "rule": "Register TLS",
  "vars": {"os": "linux"},
  "timestamp": "2026-10-13T09:00:00+02:00"
}
```

Extra Vars that are no valid YAML mapping are not sent: the event shows up as failure in the Event History with the reason.

## CLI

```bash
./cmdbsyncer eda send_events ACCOUNT            # send the events
./cmdbsyncer eda send_events ACCOUNT --dry-run  # only print them
./cmdbsyncer eda debug_host srv01               # matching rules and the events of one host
```

## Example: register Checkmk agents that are not registered

1. Inventorize the agent state from Checkmk: under **Checkmk → Inventorize from Checkmk Settings**, add `Check_MK Agent` with the source **Service Plugin Output**, and run `./cmdbsyncer checkmk inventorize_hosts ACCOUNT` (or its cronjob). Every host then carries `cmk_svc__check_mk_agent_output` (see [Manage Checkmk Agents](cmk_agents.md)).
2. Create two Event Rules:

| Rule | Condition | Event |
| :--- | :-------- | :---- |
| Register TLS | `cmk_svc__check_mk_agent_output` contains `TLS is not activated on monitored host` | `register_agent_tls` |
| Register Bakery | `cmk_svc__check_mk_agent_output` contains `not registered` | `register_agent_bakery` |

   Checkmk's exact wording varies by version, check it with `./cmdbsyncer eda debug_host HOST`.

3. Put **"EDA: Send Events"** with the EDA account into a [Cronjob Group](../basics/cron.md), after the Checkmk inventory.
4. On the EDA side, a rulebook starts the matching job template, for example with the `cmk_agent_mngmt.yml` playbook and `cmk_register_tls` or `cmk_register_bakery` set:

```yaml
- name: Checkmk agent registration from the Syncer
  hosts: all
  sources:
    - ansible.eda.webhook:
        host: 0.0.0.0
        port: 5000
        token: "{{ syncer_token }}"
  rules:
    - name: Register TLS
      condition: event.payload.event == "register_agent_tls"
      action:
        run_job_template:
          name: Register Checkmk agent
          organization: Default
          job_args:
            limit: "{{ event.payload.hostname }}"
            extra_vars:
              cmk_register_tls: true
    - name: Register Bakery
      condition: event.payload.event == "register_agent_bakery"
      action:
        run_job_template:
          name: Register Checkmk agent
          organization: Default
          job_args:
            limit: "{{ event.payload.hostname }}"
            extra_vars:
              cmk_register_bakery: true
```

With an event stream in the Ansible Automation Platform, the source is the event stream instead of `ansible.eda.webhook`, the rules stay the same.
