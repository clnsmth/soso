"""For testing the validation module."""

from pathlib import Path
import pytest
from soso.validation import (
    validate,
    _get_shacl_file_path,
    _resolve_shacl_shape,
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


def test_get_shacl_file_path_returns_path():
    """Test that _get_shacl_file_path returns a path."""
    file_path = _get_shacl_file_path()
    assert isinstance(file_path, Path)


def test_resolve_shacl_shape_bundled():
    """Should resolve to a path for the bundled shape"""
    shape_path = _resolve_shacl_shape("soso_common_v1.2.3.ttl")
    assert "soso_common_v1.2.3.ttl" in shape_path


def test_resolve_shacl_shape_local(shacl_file_path):
    """Should resolve to the local file path"""
    shape_path = _resolve_shacl_shape(shacl_file_path)
    assert shape_path == shacl_file_path


def test_resolve_shacl_shape_missing_raises_file_not_found():
    """Should raise FileNotFoundError for a non-existent resource"""
    with pytest.raises(FileNotFoundError):
        _resolve_shacl_shape("this_shape_does_not_exist.ttl")


@pytest.mark.internet_required
def test_validate_with_bundled_shape():
    """Validate using a bundled SHACL shape."""
    bundled_shape = "soso_common_v1.2.3.ttl"
    shape_path = _resolve_shacl_shape(bundled_shape)
    result = validate("tests/incomplete.jsonld", shacl_graph=shape_path)
    assert isinstance(result, dict)
    assert result["shacl_graph"] == shape_path
    assert "conforms" in result


@pytest.mark.internet_required
def test_validate_with_default_shape():
    """Validate using the default bundled SHACL shape."""
    result = validate("tests/incomplete.jsonld", shacl_graph=None)
    assert "soso_common_v1.2.3.ttl" in result["shacl_graph"]
    assert isinstance(result, dict)
    assert "conforms" in result
