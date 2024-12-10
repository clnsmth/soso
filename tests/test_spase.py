"""Test additional SPASE module functions and methods."""

from lxml import etree
from soso.strategies.spase import get_schema_version
from soso.utilities import get_empty_metadata_file_path, get_example_metadata_file_path


def test_get_schema_version_returns_expected_value():
    """Test that the get_schema_version function returns the expected value."""

    # Positive case: The function will return the schema version of the EML
    # file.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_schema_version(spase) == "2.5.0"

    # Negative case: If the schema version is not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_schema_version(spase) is None
