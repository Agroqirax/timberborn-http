from timberborn_http import TimberbornAPI

instances = TimberbornAPI.discover(timeout=3.0)

if not instances:
    quit(1)

api = instances[0]
print(api.get_levers())