"""Test additional EML module functions and methods."""

from lxml import etree
from soso.strategies.eml import (
    get_content_url,
    get_content_size,
    convert_single_date_time_type,
    convert_range_of_dates,
)


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


def test_convert_single_date_time_type_returns_expected_type():
    """Test that the convert_single_date_time_type function returns the
    expected type."""
    # If the "alternativeTimeScale" element is present, the function will
    # return a dictionary.
    xml_content = """
    <root>
        <alternativeTimeScale>
            <timeScaleName>Absolute Geologic Time Scale</timeScaleName>
            <timeScaleAgeEstimate>300 Ma</timeScaleAgeEstimate>
            <timeScaleAgeUncertainty>+/- 5 Ma</timeScaleAgeUncertainty>
        </alternativeTimeScale>
    </root>
    """
    root = etree.fromstring(xml_content)
    res = convert_single_date_time_type(root)
    assert isinstance(res, dict)

    # If the "alternativeTimeScale" element is not present, the function will
    # return a string.
    xml_content = """
    <root>
        <calendarDate>2019-01-01</calendarDate>
        <time>12:00:00</time>
    </root>
    """
    root = etree.fromstring(xml_content)
    res = convert_single_date_time_type(root)
    assert isinstance(res, str)


def test_convert_range_of_dates_returns_expected_type():
    """Test that the convert_range_of_dates function returns the expected
    type."""
    # If the "alternativeTimeScale" element is present, the function will
    # return a dictionary.
    xml_content = """
    <root>
        <beginDate>
            <alternativeTimeScale>
                <timeScaleName>Absolute Geologic Time Scale</timeScaleName>
                <timeScaleAgeEstimate>300 Ma</timeScaleAgeEstimate>
                <timeScaleAgeUncertainty>+/- 5 Ma</timeScaleAgeUncertainty>
            </alternativeTimeScale>
        </beginDate>
        <endDate>
            <alternativeTimeScale>
                <timeScaleName>Absolute Geologic Time Scale</timeScaleName>
                <timeScaleAgeEstimate>700 Ma</timeScaleAgeEstimate>
                <timeScaleAgeUncertainty>+/- 5 Ma</timeScaleAgeUncertainty>
            </alternativeTimeScale>
        </endDate>
    </root>
    """
    root = etree.fromstring(xml_content)
    res = convert_range_of_dates(root)
    assert isinstance(res, dict)

    # If the "alternativeTimeScale" element is not present, the function will
    # return a string.
    xml_content = """
    <root>
        <beginDate>
            <calendarDate>2019-01-01</calendarDate>
            <time>12:00:00</time>
        </beginDate>
        <endDate>
            <calendarDate>2020-01-01</calendarDate>
            <time>12:00:00</time>
        </endDate>
    </root>
    """
    root = etree.fromstring(xml_content)
    res = convert_range_of_dates(root)
    assert isinstance(res, str)


def test_convert_single_date_time_returns_expected_type():
    """Test that the convert_single_date_time function returns the expected
    type."""
    # If the "alternativeTimeScale" element is present, the function will
    # return a dictionary.
    xml_content = """
    <root>
        <singleDateTime>
            <alternativeTimeScale>
                <timeScaleName>Absolute Geologic Time Scale</timeScaleName>
                <timeScaleAgeEstimate>300 Ma</timeScaleAgeEstimate>
                <timeScaleAgeUncertainty>+/- 5 Ma</timeScaleAgeUncertainty>
            </alternativeTimeScale>
        </singleDateTime>
    </root>
    """
    root = etree.fromstring(xml_content)
    res = convert_single_date_time_type(root)
    assert isinstance(res, dict)

    # If the "alternativeTimeScale" element is not present, the function will
    # return a string.
    xml_content = """
    <root>
        <singleDateTime>
            <beginDate>
                <calendarDate>2019-01-01</calendarDate>
                <time>12:00:00</time>
            </beginDate>
        </singleDateTime>
    </root>
    """
    root = etree.fromstring(xml_content)
    res = convert_single_date_time_type(root)
    assert isinstance(res, str)
