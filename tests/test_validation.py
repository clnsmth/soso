"""For testing the validation module."""

import warnings
from pathlib import Path
import pytest
from soso.validation.core import (
    validate,
    get_shacl_file_path,
)


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


def test_get_shacl_file_path_returns_path():
    """Test that get_shacl_file_path returns a path."""
    file_path = get_shacl_file_path()
    assert isinstance(file_path, Path)
