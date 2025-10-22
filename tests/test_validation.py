"""For testing the validation module."""

import warnings
from pathlib import Path
import pytest
from soso.validation.core import (
    validate,
    get_shacl_file_path,
    resolve_shacl_shape,
)


@pytest.fixture(name="shacl_file_path")
def temp_shacl_file(tmp_path):
    """Create a temporary `.ttl` SHACL file and yield its path.

    Writes a minimal SHACL NodeShape to a temporary file (suffix `.ttl`),
    yields the file path to the test, and relies on pytest's `tmp_path` for cleanup.
    """
    file_path = tmp_path / "temp_shape.ttl"
    file_path.write_text(
        """
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        @prefix ex: <http://example.org/> .

        ex:DatasetShape
            a sh:NodeShape ;
            sh:targetClass ex:Dataset .
        """
    )
    yield str(file_path)


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


def test_resolve_shacl_shape_bundled():
    """Should resolve to a path for the bundled shape"""
    shape_path = resolve_shacl_shape("soso_common_v1.2.3.ttl")
    assert "soso_common_v1.2.3.ttl" in shape_path


def test_resolve_shacl_shape_local(shacl_file_path):
    """Should resolve to the local file path"""
    shape_path = resolve_shacl_shape(shacl_file_path)
    assert shape_path == shacl_file_path


def test_resolve_shacl_shape_missing_raises_file_not_found():
    """Should raise FileNotFoundError for a non-existent resource"""
    with pytest.raises(FileNotFoundError):
        resolve_shacl_shape("this_shape_does_not_exist.ttl")
