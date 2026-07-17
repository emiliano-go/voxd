import subprocess

def media_control(action : str):

    if action == "play":
        cmd = ["playerctl", "play"]
    
    elif action == "pause":
        cmd = ["playerctl", "pause"]
    
    elif action == "next":
        cmd = ["playerctl", "next"]

    elif action == "previous":
        cmd = ["playerctl", "previous"]

    else:
        return f"rejected: bad action {action!r}"  
    
    subprocess.run(cmd, check=True)

    return f"ok: media {action}"