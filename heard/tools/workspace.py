import subprocess

def workspace_switch(number: int):
    if not 1 <= number <= 10:
        return f"rejected: workspace number {number} out of range (1-10)"

    cmd = ["hyprctl", "dispatch", "workspace", str(number)]
    subprocess.run(cmd, check=True)

    return f"ok: workspace {number}"
