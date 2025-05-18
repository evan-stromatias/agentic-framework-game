import re

from game import __version__


def test_version_format():
    """Tests the dynamically loaded package version works and it's using semantic versioning."""
    assert re.match(
        r"^\d+\.\d+\.\d+$", __version__
    ), f"Invalid version format: {__version__}"