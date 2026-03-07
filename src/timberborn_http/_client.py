from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, overload
import logging
import threading
import time
import urllib.parse

import requests
from flask import Flask, cli

logger = logging.getLogger("timberborn_http")


@dataclass
class Adapter:
    """
    Represents a Timberborn HTTP Adapter block.

    Attributes
    ----------
    name : str
        Name of the adapter block in-game.
    state : bool
        Current state of the adapter (True = ON).
    """

    name: str
    state: bool
    api: "TimberbornAPI" = field(repr=False)

    def get_state(self) -> bool:
        """Get the adapter state from the API."""
        self.state = self.api.get_state(self.name)
        return self.state


@dataclass
class Lever:
    """
    Represents a Timberborn HTTP Lever block.

    Attributes
    ----------
    name : str
        Name of the lever block in-game.
    state : bool
        Current state of the lever (True = ON).
    springReturn : bool
        Whether the lever automatically resets.
    api : TimberbornAPI
        Reference to the API client used for control.
    """

    name: str
    state: bool
    springReturn: bool
    api: "TimberbornAPI" = field(repr=False)

    def on(self) -> None:
        """Switch this lever ON."""
        self.api.switch_on(self.name)

    def off(self) -> None:
        """Switch this lever OFF."""
        self.api.switch_off(self.name)

    def toggle(self) -> None:
        """Toggle this lever."""
        self.api.toggle(self.name)

    def set_color(self, hex_color: str) -> None:
        """
        Set the lever color.

        Parameters
        ----------
        hex_color : str
            Hex color code (e.g. 'ff0000').
        """
        self.api.set_color(self.name, hex_color)

    def get_state(self) -> bool:
        """Get the lever state from the API."""
        self.state = self.api.get_state(self.name)
        return self.state


class TimberbornAPI:
    """
    Client for interacting with the Timberborn HTTP automation API.
    """

    def __init__(self, host: str = "http://localhost:8080"):
        """
        Initialize the API client.

        Parameters
        ----------
        host : str
            Base URL of the Timberborn API.
        """
        self.host = host.rstrip("/")

    def _encode(self, name: str) -> str:
        """URL-encode a block name."""
        return urllib.parse.quote(name)

    def _request(self, path: str):
        """
        Perform a GET request with better error handling.
        """
        url = f"{self.host}{path}"

        try:
            r = requests.get(url)
            r.raise_for_status()
            return r

        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Failed to connect to Timberborn API at {self.host}. "
                f"Is Timberborn running & the API started?"
            ) from e

    def get_adapters(self) -> List[Adapter]:
        """
        Retrieve all adapters.

        Returns
        -------
        List[Adapter]
            List of adapters.
        """
        logger.debug("Fetching adapters")

        r = self._request("/api/adapters")
        data = r.json()

        return [Adapter(**adapter) for adapter in data]

    def get_levers(self) -> List[Lever]:
        """
        Retrieve all levers.

        Returns
        -------
        List[Lever]
            List of lever objects.
        """
        logger.debug("Fetching levers")

        r = self._request("/api/levers")
        data = r.json()

        return [Lever(**lever, api=self) for lever in data]

    def get_state(self, name: str) -> bool:
        """
        Get the state of a lever or adapter.

        Parameters
        ----------
        name : str
            Block name.

        Returns
        -------
        bool
            Current state.
        """
        for adapter in self.get_adapters():
            if adapter.name == name:
                return adapter.state

        for lever in self.get_levers():
            if lever.name == name:
                return lever.state

        raise ValueError(f"No adapter or lever named '{name}' found")

    def switch_on(self, name: str) -> None:
        """
        Switch a lever ON.

        Parameters
        ----------
        name : str
            Lever name.
        """
        logger.info("Switching ON lever '%s'", name)

        name = self._encode(name)
        self._request(f"/api/switch-on/{name}")

    def switch_off(self, name: str) -> None:
        """
        Switch a lever OFF.

        Parameters
        ----------
        name : str
            Lever name.
        """
        logger.info("Switching OFF lever '%s'", name)

        name = self._encode(name)
        self._request(f"/api/switch-off/{name}")

    def toggle(self, name: str) -> None:
        """
        Toggle a lever state.

        Parameters
        ----------
        name : str
            Lever name.
        """
        logger.info("Toggling lever '%s'", name)

        if self.get_state(name):
            self.switch_off(name)
        else:
            self.switch_on(name)

    def set_color(self, name: str, hex_color: str) -> None:
        """
        Set lever color.

        Parameters
        ----------
        name : str
            Lever name.
        hex_color : str
            Hex color (e.g. '00ff00').
        """
        logger.info("Setting color of '%s' to %s", name, hex_color)

        name = self._encode(name)
        self._request(f"/api/color/{name}/{hex_color}")

    def watch_adapter(
        self,
        name: str,
        callback: Callable[[str, bool], None],
        poll_interval: float = 1.0,
    ) -> None:
        """
        Watch an adapter and trigger a callback when its state changes.

        Parameters
        ----------
        name : str
            Adapter name.
        callback : Callable[[str, bool], None]
            Function called with (name, state).
        poll_interval : float
            Seconds between polls.
        """

        def watcher():
            logger.info("Watching adapter '%s'", name)

            last_state: Optional[bool] = None

            while True:
                state = self.get_state(name)

                if last_state is None:
                    last_state = state

                if state != last_state:
                    callback(name, state)
                    last_state = state

                time.sleep(poll_interval)

        thread = threading.Thread(target=watcher, daemon=True)
        thread.start()


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

    def _event(self, state: str, name: str):
        name = urllib.parse.unquote(name)

        logger.info("Adapter '%s' turned %s", name, state)

        callbacks = self.on_callbacks if state == "ON" else self.off_callbacks

        if name in callbacks:
            callbacks[name](name)

        return "OK"

    @overload
    def on(self, adapter_name: str) -> Callable[[
        Callable[[str], None]], Callable[[str], None]]: ...

    @overload
    def on(self, adapter_name: str, func: Callable[[str], None]) -> None: ...

    def on(
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
    def off(self, adapter_name: str) -> Callable[[
        Callable[[str], None]], Callable[[str], None]]: ...

    @overload
    def off(self, adapter_name: str, func: Callable[[str], None]) -> None: ...

    def off(
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
