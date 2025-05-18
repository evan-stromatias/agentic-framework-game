from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def get_version() -> str:
    try:
        return version("game")
    except PackageNotFoundError:
        try:
            return (Path(__file__).parent.parent / "version.txt").read_text().strip()
        except FileNotFoundError:
            return "unknown"


__version__ = get_version()
