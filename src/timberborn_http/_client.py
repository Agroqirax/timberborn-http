from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
import logging
import threading
import time
import urllib.parse

import requests
from flask import Flask

logger = logging.getLogger("timberborn_http")


# ============================================================
# Data Classes
# ============================================================


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

    # ------------------------------------------

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

    def refresh(self) -> None:
        """Refresh the lever state from the API."""
        self.state = self.api.get_lever_state(self.name)


# ============================================================
# API Client
# ============================================================


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

    # ------------------------------------------

    def _encode(self, name: str) -> str:
        """URL-encode a block name."""
        return urllib.parse.quote(name)

    # ------------------------------------------
    # Query
    # ------------------------------------------

    def get_adapters(self) -> List[Adapter]:
        """
        Retrieve all adapters.

        Returns
        -------
        List[Adapter]
            List of adapters.
        """
        logger.debug("Fetching adapters")

        r = requests.get(f"{self.host}/api/adapters")
        r.raise_for_status()

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

        r = requests.get(f"{self.host}/api/levers")
        r.raise_for_status()

        data = r.json()

        return [Lever(**lever, api=self) for lever in data]

    # ------------------------------------------
    # State helpers
    # ------------------------------------------

    def get_adapter_state(self, name: str) -> bool:
        """
        Get adapter state.

        Parameters
        ----------
        name : str
            Adapter name.

        Returns
        -------
        bool
            Adapter state.
        """
        for adapter in self.get_adapters():
            if adapter.name == name:
                return adapter.state

        raise ValueError(f"Adapter '{name}' not found")

    def get_lever_state(self, name: str) -> bool:
        """
        Get lever state.

        Parameters
        ----------
        name : str
            Lever name.

        Returns
        -------
        bool
            Lever state.
        """
        for lever in self.get_levers():
            if lever.name == name:
                return lever.state

        raise ValueError(f"Lever '{name}' not found")

    # ------------------------------------------
    # Control
    # ------------------------------------------

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
        requests.get(f"{self.host}/api/switch-on/{name}").raise_for_status()

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
        requests.get(f"{self.host}/api/switch-off/{name}").raise_for_status()

    def toggle(self, name: str) -> None:
        """
        Toggle a lever state.

        Parameters
        ----------
        name : str
            Lever name.
        """
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
        name : str
            Lever name.
        hex_color : str
            Hex color (e.g. '00ff00').
        """
        logger.info("Setting color of '%s' to %s", name, hex_color)

        name = self._encode(name)
        requests.get(
            f"{self.host}/api/color/{name}/{hex_color}"
        ).raise_for_status()

    # ------------------------------------------
    # Polling Watcher
    # ------------------------------------------

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
                state = self.get_adapter_state(name)

                if last_state is None:
                    last_state = state

                if state != last_state:
                    callback(name, state)
                    last_state = state

                time.sleep(poll_interval)

        thread = threading.Thread(target=watcher, daemon=True)
        thread.start()


# ============================================================
# Webhook Server
# ============================================================


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
                              self._on_event, methods=["GET", "POST"])
        self.app.add_url_rule("/off/<name>", "off_event",
                              self._off_event, methods=["GET", "POST"])

    # ------------------------------------------

    def _on_event(self, name: str) -> str:
        name = urllib.parse.unquote(name)

        logger.info("Adapter '%s' turned ON", name)

        if name in self.on_callbacks:
            self.on_callbacks[name](name)

        return "OK"

    def _off_event(self, name: str) -> str:
        name = urllib.parse.unquote(name)

        logger.info("Adapter '%s' turned OFF", name)

        if name in self.off_callbacks:
            self.off_callbacks[name](name)

        return "OK"

    # ------------------------------------------
    # Registration
    # ------------------------------------------

    def on(self, adapter_name: str, func: Optional[Callable[[str], None]] = None):
        """
        Register a callback when an adapter turns ON.

        Can be used as a decorator or function call.
        """

        if func is None:

            def decorator(f):
                self.on_callbacks[adapter_name] = f
                return f

            return decorator

        self.on_callbacks[adapter_name] = func

    def off(self, adapter_name: str, func: Optional[Callable[[str], None]] = None):
        """
        Register a callback when an adapter turns OFF.

        Can be used as a decorator or function call.
        """

        if func is None:

            def decorator(f):
                self.off_callbacks[adapter_name] = f
                return f

            return decorator

        self.off_callbacks[adapter_name] = func

    # ------------------------------------------

    def start(self) -> None:
        """Start the webhook server in a background thread."""

        logger.info("Starting webhook server on %s:%s", self.host, self.port)

        thread = threading.Thread(
            target=self.app.run,
            kwargs={"host": self.host, "port": self.port},
            daemon=True,
        )

        thread.start()
