import subprocess

from .types import Failed, Ok, Rejected, Result


def media_control(action: str) -> Result:
    if action == "play":
        cmd = ["playerctl", "play"]

    elif action == "pause":
        cmd = ["playerctl", "pause"]

    elif action == "next":
        cmd = ["playerctl", "next"]

    elif action == "previous":
        cmd = ["playerctl", "previous"]

    else:
        return Rejected("media_control", f"bad action {action!r}", "invalid_value")

    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        return Failed("media_control", f"{cmd[0]} not found")
    return Ok("media_control", f"media {action}")
