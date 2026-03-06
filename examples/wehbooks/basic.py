#!/usr/bin/env python3
"""
Basic webhook server example.
Demonstrates responding to adapter ON/OFF events.
"""
from timberborn_http import TimberbornWebhookServer

server = TimberbornWebhookServer()


def on_func(name):
    print(f"{name} turned ON!")


def off_func(name):
    print(f"{name} turned OFF!")


# Register callbacks
server.on("Main Water Pump", on_func)
server.off("Main Water Pump", off_func)

# Start the server
server.start()
print("Webhook server running. Press Ctrl+C to stop.")
while True:
    pass
