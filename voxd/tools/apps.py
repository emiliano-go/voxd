import subprocess
from pathlib import Path

from .helpers.apps import app_exists


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