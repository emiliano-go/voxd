import subprocess

STEP = "5%"

def volume_control(action, amount=None):
    sink = "@DEFAULT_AUDIO_SINK@"

    if action == "up":
        cmd = ["wpctl", "set-volume", sink, f"{STEP}+"]

    elif action == "down":
        cmd = ["wpctl", "set-volume", sink, f"{STEP}-"]
    
    elif action == "mute":
        cmd = ["wpctl", "set-mute", sink, "1"]      # 1 = mute, 0 = unmute
    
    elif action == "set":
    
        if amount is None:
            return f"rejected: set needs amount"
    
        cmd = ["wpctl", "set-volume", sink, f"{int(amount)}%"]
    
    else:
        return f"rejected: bad action {action!r}"

    subprocess.run(cmd, check=True)
    
    return f"ok: volume {action}"