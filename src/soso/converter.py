"""The converter module."""

from soso.strategies.eml import EML
from soso.strategies.iso19115 import ISO19115


def convert(strategy):
    """Return SOSO markup for a metadata document and specified strategy."""

    # Load the strategy based on user choice
    if strategy == "eml":
        strategy = EML()
    elif strategy == "iso19115":
        strategy = ISO19115()
    else:
        raise ValueError("Invalid choice!")

    # Build the graph
    res = {"name": strategy.set_name(), "description": strategy.set_description()}
    return res
