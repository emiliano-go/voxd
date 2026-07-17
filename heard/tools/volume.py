import subprocess

from .types import Failed, Ok, Rejected, Result

STEP = "5%"


def volume_control(action: str, amount: str | None = None) -> Result:
    sink = "@DEFAULT_AUDIO_SINK@"

    if action == "up":
        cmd = ["wpctl", "set-volume", sink, f"{STEP}+"]

    elif action == "down":
        cmd = ["wpctl", "set-volume", sink, f"{STEP}-"]

    elif action == "mute":
        cmd = ["wpctl", "set-mute", sink, "1"]

    elif action == "set":
        if amount is None:
            return Rejected("volume_control", "set needs amount", "bad_args")
        cmd = ["wpctl", "set-volume", sink, f"{int(amount)}%"]

    else:
        return Rejected("volume_control", f"bad action {action!r}", "invalid_value")

    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        return Failed("volume_control", f"{cmd[0]} not found")
    return Ok("volume_control", f"volume {action}")
