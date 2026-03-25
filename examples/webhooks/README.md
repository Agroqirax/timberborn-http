# Webhook Examples

When the state of an adapter changes the game can send a webhook. TimberbornWebhookServer can recieve these webhooks and run functions when that happens.

## Quickstart

To register a webhook, first import the library and create a server instance

```python
from timberborn_http import TimberbornWebhookServer

server = TimberbornWebhookServer(port=8081)
```

Then register callbacks with the name and function

```python
def on_func(name):
    print(f"{name} turned ON!")

server.on_event("HTTP Adapter 1", on_func)
```

It is also possible to use decorators to register callbacks

```python
@server.on_event("HTTP Adapter 1")
def on_func(name):
    print(f"Adapter {name} turned ON!")
```

> [!IMPORTANT]
> The name of the adapter will be passed as a parameter so it is important that the function has **exactly one** parameter, even if you don't use it

The server will only receive webhooks while the program is running.
You can put an infinite while loop at the end so the program keeps running.

```python
import time

while True:
    time.sleep(1)
```

Only one function can be registered per adapter. If you register more the previous one will be overridden

You can find more examples in this folder

## Function reference

| Function                                               | Comment                                                                  |
| ------------------------------------------------------ | ------------------------------------------------------------------------ |
| `server.on_event(name: str, func: callable) -> None  ` | Register `func(name)` to run when the adapter with name `name` turns on  |
| `server.off_event(name: str, func: callable) -> None ` | Register `func(name)` to run when the adapter with name `name` turns off |
| `@server.on_event(name: str) -> None  `                | Register `func(name)` to run when the adapter with name `name` turns on  |
| `@server.off_event(name: str) -> None `                | Register `func(name)` to run when the adapter with name `name` turns off |
