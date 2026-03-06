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
levers = api.get_levers()  # Get list of levers
for lever in levers:  # Iterate thru list
    # Print name & state
    print(f"- {lever.name}: {'ON' if lever.state else 'OFF'}")

# List all adapters
print("\nAdapters:")
adapters = api.get_adapters()
for adapter in adapters:
    print(f"- {adapter.name}: {'ON' if adapter.state else 'OFF'}")

print()

# Control a lever
api.switch_on("HTTP Lever 1")  # Set 'HTTP Lever 1' to on
print("Turned 'HTTP Lever 1' on")  # Print that action was performed
print()  # Print blank line

sleep(1)  # Wait 1 second before proceeding

api.switch_off("HTTP Lever 1")
print("Turned 'HTTP Lever 1' off")
print()

sleep(1)

api.set_color("HTTP Lever 1", "ff0000")
print("Set color of 'HTTP Lever 1' to #ff0000")
print()

sleep(1)

api.toggle("HTTP Lever 1")
print("Toggled state of 'HTTP Lever 1'")

print()

print(f"State of 'HTTP Adapter 1': {api.get_adapter_state("HTTP Adapter 1")}")
print(f"State of 'HTTP Lever 1': {api.get_lever_state("HTTP Lever 1")}")
