import subprocess

from .types import Failed, Ok, Rejected, Result


def window_action(action: str, target: str | None = None) -> Result:
    if action == "close":
        cmd = ["hyprctl", "dispatch", "closewindow", "active"]

    elif action == "fullscreen":
        cmd = ["hyprctl", "dispatch", "fullscreen", "1"]

    elif action == "focus":
        if target is None:
            return Rejected("window_action", "focus needs a target", "bad_args")
        cmd = ["hyprctl", "dispatch", "focuswindow", target]

    else:
        return Rejected("window_action", f"bad action {action!r}", "invalid_value")

    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        return Failed("window_action", f"{cmd[0]} not found")
    return Ok("window_action", f"window {action}")
