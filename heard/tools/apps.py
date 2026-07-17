import subprocess

from .helpers.apps import app_exists
from .types import Ok, Rejected, Result


def launch_app(app: str) -> Result:
    if not app_exists(app):
        return Rejected("launch_app", f"no such app {app!r}", "declined")
    try:
        subprocess.Popen(
            ["uwsm", "app", "--", app],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return Ok("launch_app", f"launched {app}")
    except FileNotFoundError:
        return Rejected("launch_app", "uwsm not found", "declined")
