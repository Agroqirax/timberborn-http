#!/usr/bin/env python3
"""
Object-oriented usage example.
Demonstrates controlling levers as objects.
"""
from timberborn_http import TimberbornAPI  # Import module

api = TimberbornAPI("http://localhost:8080")  # Start API

levers = api.get_levers()  # Get levers
lever = next(lever for lever in levers if lever.name ==
             "HTTP Lever 1")  # Get 'HTTP Lever 1'

# Control the lever using object methods
lever.on()  # Turn lever on
# lever.off()
# lever.toggle()

lever.set_color("00ff00")  # Set lever color to #00ff00 (green)
lever.refresh()  # Refresh state
print(f"Pump state: {'ON' if lever.state else 'OFF'}")  # Print current state
