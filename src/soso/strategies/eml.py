"""The EML strategy module."""

from soso.interface import StrategyInterface


class EML(StrategyInterface):
    """Define the strategy for EML."""

    def set_name(self):
        """Set the dataset name property."""
        return "name from EML"

    def set_description(self):
        """Set the dataset description property."""
        return "description from EML"
