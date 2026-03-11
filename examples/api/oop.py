#!/usr/bin/env python3
"""
Object-oriented usage example.
Demonstrates controlling levers as objects.
"""
from timberborn_http import TimberbornAPI  # Import module

api = TimberbornAPI("http://192.168.1.65:8080")  # Start API

lever1 = api.get_lever("HTTP Lever 1")

# Control the lever using object methods
lever1.switch_on()
lever1.switch_off()
lever1.toggle()

lever1.set_color("00ff00")  # Set lever color to #00ff00 (green)

# Print current state
print(f"'HTTP Lever 1' state: {'ON' if lever1.state else 'OFF'}")
