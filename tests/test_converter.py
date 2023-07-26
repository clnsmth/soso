"""Test the converter."""

from soso.converter import convert


def test_convert_returns_dict(strategy_names):
    """Test that the convert function returns a dictionary."""
    for strategy in strategy_names:
        res = convert(strategy=strategy)
        assert isinstance(res, dict)


def test_convert_returns_expected_properties(strategy_names, soso_properties):
    """Test that the convert function returns the expected properties/keys."""
    for strategy in strategy_names:
        res = convert(strategy=strategy)
        assert all(key in soso_properties for key in res)


def test_convert_returns_no_none_values(strategy_names):
    """Test that the convert function removes non-existent properties."""
    for strategy in strategy_names:
        res = convert(strategy=strategy)
        assert all(value is not None for value in res.values())
