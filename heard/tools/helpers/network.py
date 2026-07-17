from enum import Enum
from pathlib import Path
import socket


class NetworkState(str, Enum):
    CONNECTED = "connected"
    LIMITED = "limited"
    DISCONNECTED = "disconnected"


def _has_active_interface() -> bool:
    """Return True if any non-loopback interface is operational."""

    for iface in Path("/sys/class/net").iterdir():
        if iface.name == "lo":
            continue

        try:
            operstate = (iface / "operstate").read_text().strip()
            if operstate == "up":
                return True
        except OSError:
            continue

    return False


def _has_internet(timeout: float = 1.5) -> bool:
    """Return True if the Internet is reachable."""

    endpoints = (
        ("1.1.1.1", 443),  # Cloudflare
        ("8.8.8.8", 53),   # Google DNS
    )

    for host, port in endpoints:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            pass

    return False