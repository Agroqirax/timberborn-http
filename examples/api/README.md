# API Examples

To use the API import the library & create an API class

```python
from timberborn_http import TimberbornAPI

api = TimberbornAPI("http://localhost:8080")
```

Now you can perform actions with the API like:

- `api.get_adapters()` Get list of adapters
- `api.get_levers()` Get list of levers
- `api.switch_on("HTTP Lever 1")` Switch lever on
- `api.switch_off("HTTP Lever 1")` Switch lever off
- `api.toggle("HTTP Lever 1")` Toggle lever
- `api.set_color("HTTP Lever 1")` Set lever color
- `api.get_state("HTTP Lever 1")` Get the state of a lever or adapter

"HTTP Lever 1" is, of course, substitutable by any lever name.

If you prefer you can also use OOP like this:

```python
levers = api.get_levers()
lever1 = next(lever for lever in levers if lever.name ==
              "HTTP Lever 1")

lever1.on()
```
