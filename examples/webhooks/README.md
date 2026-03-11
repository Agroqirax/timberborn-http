# Webhook Examples

To register a webhook first import the library & create a server class

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

Remember to put an infinite while loop at the end so the program keeps running

```python
while True:
    pass
```

Only one function can be registered per adapter. If you register more the previous one will be overridden

More examples in this folder
