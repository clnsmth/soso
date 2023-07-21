"""For package data related operations."""

from importlib import resources


def get_soso_common():
    """Get the path to the SOSO shape file

    Returns
    -------
    str
        Path to file.
    """
    with resources.path("soso.data", "soso_common_v1.2.3.ttl") as f:
        return f
