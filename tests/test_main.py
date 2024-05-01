"""Test the converter."""

from json import loads
from soso.main import convert
from soso.utilities import get_example_metadata_file_path
from tests.conftest import get_kwargs


def test_convert_returns_str(strategy_names):
    """Test that the convert function returns a string."""
    for strategy in strategy_names:
        res = convert(file=get_example_metadata_file_path(strategy), strategy=strategy)
        assert isinstance(res, str)


def test_convert_returns_json(strategy_names):
    """Test that the convert function returns valid JSON."""
    for strategy in strategy_names:
        res = convert(
            file=get_example_metadata_file_path(strategy),
            strategy=strategy,
            **get_kwargs(strategy)
        )
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


def test_convert_verify_strategy_results(strategy_names):
    """Test that the convert function returns the expected results by comparing
    them with a snapshot of the expected results.

    Note, this snapshot requires updating if the strategy's results change."""
    for strategy in strategy_names:
        with open("tests/data/" + strategy + ".json", "r", encoding="utf-8") as file:
            expected_results = file.read()
            res = convert(
                file=get_example_metadata_file_path(strategy),
                strategy=strategy,
                **get_kwargs(strategy)
            )
            assert res == expected_results
