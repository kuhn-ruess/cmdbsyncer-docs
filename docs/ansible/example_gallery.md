# Example Playbook Gallery

Copy-paste-ready playbooks for common automation tasks, each paired with the matching CMDB rule snippet so you can dispatch them via the [Run Playbook UI](run_from_ui.md) or the [Playbook Fire Rules](fire_rules.md). Drop the playbook into `ansible/`, register it in `ansible/playbooks.local.yml`, and you're done.

> Convention: site-local playbooks live in `ansible/local_*.yml`. The `local_` prefix is gitignored, so your additions never collide with future bundled playbooks.

## Windows Patch Rollout

Roll out pending Windows updates during a maintenance window.

`ansible/local_windows_patch.yml`:

```yaml
---
- name: "Patch Windows hosts"
  hosts: all
  gather_facts: true
  tasks:
    - name: "Search for security and critical updates"
      ansible.windows.win_updates:
        category_names:
          - SecurityUpdates
          - CriticalUpdates
        state: searched
      register: update_search

    - name: "Install pending updates"
      ansible.windows.win_updates:
        category_names:
          - SecurityUpdates
          - CriticalUpdates
        reboot: true
        reboot_timeout: 1800
      when: update_search.found_update_count | default(0) > 0
```

`ansible/playbooks.local.yml`:

```yaml
playbooks:
  - file: local_windows_patch.yml
    name: "Windows: Patch (security + critical)"
```

Fire Rule (target only Windows hosts):

| Field | Value |
| :---- | :---- |
| Condition | `match_type = tag`, tag `os_family` equals `Windows` |
| Outcome | playbook `local_windows_patch.yml` |

---

## Cron Deployment

Sync a cronjob entry from the Syncer to every matching host. The cron command itself comes from a host attribute so you can drive it from the CMDB.

`ansible/local_deploy_cron.yml`:

```yaml
---
- name: "Deploy site cronjob"
  hosts: all
  become: true
  tasks:
    - name: "Install /etc/cron.d/syncer entry"
      ansible.builtin.cron:
        name: "{{ cron_name }}"
        user: "{{ cron_user | default('root') }}"
        minute: "{{ cron_minute | default('*/15') }}"
        job: "{{ cron_command }}"
        cron_file: syncer
      when: cron_command is defined
```

`ansible/playbooks.local.yml`:

```yaml
playbooks:
  - file: local_deploy_cron.yml
    name: "Cron: Deploy entry from CMDB"
```

Use Custom Variables on the Ansible attribute rule to feed `cron_name`, `cron_command` etc. from host labels.

---

## Password Rotation

Rotate a service-account password and update its sudoers entry. Driven by an extra-var so the password never lands in a playbook commit.

`ansible/local_rotate_service_pw.yml`:

```yaml
---
- name: "Rotate svc_monitoring password"
  hosts: all
  become: true
  vars:
    svc_user: svc_monitoring
  tasks:
    - name: "Set new password"
      ansible.builtin.user:
        name: "{{ svc_user }}"
        password: "{{ new_password | password_hash('sha512') }}"
      when: new_password is defined

    - name: "Allow NOPASSWD sudo for monitoring commands"
      ansible.builtin.copy:
        dest: "/etc/sudoers.d/{{ svc_user }}"
        content: "{{ svc_user }} ALL=(ALL) NOPASSWD: /usr/bin/check_*\n"
        mode: "0440"
        validate: "/usr/sbin/visudo -cf %s"
```

Trigger from the UI with **Extra Vars** = `new_password=…`. Treat the run as one-shot — do not register it as a fire rule.

---

## Fileadmin Sync

Copy files from the [Fileadmin](../basics/fileadmin.md) area onto matching hosts.

`ansible/local_fileadmin_sync.yml`:

```yaml
---
- name: "Sync /etc/cmdbsyncer payload"
  hosts: all
  become: true
  vars:
    syncer_files_dir: /var/cmdbsyncer/files
  tasks:
    - name: "Ensure target directory exists"
      ansible.builtin.file:
        path: /etc/cmdbsyncer
        state: directory
        mode: "0755"

    - name: "Copy payload"
      ansible.builtin.copy:
        src: "{{ syncer_files_dir }}/{{ inventory_hostname }}/"
        dest: /etc/cmdbsyncer/
        mode: preserve
      delegate_to: localhost
      run_once: false
```

`ansible/playbooks.local.yml`:

```yaml
playbooks:
  - file: local_fileadmin_sync.yml
    name: "Fileadmin: Sync payload to host"
```

---

## More

The bundled playbooks (`cmk_agent_mngmt.yml`, `cmk_server_mngmt.yml`, `cmk_omd_cleanup.yml`, `server_mngmt.yml`) are themselves copy-paste-ready references — see the source under [`ansible/`](https://github.com/kuhn-ruess/cmdbsyncer/tree/main/ansible) in the Git repository.
