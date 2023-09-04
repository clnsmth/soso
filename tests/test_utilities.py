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
