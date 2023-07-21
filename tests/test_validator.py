"""For testing the validator module."""

import warnings
import pytest
from soso.validator import validate


def test_validate_returns_warning_when_invalid():
    """Test validate returns a warning when the graph is invalid."""
    with pytest.warns(UserWarning, match="Validation Report"):
        validate("tests/incomplete.jsonld")


def test_validate_returns_no_warning_when_valid():
    """Test validate returns no warning when the graph is valid."""
    with warnings.catch_warnings(record=True) as w:
        validate("tests/full.jsonld")
        for warning in w:
            assert not issubclass(warning.category, UserWarning)


def test_validate_returns_true_when_valid():
    """Test validate returns True when the graph is valid."""
    assert validate("tests/full.jsonld") is True


def test_validate_returns_false_when_invalid():
    """Test validate returns False when the graph is invalid."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert validate("tests/incomplete.jsonld") is False
