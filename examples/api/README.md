# API Examples

## Quickstart

To use the API, import the library and create an API instance

```python
from timberborn_http import TimberbornAPI

api = TimberbornAPI("http://localhost:8080")
```

> [!TIP]
> With the [Remote API Access](https://steamcommunity.com/sharedfiles/filedetails/?id=3682669754) mod you can control the API from a different computer.
> Find your computer's IP address in the network settings under **IPv4 address**.
> Then use `http://192.168.x.xxx:8080` instead of `http://localhost:8080`.

> [!NOTE]
> If you change the port number in the game, you must use the same port in the API URL.

You can now use the following functions to interact with the API.

## Function reference

| Function                                         | Comment                                                                        |
| ------------------------------------------------ | ------------------------------------------------------------------------------ |
| `api.get_adapters() -> List[Adapter]           ` | Get all adapters                                                               |
| `api.get_levers() -> List[Lever]               ` | Get all levers                                                                 |
| `api.get_adapter(name: str) -> Adapter         ` | Get an adapter by name                                                         |
| `api.get_lever(name: str) -> Lever             ` | Get a lever by name                                                            |
| `api.get_adapter_state(name: str) -> bool      ` | Get adapter state                                                              |
| `api.get_lever_state(name: str) -> bool        ` | Get lever state                                                                |
| `api.get_lever_spring_return(name: str) -> bool` | Get lever spring return                                                        |
| `api.switch_on(name: str) -> None              ` | Switch lever on                                                                |
| `api.switch_off(name: str) -> None             ` | Switch lever off                                                               |
| `api.toggle(name: str) -> None                 ` | Toggle lever                                                                   |
| `api.set_color(name: str, color: str) -> None  ` | Set lever color. Color in the format ff0000 or a common color name such as red |

## Attributes reference

| Attribute                    | Comment                          |
| ---------------------------- | -------------------------------- |
| `Adapter.state -> bool     ` | Current adapter state            |
| `Lever.state -> bool       ` | Current lever state              |
| `Lever.springReturn -> bool` | Whether spring return is enabled |

## Object-oriented programming

If you prefer you can also use OOP like this:

```python
lever = api.get_lever("HTTP Lever 1")

lever.switch_on()
```

You can find more examples in this folder
