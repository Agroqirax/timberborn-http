from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, overload
import logging
import threading
import time
import urllib.parse

import requests
from flask import Flask, cli

logger = logging.getLogger("timberborn_http")


class TimberbornAPI:
    """
    Client for interacting with the Timberborn HTTP automation API.
    """

    def __init__(self, host: str = "http://localhost:8080"):
        self.host = host.rstrip("/")

    def _encode(self, name: str) -> str:
        return urllib.parse.quote(name, safe="")

    def _request(self, path: str) -> requests.Response:
        url = f"{self.host}{path}"
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            return r
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Failed to connect to Timberborn API at {self.host}. "
                f"Is Timberborn running & the API started?"
            ) from e
        except requests.exceptions.Timeout as e:
            raise TimeoutError(
                f"Request to {url} timed out."
            ) from e
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(
                f"HTTP error from Timberborn API: {r.status_code} {r.reason} — {url}"
            ) from e

    # ------------------------------------------------------------------
    # Fetchers
    # ------------------------------------------------------------------

    def get_adapters(self) -> List["TimberbornAPI.Adapter"]:
        """Retrieve all adapters."""
        logger.debug("Fetching all adapters")
        data = self._request("/api/adapters").json()
        return [self.Adapter(self, d["name"]) for d in data]

    def get_levers(self) -> List["TimberbornAPI.Lever"]:
        """Retrieve all levers."""
        logger.debug("Fetching all levers")
        data = self._request("/api/levers").json()
        return [self.Lever(self, d["name"]) for d in data]

    def get_adapter(self, name: str) -> "TimberbornAPI.Adapter":
        """Retrieve a single adapter by name."""
        logger.debug("Fetching adapter '%s'", name)
        # validates existence
        self._request(f"/api/adapters/{self._encode(name)}")
        return self.Adapter(self, name)

    def get_lever(self, name: str) -> "TimberbornAPI.Lever":
        """Retrieve a single lever by name."""
        logger.debug("Fetching lever '%s'", name)
        # validates existence
        self._request(f"/api/levers/{self._encode(name)}")
        return self.Lever(self, name)

    # ------------------------------------------------------------------
    # Low-level control (used by Adapter/Lever, but also callable directly)
    # ------------------------------------------------------------------

    def get_adapter_state(self, name: str) -> bool:
        """Fetch the live state of an adapter."""
        data = self._request(f"/api/adapters/{self._encode(name)}").json()
        return bool(data["state"])

    def get_lever_state(self, name: str) -> bool:
        """Fetch the live state of a lever."""
        data = self._request(f"/api/levers/{self._encode(name)}").json()
        return bool(data["state"])

    def get_lever_spring_return(self, name: str) -> bool:
        """Fetch the live springReturn value of a lever."""
        data = self._request(f"/api/levers/{self._encode(name)}").json()
        return bool(data["springReturn"])

    def switch_on(self, name: str) -> None:
        """Switch a lever ON."""
        logger.info("Switching ON lever '%s'", name)
        self._request(f"/api/switch-on/{self._encode(name)}")

    def switch_off(self, name: str) -> None:
        """Switch a lever OFF."""
        logger.info("Switching OFF lever '%s'", name)
        self._request(f"/api/switch-off/{self._encode(name)}")

    def toggle(self, name: str) -> None:
        """Toggle a lever between ON and OFF."""
        logger.info("Toggling lever '%s'", name)
        if self.get_lever_state(name):
            self.switch_off(name)
        else:
            self.switch_on(name)

    def set_color(self, name: str, hex_color: str) -> None:
        """
        Set lever color.

        Parameters
        ----------
        hex_color : str
            Hex color without '#' (e.g. '00ff00').
        """
        hex_color = hex_color.lstrip("#")
        if len(hex_color) != 6 or not all(c in "0123456789abcdefABCDEF" for c in hex_color):
            raise ValueError(
                f"Invalid hex color: '{hex_color}'. Expected 6 hex digits.")
        logger.info("Setting color of '%s' to #%s", name, hex_color)
        self._request(f"/api/color/{self._encode(name)}/{hex_color}")

    # ------------------------------------------------------------------
    # Inner classes
    # ------------------------------------------------------------------

    class Adapter:
        """
        Represents a Timberborn HTTP Adapter block.

        Attributes
        ----------
        name : str
            Name of the adapter block in-game.
        state : bool
            Live-fetched state of the adapter (True = ON). Calls the API on access.
        """

        def __init__(self, api: "TimberbornAPI", name: str):
            self._api = api
            self.name = name

        @property
        def state(self) -> bool:
            """Live state — fetches from API on every access."""
            return self._api.get_adapter_state(self.name)

        def __repr__(self) -> str:
            return f"Adapter(name={self.name!r})"

    class Lever:
        """
        Represents a Timberborn HTTP Lever block.

        Attributes
        ----------
        name : str
            Name of the lever block in-game.
        state : bool
            Live-fetched state of the lever (True = ON). Calls the API on access.
        springReturn : bool
            Live-fetched springReturn flag. Calls the API on access.
        """

        def __init__(self, api: "TimberbornAPI", name: str):
            self._api = api
            self.name = name

        @property
        def state(self) -> bool:
            """Live state — fetches from API on every access."""
            return self._api.get_lever_state(self.name)

        @property
        def spring_return(self) -> bool:
            """Live springReturn — fetches from API on every access."""
            return self._api.get_lever_spring_return(self.name)

        def switch_on(self) -> None:
            """Switch this lever ON."""
            self._api.switch_on(self.name)

        def switch_off(self) -> None:
            """Switch this lever OFF."""
            self._api.switch_off(self.name)

        def toggle(self) -> None:
            """Toggle this lever."""
            self._api.toggle(self.name)

        def set_color(self, hex_color: str) -> None:
            """Set the lever color (hex without '#', e.g. 'ff0000')."""
            self._api.set_color(self.name, hex_color)

        def __repr__(self) -> str:
            return f"Lever(name={self.name!r})"


