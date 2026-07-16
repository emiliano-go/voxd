from pathlib import Path
from datetime import datetime
import shutil
import time as timelib
import psutil

from voxd.tools.helpers.network import _has_internet, NetworkState, _has_active_interface
from voxd.tools.helpers.system import format_bytes, is_physical_disk

def battery() -> tuple[str, int] | None:
    for supply in Path("/sys/class/power_supply").iterdir():
        capacity = supply / "capacity"
        if capacity.is_file():
            return supply.name, int(capacity.read_text().strip())

    return None


def time():
    return datetime.now()


def network() -> NetworkState:
    """
    Returns:
        NetworkState.CONNECTED
        NetworkState.LIMITED
        NetworkState.DISCONNECTED
    """

    if not _has_active_interface():
        return NetworkState.DISCONNECTED

    if _has_internet():
        return NetworkState.CONNECTED

    return NetworkState.LIMITED

def disk():
    usage = shutil.disk_usage("/")

    return {
        "total": format_bytes(usage.total),
        "used": format_bytes(usage.used),
        "free": format_bytes(usage.free),
        "percent": round(usage.used / usage.total * 100, 1),
    }

def io():
    """
    Measure disk utilization over the given interval.

    Returns:
        A dictionary mapping physical disk names to utilization percentages.

    Example:
        {
            "nvme0n1": 3.4,
            "sda": 0.0,
        }
    """
    start = psutil.disk_io_counters(perdisk=True)
    timelib.sleep(0.5)
    end = psutil.disk_io_counters(perdisk=True)

    utilization: dict[str, float] = {}

    elapsed_ms = 0.5 * 1000

    for device, end_stats in end.items():
        if not is_physical_disk(device):
            continue

        start_stats = start.get(device)
        if start_stats is None:
            continue

        if start_stats.busy_time is None or end_stats.busy_time is None:
            continue

        busy_ms = end_stats.busy_time - start_stats.busy_time
        percent = min(100.0, busy_ms * 100 / elapsed_ms)

        utilization[device] = round(percent, 1)

    return utilization