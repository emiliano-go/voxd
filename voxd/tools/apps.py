import subprocess
import shutil
from pathlib import Path


def app_exists(app: str) -> bool:
    return shutil.which(app) is not None


def launch_app(app : str):
    
    if not app_exists(app):
        return f"rejected: no such app {app!r}"
    try:
        subprocess.Popen(
            ["uwsm", "app", "--", app],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,      # detach: app survives voxd restarts
        )
        return f"ok: launched {app}"
    except FileNotFoundError:
        return f"rejected: uwsm not found"