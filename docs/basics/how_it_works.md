# How it all works


``` mermaid
graph LR
SD[Source Database]
SC[Source CSV]
S[CMDB Syncer DB]
C[Checkmk]
I[I-Doit]
N[Netbox]
R[Rest API]
O[Other Source]
RE[CMDB Syncer Rules]


SD --> S
SC --> S
R --> S
O --> S


S --> RE

C --> S 
RE --> C
N --> S
RE --> N

I --> S
RE --> I



```

The CMDB Syncer [imports](import.md) all sort of devices as Hosts into his Database. Along with the Hostnames, [Labels and Inventory](host_labels_inventory.md) will store as attributes. That could be an IP-Address, a Contact or every other type of Data, which fit in a key value pair like Strings or event Lists and Dicts.

With rules, you can then [add additional Attributes](custom_attributes.md) and [Rewrite](rewrite_attributes.md) existing ones. The goal is to use this Attributes as Condition, to control the Process of [export](export.md) to another system.

The Functions of the Export depend on the Other System. You will find the Details on the Module Section.

When a Host is no longer found on an import source, it will be deleted after a grace time. Hosts no longer in this Database, will also be deleted on the export target.


With the Command Line Interface of the Syncer, you can debug all Outcomes before you start the Sync. Some Modules like Checkmk support Web based Debug Options.

## Architecture

The System is Module-based. It supports [Plugins](../advanced/own_plugins.md) to import and export, which can use a simple API, but also ships well tested internal plugins who cover a lot.

The Application is written in Python, the Local Database is a MongoDB. [Docker](../installation/setup_docker.md) is also fully supported to run it.

The Admin Interface uses Flask-Admin. This simplifies a lot, but also limits some things in the frontend.
