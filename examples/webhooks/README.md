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
@server.on("HTTP Adapter 1")
def on_func(name):
    print(f"Adapter {name} turned ON!")
```

Finally start the server & remember to put an infinite while loop at the end so the program keeps running

```python
server.start()

while True:
    pass
```

The functions `server.on(name, func)` & `@server.on(name)` only keep the last function registered.
For example:

```python
@server.on("HTTP Adapter 1")
def func_a(name):
    print(f"Adapter {name} turned ON A!")


@server.on("HTTP Adapter 1")
def func_b(name):
    print(f"Adapter {name} turned ON B!")
```

Only func_b(name) will run when 'HTTP Adapter 1 turns on.

To run multiple functions create a meta function & register that

```python
@server.on("HTTP Adapter 1")
def on_func(name):
    func_a(name)
    func_b(name)
```

More examples in this folder
