import subprocess

from .types import Failed, Ok, Rejected, Result


def workspace_switch(workspace: str) -> Result:
    try:
        n = int(workspace)
    except (ValueError, TypeError):
        return Rejected("workspace_switch", f"invalid workspace {workspace!r}", "invalid_value")

    if not 1 <= n <= 10:
        return Rejected("workspace_switch", f"workspace {n} out of range (1-10)", "invalid_value")

    cmd = ["hyprctl", "dispatch", "workspace", str(n)]
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        return Failed("workspace_switch", f"{cmd[0]} not found")

    return Ok("workspace_switch", f"workspace {n}")
