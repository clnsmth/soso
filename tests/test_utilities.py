"""For testing the validator module."""

import warnings
from pathlib import PosixPath
import pytest
from pandas import DataFrame
from soso.utilities import validate
from soso.utilities import get_sssom_file_path
from soso.utilities import read_sssom
from soso.utilities import get_example_metadata_file_path
from soso.utilities import get_shacl_file_path

# from soso.utilities import remove_empty_values
# from soso.utilities import remove_empty_recursive
from soso.utilities import clean_jsonld
from soso.utilities import clean_jsonld_x2


@pytest.mark.internet_required
def test_validate_returns_warning_when_invalid(internet_connection):
    """Test validate returns a warning when the graph is invalid."""
    if not internet_connection:
        pytest.skip("Internet connection is not available.")
    with pytest.warns(UserWarning, match="Validation Report"):
        validate("tests/incomplete.jsonld")


@pytest.mark.internet_required
def test_validate_returns_no_warning_when_valid(internet_connection):
    """Test validate returns no warning when the graph is valid."""
    if not internet_connection:
        pytest.skip("Internet connection is not available.")
    with warnings.catch_warnings(record=True) as list_of_warnings:
        validate("tests/full.jsonld")
        for warning in list_of_warnings:
            assert not issubclass(warning.category, UserWarning)


@pytest.mark.internet_required
def test_validate_returns_true_when_valid(internet_connection):
    """Test validate returns True when the graph is valid."""
    if not internet_connection:
        pytest.skip("Internet connection is not available.")
    assert validate("tests/full.jsonld") is True


@pytest.mark.internet_required
def test_validate_returns_false_when_invalid(internet_connection):
    """Test validate returns False when the graph is invalid."""
    if not internet_connection:
        pytest.skip("Internet connection is not available.")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert validate("tests/incomplete.jsonld") is False


def test_get_sssom_file_path_returns_path(strategy_names):
    """Test that get_sssom_file_path returns a path for each strategy name.

    This ensures a SSSOM file exists for each strategy and that the path to
    each is valid."""
    for strategy in strategy_names:
        sssom_file_path = get_sssom_file_path(strategy)
        assert isinstance(sssom_file_path, PosixPath)


def test_read_sssom_returns_dataframe(strategy_names):
    """Test that read_sssom returns a dataframe.

    SSSOM files contain an extensive set of information and can become
    malformed during manual curation. This test is a very basic check on the
    format (i.e. can be read without error)."""
    for strategy in strategy_names:
        sssom = read_sssom(strategy)
        assert isinstance(sssom, DataFrame)


def test_get_example_metadata_file_path_returns_path(strategy_names):
    """Test that get_example_metadata returns a path."""
    for strategy in strategy_names:
        file_path = get_example_metadata_file_path(strategy=strategy)
        assert isinstance(file_path, PosixPath)


def test_get_shacl_file_path_returns_path():
    """Test that get_shacl_file_path returns a path."""
    file_path = get_shacl_file_path()
    assert isinstance(file_path, PosixPath)


def test_clean_jsonld_x2():
    """Test that clean_jsonld removes empty values from a JSON-LD object."""
    # Dictionary is empty / non-empty
    assert clean_jsonld_x2({}) is None  # FIXME Fails
    assert clean_jsonld_x2({"name": "John Doe"}) == {"name": "John Doe"}

    # Dictionary only contains @type / has more than @type
    assert clean_jsonld_x2({"@type": "schema:Thing"}) is None  # FIXME Fails
    data = clean_jsonld_x2({"@type": "schema:Thing", "name": "John Doe"})
    expected = {"@type": "schema:Thing", "name": "John Doe"}
    assert data == expected

    # Nested dictionary is empty / non-empty
    data = {"address": {}}
    assert clean_jsonld_x2(data) is None  # FIXME Fails
    data = {"address": {"street": "123 Main St"}}
    expected = {"address": {"street": "123 Main St"}}
    assert clean_jsonld_x2(data) == expected

    # Nested dictionary only contains @type / has more than @type
    data = {"role": {"@type": "Role"}}
    assert clean_jsonld_x2(data) is None  # FIXME Fails
    data = {"role": {"@type": "Role", "name": "Manager"}}
    expected = {"role": {"@type": "Role", "name": "Manager"}}
    assert clean_jsonld_x2(data) == expected

    # List is empty / non-empty
    assert clean_jsonld_x2([]) is None  # FIXME Fails
    data = ["John Doe", 123, True]
    expected = ["John Doe", 123, True]
    assert clean_jsonld_x2(data) == expected

    # List contains empty dictionaries / non-empty dictionaries
    data = [{}, {}]
    assert clean_jsonld_x2(data) is None  # FIXME Fails
    data = [{"name": "John Doe"}, {"name": "Jane Doe"}]
    res = clean_jsonld_x2(data)
    expected = [{"name": "John Doe"}, {"name": "Jane Doe"}]
    set1 = {frozenset(item.items()) for item in res}
    set2 = {frozenset(item.items()) for item in expected}
    assert set1 == set2

    # List contains empty lists / non-empty lists
    data = [[], []]
    assert clean_jsonld_x2(data) is None  # FIXME Fails
    data = [["John Doe"], ["Jane Doe"]]
    expected = [["John Doe"], ["Jane Doe"]]
    assert clean_jsonld_x2(data) == expected

    # Text string is empty / non-empty
    # assert clean_jsonld("") is None  # FIXME Fails
    assert clean_jsonld_x2("John Doe") == "John Doe"

    # Number is non-empty
    assert clean_jsonld_x2(123) == 123

    # Boolean is non-empty
    assert clean_jsonld(True) is True

    # Value is None
    assert clean_jsonld(None) is None
