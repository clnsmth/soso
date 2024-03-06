"""Test the test configuration."""

from tests.conftest import is_url
from tests.conftest import is_property_type


def test_is_url():
    """Test that the is_url function returns True for valid URLs."""
    assert is_url("https://example.com")
    assert is_url("http://example.com")
    assert is_url("ftp://example.com")
    assert is_url("https://example.com/path")
    assert is_url("https://example.com/path/")
    assert is_url("example.com") is False
    assert is_url("example.com/path") is False


def test_is_property_type_for_expected_datatypes():
    """Test that the is_property_type function returns True for expected
    DataTypes and False otherwise."""
    # schema:Text
    assert is_property_type("Some text", ["schema:Text"])
    assert is_property_type(123, ["schema:Text"]) is False
    # schema:URL
    assert is_property_type("https://example.com", ["schema:URL"])
    assert is_property_type("example.com", ["schema:URL"]) is False
    # schema:Number
    assert is_property_type(123, ["schema:Number"])
    assert is_property_type(123.4, ["schema:Number"])
    assert is_property_type("123", ["schema:Number"]) is False
    # schema:Boolean
    assert is_property_type(True, ["schema:Boolean"])
    assert is_property_type(False, ["schema:Boolean"])
    assert is_property_type("123", ["schema:Boolean"]) is False
    # Works for a list of possible DataTypes
    datatypes = ["schema:Number", "schema:Boolean", "schema:Text"]
    assert is_property_type(123, datatypes)


def test_is_property_type_for_expected_things():
    """Test that the is_property_type function returns True for expected
    Things and False otherwise."""
    things = [
        "schema:DefinedTerm",
        "schema:PropertyValue",
        "schema:DataCatalog",
        "schema:DataDownload",
        "time:ProperInterval",
        "time:Instant",
        "schema:Place",
        "schema:Person",
        "schema:Organization",
        "schema:MonetaryGrant",
    ]
    for thing in things:
        assert is_property_type({"@type": thing}, expected_type=[thing])
    for thing in things:
        assert (
            is_property_type({"@type": thing}, expected_type=["schema:Text"]) is False
        )


def test_is_property_type_returns_true_for_subsets():
    """Test that the is_property_type function returns True if the type is a
    subset of the expected types."""
    things = ["schema:Text", "schema:DefinedTerm"]
    assert is_property_type({"@type": "schema:DefinedTerm"}, expected_type=things)
    assert is_property_type("some text", expected_type=things)
