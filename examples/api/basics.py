#!/usr/bin/env python3
"""
Basic API usage example.
Demonstrates listing and controlling levers and adapters.
"""
from timberborn_http import TimberbornAPI  # Import module
from time import sleep

api = TimberbornAPI("http://localhost:8080")  # Start API

# List all levers
print("Levers:")
for lever in api.get_levers():
    print(f"- {lever.name}: {'ON' if lever.state else 'OFF'}")

# List all adapters
print("Adapters:")
for lever in api.get_adapters():
    print(f"- {lever.name}: {'ON' if lever.state else 'OFF'}")

print()

# Control a lever
# api.switch_on("HTTP Lever 1")
# api.switch_off("HTTP Lever 1")
api.toggle("HTTP Lever 1")

api.set_color("HTTP Lever 1", "00ff00")
api.set_color("HTTP Lever 1", "red")

print(f"State of HTTP Adapter 1: {api.get_adapter("HTTP Adapter 1").state}")
