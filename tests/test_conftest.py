"""Test the test configuration."""

from tests.conftest import is_url
from tests.conftest import is_property_type
from tests.conftest import is_not_null


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
        assert is_property_type({"@type": thing}, expected_types=[thing])
    for thing in things:
        assert (
            is_property_type(results={"@type": thing}, expected_types=["schema:Text"])
            is False
        )


def test_is_property_type_returns_true_for_subsets():
    """Test that the is_property_type function returns True if the type is a
    subset of the expected types."""
    things = ["schema:Text", "schema:DefinedTerm"]
    assert is_property_type(
        results={"@type": "schema:DefinedTerm"}, expected_types=things
    )
    assert is_property_type("some text", expected_types=things)


def test_is_not_null_for_dictionaries():
    """Test that the is_not_null function returns True for non-empty
    dictionaries, and False otherwise."""

    # Single non-null dictionaries should pass
    res = {"@type": "schema:Text", "name": "some text"}
    assert is_not_null(res)
    res = {"@type": "schema:Text", "@id": "https://example.com"}
    assert is_not_null(res)
    res = {"@id": "https://example.com"}
    assert is_not_null(res)

    # Single dictionary w/some null results should pass
    res = {"@type": "schema:Text", "name": "some text", "description": ""}
    assert is_not_null(res)

    # List of non-null dictionaries should pass
    res = [
        {"@type": "schema:Text", "name": "some text"},
        {"@type": "schema:Text", "@id": "https://example.com"},
        {"@id": "https://example.com"},
    ]
    assert is_not_null(res)
    res = [
        {"name": ""},  # even when one is null
        {"@type": "schema:Text", "@id": "https://example.com"},
        {"@id": "https://example.com"},
    ]
    assert is_not_null(res)

    # Single null dictionaries should fail
    res = {"@type": "schema:Text"}  # once @type is removed, nothing is left
    assert is_not_null(res) is False
    res = {"@type": "schema:Text", "@id": ""}
    assert is_not_null(res) is False

    # List of null dictionaries should fail
    res = [
        {"@type": "schema:Text", "name": ""},
        {"@type": "schema:Text", "@id": ""},
        {"@id": ""},
    ]
    assert is_not_null(res) is False


def test_is_not_null_for_non_dictionaries():
    """Test that the is_not_null function returns True for non-null results,
    and False otherwise."""
    # Non-null results should pass
    assert is_not_null("some text")  # schema:Text
    assert is_not_null("https://example.com")  # schema:URL
    assert is_not_null(123)  # schema:Number
    assert is_not_null(True)  # schema:Boolean
    assert is_not_null(["some text"])  # List
    # Null results should fail
    assert is_not_null("") is False  # schema:Text & schema:URL
    assert is_not_null(None) is False  # schema:Number & schema:Boolean
    assert is_not_null([]) is False  # List
