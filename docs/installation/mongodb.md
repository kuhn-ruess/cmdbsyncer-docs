# MongoDB

The Syncer stores all its data in MongoDB. The Docker image ships
MongoDB 8.0, use the same major version for a local instance:

=== "RedHat / Rocky / Alma"
    Create `/etc/yum.repos.d/mongodb-org-8.0.repo`:
    ```ini
    [mongodb-org-8.0]
    name=MongoDB Repository
    baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/8.0/x86_64/
    gpgcheck=1
    enabled=1
    gpgkey=https://pgp.mongodb.com/server-8.0.asc
    ```
    Then install and start it:
    ```bash
    sudo dnf install -y mongodb-org
    sudo systemctl enable --now mongod
    ```

=== "Ubuntu"
    ```bash
    sudo apt install -y gnupg curl
    curl -fsSL https://pgp.mongodb.com/server-8.0.asc | \
        sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg --dearmor
    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu $(. /etc/os-release; echo $VERSION_CODENAME)/mongodb-org/8.0 multiverse" | \
        sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
    sudo apt update
    sudo apt install -y mongodb-org
    sudo systemctl enable --now mongod
    ```
    For Debian, follow the
    [official MongoDB guide for Debian](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-debian/).

The Syncer connects to `127.0.0.1:27017`, database `cmdb-api`, by default.
For a remote server, set `MONGODB_SETTINGS` in `local_config.py` or the
`CMDBSYNCER_MONGODB_*` environment variables, see
[Local Config](../basics/lcl_config.md).

## Illegal Instruction in a VM

MongoDB requires AVX CPU instructions. If you are running in a **virtual machine (e.g. Proxmox)**, the default CPU type (`kvm64`) does not expose AVX to the guest even if the host supports it.

Check whether AVX is available inside the VM:

```bash
grep avx /proc/cpuinfo
```

If the output is empty, configure the VM CPU type in Proxmox to expose AVX. Edit the VM config (e.g. `/etc/pve/qemu-server/<vmid>.conf`) and set a CPU type that includes AVX:

```text
cpu: x86-64-v2-AES,flags=+avx;+avx2
```

Then restart the VM. Afterwards MongoDB should start normally.
