"""Test the strategies."""

from soso.interface import StrategyInterface


def test_strategy_inherits_strategy_interface(strategy_instance):
    """Test that each strategy inherits the StrategyInterface class."""
    assert isinstance(strategy_instance, StrategyInterface)


# SOSO properties are not universally shared across metadata dialects. In cases
# where a property is not available, the corresponding strategy method will
# return None. Therefore, each method test below first checks if the return
# value is not None before checking the type of the returned value. This
# approach allows for the flexibility of the SOSO guidelines while providing a
# consistent test suite.


def test_set_name_returns_str(strategy_instance):
    """Test that the set_name method returns a string."""
    res = strategy_instance.set_name()
    if res is not None:
        assert isinstance(res, str)


def test_set_description_returns_str(strategy_instance):
    """Test that the set_description method returns a string."""
    res = strategy_instance.set_description()
    if res is not None:
        assert isinstance(res, str)
