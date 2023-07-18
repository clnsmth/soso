"""Test the strategy interface."""

from soso.interface import StrategyInterface


def test_interface_has_methods(interface_methods):
    """Test that the StrategyInterface class has the expected methods."""
    for method in interface_methods:
        assert hasattr(StrategyInterface, method)