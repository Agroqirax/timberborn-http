#!/usr/bin/env python3
"""
Object-oriented usage example.
Demonstrates controlling levers as objects.
"""
from timberborn_http import TimberbornAPI  # Import module

api = TimberbornAPI("http://localhost:8080")  # Start API

levers = api.get_levers()  # Get levers
lever1 = next(lever for lever in levers if lever.name ==
              "HTTP Lever 1")  # Get 'HTTP Lever 1'

# Control the lever using object methods
lever1.on()  # Turn lever on
# lever.off()
# lever.toggle()

lever1.set_color("00ff00")  # Set lever color to #00ff00 (green)
lever1.get_state()  # Refresh state
# Print current state
print(f"'HTTP Lever 1' state: {'ON' if lever1.state else 'OFF'}")
