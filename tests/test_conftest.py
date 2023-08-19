"""Test the test configuration."""

from tests.conftest import is_url


def test_is_url():
    """Test that the is_url function returns True for valid URLs."""
    assert is_url("https://example.com")
    assert is_url("http://example.com")
    assert is_url("ftp://example.com")
    assert is_url("https://example.com/path")
    assert is_url("https://example.com/path/")
    assert is_url("example.com") is False
    assert is_url("example.com/path") is False
