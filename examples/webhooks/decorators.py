#!/usr/bin/env python3
"""
Decorator-based webhook example.
Demonstrates using decorators to register event handlers.
"""
from timberborn_http import TimberbornWebhookServer

server = TimberbornWebhookServer()
server.start()


@server.on("HTTP Adapter 1")
def on_func(name):
    print(f"Adapter {name} turned ON!")


@server.off("HTTP Adapter 1")
def off_func(name):
    print(f"Adapter {name} turned OFF!")


# Start the server
print("Webhook server running. Press Ctrl+C to stop.")
while True:
    pass
