# Webhook Examples

To register a webhook first import the library & create a server class

```python
from timberborn_http import TimberbornWebhookServer

server = TimberbornWebhookServer()
```

Then register callbacks with the name and function

```python
def on_func(name):
    print(f"{name} turned ON!")

server.on("HTTP Adapter 1", on_func)
```

It is also possible to use decorators to register callbacks

```python
@server.on("HTTP Adapter 1")  # type: ignore
def on_func(name):
    print(f"Pump {name} turned ON!")
```

Finally start the server & remember to put an infinite while loop at the end so the program keeps running

```python
server.start()

while True:
    pass
```

More examples in this folder
