
# I-Doit Sync
With the I-Doit Feature of the Syncer, you can Sync Informationen to I-Doit. That can be everything the Syncer knows about an Object, and could be everything. Everything means, you can use the inventory feature to import e.g. Checkmk Service Information, Checkmk HW/SW Inventory information, CSV or APIs. But thats True for every Syncer Module.

## How to Set it up

**Modules → i-doit →Custom Attributes**
In Rule Outcomes you can define the e.g. the Templates to send to I-Doit and use Jinja Magic to access the Attributes of the Objects.

### Category Template Examples

```
TBD
```


### Define Objects Object Type


### Define Attributes to use as Objects Description

## From a pasted list

An i-doit custom attributes rule can take a pasted list as its input instead
of the hosts: set **Rule source** to **From a pasted list**. Every row
creates one i-doit object, titled with its `hostname` (or `name`) column,
with the outcomes rendered with the columns of the row. See [Rules from a Pasted List](../basics/list_source.md) for the
list itself.
