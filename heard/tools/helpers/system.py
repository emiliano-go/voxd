import re

def format_bytes(n: int) -> str:
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if n < 1024 or unit == "TiB":
            return f"{n:.1f} {unit}"
        n /= 1024

_PHYSICAL_DISK_RE = re.compile(
    r"^(?:sd[a-z]+|hd[a-z]+|vd[a-z]+|xvd[a-z]+|nvme\d+n\d+|mmcblk\d+)$"
)


def is_physical_disk(device: str) -> bool:
    """Return True if the device appears to be a physical disk."""
    return _PHYSICAL_DISK_RE.fullmatch(device) is not None
