# Timberborn HTTP API Wrapper

A Python library for interacting with the Timberborn HTTP automation API.
Supports both direct API control and webhook-based event handling.

## Features

- Get the state of levers & adapters from timberborn
- Update the state of levers
- Receive webhooks and trigger actions

## Installation

```bash
pip install timberborn-http
```

## Quickstart

### 1. Direct API Control

```python
from timberborn_http import TimberbornAPI

api = TimberbornAPI("http://localhost:8080")

# Get all levers
levers = api.get_levers()
for lever in levers:
    print(lever.name, lever.state)

# Control a lever
api.switch_on("HTTP Lever 1")
api.set_color("HTTP Lever 1", "ff0000")
```

### 2. Webhook Events

```python
from timberborn_http import TimberbornWebhookServer

server = TimberbornWebhookServer()

@server.on("HTTP Lever 1")
def handle_on(name):
    print(f"{name} turned ON!")

server.start()
```

## Documentation & Examples

- [API Usage](/examples/api): Direct control and polling
- [Webhook Usage](/examples/webhooks): Real-time event handling

## Getting Help

- [GitHub Issues](https://github.com/agroqirax/timberborn-http/issues)
- [Discord](https://discord.gg/timberborn)

## Commands

- `python -m venv .venv`
- `pip install -r requirements.txt`
- `pip install -e .`
- `python -m build`
- `python3 -m twine upload --repository testpypi dist/*`
