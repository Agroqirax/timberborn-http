#!/usr/bin/env python3
"""
Decorator-based webhook example.
Demonstrates using decorators to register event handlers.
"""
from timberborn_http import TimberbornWebhookServer

server = TimberbornWebhookServer()


@server.on("HTTP Adapter 1")  # type: ignore
def on_func(name):
    print(f"Pump {name} turned ON!")


@server.off("HTTP Adapter 1")  # type: ignore
def off_func(name):
    print(f"Pump {name} turned OFF!")


# Start the server
server.start()
print("Webhook server running. Press Ctrl+C to stop.")
while True:
    pass