class TimberbornWebhookServer:
    """
    Webhook server that receives adapter events from Timberborn.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8081):
        """
        Create a webhook server.

        Parameters
        ----------
        host : str
            Host to bind to.
        port : int
            Port to listen on.
        """

        self.host = host
        self.port = port

        self.app = Flask("timberborn_webhooks")

        self.on_callbacks: Dict[str, Callable[[str], None]] = {}
        self.off_callbacks: Dict[str, Callable[[str], None]] = {}

        self.app.add_url_rule("/on/<name>", "on_event",
                              lambda name: self._event("ON", name),
                              methods=["GET", "POST"])

        self.app.add_url_rule("/off/<name>", "off_event",
                              lambda name: self._event("OFF", name),
                              methods=["GET", "POST"])

        self.start()

    def _event(self, state: str, name: str):
        name = urllib.parse.unquote(name)

        logger.info("Adapter '%s' turned %s", name, state)

        callbacks = self.on_callbacks if state == "ON" else self.off_callbacks

        if name in callbacks:
            callbacks[name](name)

        return "OK"

    @overload
    def on_event(self, adapter_name: str) -> Callable[[
        Callable[[str], None]], Callable[[str], None]]: ...

    @overload
    def on_event(self, adapter_name: str,
                 func: Callable[[str], None]) -> None: ...

    def on_event(
        self,
        adapter_name: str,
        func: Optional[Callable[[str], None]] = None
    ) -> Optional[Callable[[Callable[[str], None]], Callable[[str], None]]]:
        """
        Register a callback when an adapter turns ON.

        Can be used as a decorator or function call.
        """

        if func is None:
            def decorator(f: Callable[[str], None]) -> Callable[[str], None]:
                self.on_callbacks[adapter_name] = f
                return f

            return decorator

        self.on_callbacks[adapter_name] = func
        return None

    @overload
    def off_event(self, adapter_name: str) -> Callable[[
        Callable[[str], None]], Callable[[str], None]]: ...

    @overload
    def off_event(self, adapter_name: str,
                  func: Callable[[str], None]) -> None: ...

    def off_event(
        self,
        adapter_name: str,
        func: Optional[Callable[[str], None]] = None
    ) -> Optional[Callable[[Callable[[str], None]], Callable[[str], None]]]:
        """
        Register a callback when an adapter turns OFF.

        Can be used as a decorator or function call.
        """

        if func is None:
            def decorator(f: Callable[[str], None]) -> Callable[[str], None]:
                self.off_callbacks[adapter_name] = f
                return f

            return decorator

        self.off_callbacks[adapter_name] = func
        return None

    def start(self) -> None:
        """Start webhook server. Can take a second or two to start."""
        logger.info("Starting webhook server on %s:%s", self.host, self.port)

        cli.show_server_banner = lambda *x: None

        logging.getLogger("werkzeug").setLevel(logging.ERROR)

        thread = threading.Thread(
            target=lambda: self.app.run(
                host=self.host,
                port=self.port,
                debug=False,
                use_reloader=False
            ),
            daemon=True,
        )

        thread.start()
