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


def test_convert_verify_strategy_results(strategy_names):
    """Test that the convert function returns the expected results by comparing
    them with a snapshot of the expected results.

    Verification testing helps address gaps in our unit tests by verifying the
    consistency of inputs and outputs produced by the system. This mitigates
    the risk of unexpected deviations. We maintain a static snapshot of
    `main.convert` results (JSON-LD file) captured at the time of the most
    recent modification to a strategy and stored at
    `tests/data/[strategy].json`.
    Developers are responsible for updating this snapshot when changes occur
    and are reminded to manually inspect and validate the anticipated changes
    to this file before committing a new snapshot to the test suite."""
    for strategy in strategy_names:
        with open("tests/data/" + strategy + ".json", "r", encoding="utf-8") as file:
            expected_results = file.read()
            res = convert(
                file=get_example_metadata_file_path(strategy), strategy=strategy
            )
            assert res == expected_results


def test_convert_with_kwargs(soso_properties):
    """Test that the convert function returns the expected results when passed
    keyword arguments. All properties matching kwargs keys will be replaced
    with the kwargs values."""
    # Create test data, a dict of kwargs containing one entry for each SOSO
    # property. Exclude @context and @type, we don't want to change them.
    properties = [prop for prop in soso_properties if not prop.startswith("@")]
    kwargs = {prop: prop + "_via_kwargs" for prop in properties}
    res = convert(
        file=get_example_metadata_file_path("EML"),
        strategy="eml",
        **kwargs,
    )
    res = loads(res)
    for key, value in kwargs.items():
        assert res[key] == value

    # But it should not work in reverse. I.e. any kwargs not in the SOSO
    # properties should be ignored.
    res = convert(
        file=get_example_metadata_file_path("EML"),
        strategy="eml",
        **{"not_a_property": "value"},
    )
    res = loads(res)
    assert "not_a_property" not in res
