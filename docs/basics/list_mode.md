# Outcomes List Mode

Some rules support iterating over list-based variables. This multiplies the number of rule outcomes by looping over the items in a list attribute.

Rules that support this feature show two extra fields in the outcome section:

- **List Variable Name** — the attribute containing the list to iterate over
- **Enable List Mode** checkbox — must be checked to activate the feature

In the outcome _Param_ field, use `LIST_VAR` to access the current loop variable.

## Example

Your host has this attribute:

```python
contacts: [{'name': 'Harry'}, {'name': 'Hirsch'}]
```

Set _List Variable Name_ to `contacts` and use `{{LIST_VAR['name']}}` as the Param value.

The rule will now produce two separate outcomes — one with `Harry` and one with `Hirsch`. All other outcome fields are duplicated for each iteration.

## Multiple List Variables in One Rule

If a rule has more than one list variable, make sure the lists are always in the same order and have the same length. Ideally, they refer to different keys from the same list of dicts. If the lists are independent and have different orders or lengths, data can be mixed up unexpectedly.
