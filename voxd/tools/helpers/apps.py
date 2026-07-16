import shutil


def app_exists(app: str) -> bool:
    return shutil.which(app) is not None
