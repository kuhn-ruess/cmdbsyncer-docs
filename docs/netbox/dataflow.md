# Dataflow Plugin

The Syncer can be used to synchronize to the Third-Party Plugin Data flow.
But this is a bit more complicated as the other Netbox Functions.

Dataflow as multiple Models. But to set it up, start with the creation of "Field Definitions".
There you map the Fields of Netbox to the Attributes of your Syncer Objects. You can also create Multiple Rules for the Same model if needed.

The second Step, is to create a 'Model Definition'. There you choose the Target Model and Connect the Field Definitions you created before.

## Field Definitions


### Field Name
The Field Name, as given in Netbox. If it is a Custom Field, you can check `Is Netbox Custom Field`.  If the Field is a "List Field", Like the list of Tags or a custom created one, you need to check `Is Netbox List Field`.

### Field Value
The Field Value can use extended Jinja Syntax. Also, you can create Multiple Outcomes with one rule. When checked `Expand Value as List`, you can provide a comma separated list here. No need to do in manually, this can also be done with Jinja, here is an Example:

```python
{% for app in jdisc_applications__list %}{{app['application']['name']}},{% endfor %}
```
Note the Comma after the bracket inside the loop.
### Use to Idenitfy
The Syncer needs to know which of your Attributes should be the used as the Field which identifies the Object in Netbox. Its necessary that exactly one Field is set as such.

