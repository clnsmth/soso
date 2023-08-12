"""Test the converter."""

from json import loads
from soso.main import convert
from soso.utilities import get_example_metadata_file_path


def test_convert_returns_str(strategy_names):
    """Test that the convert function returns a string."""
    for strategy in strategy_names:
        res = convert(file=get_example_metadata_file_path(strategy), strategy=strategy)
        assert isinstance(res, str)


def test_convert_returns_json(strategy_names):
    """Test that the convert function returns valid JSON."""
    for strategy in strategy_names:
        res = convert(file=get_example_metadata_file_path(strategy), strategy=strategy)
        assert isinstance(loads(res), dict)


def test_convert_returns_context(strategy_names):
    """Test that the convert function returns a context."""
    for strategy in strategy_names:
        res = convert(file=get_example_metadata_file_path(strategy), strategy=strategy)
        assert "@context" in res


def test_convert_returns_expected_properties(strategy_names, soso_properties):
    """Test that the convert function returns the expected properties/keys."""
    for strategy in strategy_names:
        res = convert(file=get_example_metadata_file_path(strategy), strategy=strategy)
        assert all(key in soso_properties for key in loads(res))


def test_convert_returns_no_none_values(strategy_names):
    """Test that the convert function removes non-existent properties."""
    for strategy in strategy_names:
        res = convert(file=get_example_metadata_file_path(strategy), strategy=strategy)
        assert all(value is not None for value in loads(res).values())
