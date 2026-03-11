# API Examples

To use the API import the library & create an API class

```python
from timberborn_http import TimberbornAPI

api = TimberbornAPI("http://localhost:8080")
```

Now you can perform actions with the API like:

| Function                                               | Comment                 |
| ------------------------------------------------------ | ----------------------- |
| `api.get_adapters() -> List[Adapter]             `     | Get list of adapters    |
| `api.get_levers() -> List[Lever]                 `     | Get list of levers      |
| `api.get_adapter(name: str) -> Adapter           `     | Get adapter             |
| `api.get_lever(name: str) -> Lever               `     | Get lever               |
| `api.switch_on(name: str) -> None                `     | Switch lever on         |
| `api.switch_off(name: str) -> None               `     | Switch lever off        |
| `api.toggle(name: str) -> None                   `     | Toggle lever            |
| `api.set_color(name: str) -> None                `     | Set lever color         |
| `api.get_adapter_state(name: str) -> bool        `     | Get adapter state       |
| `api.get_lever_state(name: str) -> bool          `     | Get lever state         |
| `api.get_lever_spring_return(self, name: str) -> bool` | Get lever spring return |

If you prefer you can also use OOP like this:

```python
lever = api.get_lever("HTTP Lever 1")

lever.switch_on()
```

More examples in this folder
