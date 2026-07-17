import subprocess

def window_action(action: str, target: str | None = None):
    if action == "close":
        cmd = ["hyprctl", "dispatch", "closewindow", "active"]

    elif action == "fullscreen":
        cmd = ["hyprctl", "dispatch", "fullscreen", "1"]

    elif action == "focus":
        if target is None:
            return "rejected: focus needs a target"
        cmd = ["hyprctl", "dispatch", "focuswindow", target]

    else:
        return f"rejected: bad action {action!r}"

    subprocess.run(cmd, check=True)

    return f"ok: window {action}"
