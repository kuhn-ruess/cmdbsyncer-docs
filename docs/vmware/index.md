# VMware vCenter

The VMware plugin connects to a vCenter and can:

- **Inventorize** virtual machines into the Syncer (power state, guest OS, resource pool, ESXi host, VMware Tools version, CPU/memory, network cards, virtual disks, IDE/SCSI controllers, datastores, networks and existing custom attributes).
- **Export Custom Attributes** back to the VMs, driven by the Syncer rules.

## Setup

Create an Account of type `VMware vCenter` and fill in:

- `address` – the vCenter hostname or IP
- `username` / `password` – a vCenter user allowed to read the inventory (and to write custom attributes if you use the export)

## Account Settings

The following extra configuration is possible via the account's custom fields:

| Field              | Description                                                                                                                                   |
| :----------------- | :------------------------------------------------------------------------------------------------------------------------------------------- |
| `verify_cert`      | `True` for certificate validation, else `False`                                                                                              |
| `inventory_filter` | Limit which VMs are processed. Comma-separated `key:value` pairs matched against any collected attribute, e.g. `power_state:poweredOn` or `power_state:poweredOn,guest_os:Linux`. The same key repeated is an OR match, different keys must all match (AND). New accounts are pre-filled with `power_state:poweredOn`; clear the field to process all VMs. |

## Custom Attributes

The export writes **vCenter Custom Attributes** onto your VMs, driven by the
Syncer rules. This lets you push information the Syncer knows about a host
(labels, inventory data, attributes from other sources) directly into vCenter,
where it becomes visible in the *Custom Attributes* section of each VM.

Two rule types control the export:

- **Rewrite Attributes** – optionally rewrite/normalise the host's existing
  attributes before they are used (same mechanism as
  [Rewrite Attributes](../basics/rewrite_attributes.md)).
- **Custom Attributes** – for every matching host, define one or more
  `attribute_name` / `attribute_value` pairs. The value is rendered with Jinja,
  so you can build it from the host's attributes, e.g. `{{ os }}` or a fixed
  string. See [Custom Attributes](../basics/custom_attributes.md) for the rule
  basics.

When `export_custom_attributes` runs, each host in the Syncer is matched
against these rules, the resulting attributes are compared with what is already
set on the VM in vCenter, and **only changed values are written back** (via the
vCenter API). VMs that are not found in vCenter, or hosts excluded by the
`inventory_filter`, are skipped.

## Commands

```bash
# Inventorize VMs from vCenter into the Syncer
cmdbsyncer vmware inventorize_custom_attributes <account>

# Export Custom Attributes from the Syncer back to the VMs
cmdbsyncer vmware export_custom_attributes <account>
```

Both commands accept `--debug`.
