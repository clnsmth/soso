"""The ISO 19115-1 strategy module."""

from soso.interface import StrategyInterface


class ISO19115(StrategyInterface):
    """Define the strategy for ISO 19115."""

    def set_name(self):
        return "name from ISO19115"

    def set_description(self):
        return "description from ISO19115"
