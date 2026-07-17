from pathlib import Path
from datetime import datetime
import shutil
import time as timelib
import psutil

from heard.tools.helpers.network import _has_internet, NetworkState, _has_active_interface
from heard.tools.helpers.system import format_bytes, is_physical_disk
from .types import Ok, Rejected, Result


def _battery() -> tuple[str, int] | None:
    for supply in Path("/sys/class/power_supply").iterdir():
        capacity = supply / "capacity"
        if capacity.is_file():
            return supply.name, int(capacity.read_text().strip())
    return None


def _time():
    return datetime.now()


def _network() -> NetworkState:
    if not _has_active_interface():
        return NetworkState.DISCONNECTED
    if _has_internet():
        return NetworkState.CONNECTED
    return NetworkState.LIMITED


def _disk():
    usage = shutil.disk_usage("/")
    return {
        "total": format_bytes(usage.total),
        "used": format_bytes(usage.used),
        "free": format_bytes(usage.free),
        "percent": round(usage.used / usage.total * 100, 1),
    }


SUB = {
    "battery": _battery,
    "time": _time,
    "network": _network,
    "disk": _disk,
}


def system_query(query: str) -> Result:
    fn = SUB.get(query)
    if fn is None:
        return Rejected("system_query", f"unknown query {query!r}", "invalid_value")
    try:
        result = fn()
        return Ok("system_query", str(result))
    except Exception as e:
        return Failed("system_query", str(e))
