# List Variable Mode

Some Rules support the Iteration of List-based Variables.
These Rules have two extra options in their outcome:

![](attachments/Pasted%20image%2020250122174915.png)

This function basically multiplies the Outcomes by iteration over the Attribute given in 'List Variable Name' Field. Also, you need to activate it using the Checkbox.

In the 'Param' Field, you then use `LIST_VAR` to access the loop Variable.

## Example
Best to Understand is using an Example:

Your host has this Varialbe:

``` python
  Variablename: [{'name': 'Harry'}, {'name': 'Hirsch'}]
```

If you then set 
```python
{{LIST_VAR['name']}}
```
as Param, 

The rule will now create two more Outcomes with 'Harry' and 'Hirsch' for the used field.
All other Outcome Params will be duplicated to to 'Harry' and 'Hirsch'.

If you have more List Variables in one rule, you need to make sure that the Order of the given List Variables are always the same. Ideally, it's always the same list, but just another Dict key from it. Otherwise Data can be mixed up.


