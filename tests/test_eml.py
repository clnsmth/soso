"""Test additional EML module functions and methods."""

from lxml import etree
from soso.strategies.eml import get_content_url, get_content_size


def test_get_content_url_returns_expected_value():
    """Test that the get_content_url function returns the expected value."""
    # If the "function" attribute of the "url" element is "information", the
    # function will return None.
    xml_content = """
    <root>
        <distribution>
            <online>
                <url function="information">https://example.data</url>
            </online>
        </distribution>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert get_content_url(root) is None

    # If the "function" attribute of the "url" element is not "information",
    # the function will return the value of the "url" element.
    xml_content = """
    <root>
        <distribution>
            <online>
                <url function="download">https://example.data</url>
            </online>
        </distribution>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert get_content_url(root) == "https://example.data"

    xml_content = """
    <root>
        <distribution>
            <online>
                <url>https://example.data</url>
            </online>
        </distribution>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert get_content_url(root) == "https://example.data"


def test_get_content_size_returns_expected_value():
    """Test that the get_content_size function returns the expected value."""
    # If the "unit" attribute of the "size" element is defined, it will be
    # appended to the content size value.
    xml_content = """
    <root>
        <physical>
            <size unit="kilobytes">10</size>
        </physical>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert get_content_size(root) == "10 kilobytes"

    # If the "unit" attribute of the "size" element is not defined, the content
    # size value will be returned as is.
    xml_content = """
    <root>
        <physical>
            <size>10</size>
        </physical>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert get_content_size(root) == "10"