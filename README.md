# Timberborn HTTP API Wrapper

A Python library for interacting with the Timberborn HTTP automation API.
Supports both direct API control and webhook-based event handling.

## Features

- Get the state of levers and adapters from Timberborn
- Change lever states
- Receive webhook events and trigger actions

## Installation

```bash
pip install timberborn-http
```

## Quickstart

### Direct API Control

```python
from timberborn_http import TimberbornAPI

api = TimberbornAPI("http://localhost:8080")

# Get all levers
for lever in api.get_levers():
    print(f"Lever {lever.name}is currently {lever.state}")

# Control a lever
api.switch_on("HTTP Lever 1")
api.set_color("HTTP Lever 1", "ff0000")
```

### Webhook Events

```python
import time
from timberborn_http import TimberbornWebhookServer

server = TimberbornWebhookServer(port=8081)

@server.on_event("HTTP Lever 1")
def handle_on(name):
    print(f"{name} turned ON!")

while True:
    time.sleep(1)
```

More examples & details in the [examples](https://github.com/Agroqirax/timberborn-http/tree/main/examples) folder

## Getting Help

- [GitHub Issues](https://github.com/agroqirax/timberborn-http/issues)
- [Discord](https://discord.gg/timberborn) in `#⏱️automation` or `#🤖mod-creators`
