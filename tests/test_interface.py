"""Test the strategy interface.

Test for the presence of strategy features, i.e. specific attributes, and
methods.
"""

from soso.interface import StrategyInterface


def test_interface_has_metadata_attribute():
    """Test that the StrategyInterface class has a metadata attribute."""
    assert hasattr(StrategyInterface(), "metadata")


def test_interface_has_file_attribute():
    """Test that the StrategyInterface class has a file attribute."""
    assert hasattr(StrategyInterface(), "file")


def test_interface_has_kwargs_attribute():
    """Test that the StrategyInterface class has a kwargs attribute."""
    assert hasattr(StrategyInterface(), "kwargs")


def test_interface_has_methods(interface_methods):
    """Test that the StrategyInterface class has the expected methods."""
    for method in interface_methods:
        assert hasattr(StrategyInterface, method)
