"""Test additional EML module functions and methods."""

from importlib import resources
from lxml import etree
from soso.strategies.eml import (
    get_content_url,
    get_content_size,
    convert_single_date_time_type,
    convert_range_of_dates,
    get_spatial_type,
    get_point,
    get_elevation,
    get_box,
    get_polygon,
    convert_user_id,
    get_data_entity_encoding_format,
    get_person_or_organization,
    get_encoding_format,
    EML,
    get_methods,
    get_checksum,
)
from soso.utilities import get_example_metadata_file_path


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

    # Negative case: If the "url" element is not present, the function will
    # return None.
    xml_content = """
    <root>
        <distribution>
            <online>
            </online>
        </distribution>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert get_content_url(root) is None


def test_get_content_size_returns_expected_value():
    """Test that the get_content_size function returns the expected value."""
    # Positive case: If the "unit" attribute of the "size" element is defined,
    # it will be appended to the content size value.
    xml_content = """
    <root>
        <physical>
            <size unit="kilobytes">10</size>
        </physical>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert get_content_size(root) == "10 kilobytes"
    # Negative case: If size element is not present, the function will return
    # None.
    xml_content = """
    <root>
        <physical>
        </physical>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert get_content_size(root) is None

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

    # If the "size" value is missing the function will return None, even if the
    # "unit" attribute is present.
    xml_content = """
    <root>
        <physical>
            <size unit="kilobytes"></size>
        </physical>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert get_content_size(root) is None


def test_convert_single_date_time_type_returns_expected_type():
    """Test that the convert_single_date_time_type function returns the
    expected type."""
    # If the "alternativeTimeScale" element is present, and both the
    # timeScaleAgeEstimate and timeScaleAgeUncertainty elements are numeric,
    # function will return a dictionary.
    xml_content = """
    <root>
        <alternativeTimeScale>
            <timeScaleName>Absolute Geologic Time Scale</timeScaleName>
            <timeScaleAgeEstimate>300</timeScaleAgeEstimate>
            <timeScaleAgeUncertainty>5</timeScaleAgeUncertainty>
        </alternativeTimeScale>
    </root>
    """
    root = etree.fromstring(xml_content)
    res = convert_single_date_time_type(root)
    assert isinstance(res, dict)

    # If the "alternativeTimeScale" element is not present, the function will
    # return a string. Add text for test merge.
    xml_content = """
    <root>
        <calendarDate>2019-01-01</calendarDate>
        <time>12:00:00</time>
    </root>
    """
    root = etree.fromstring(xml_content)
    res = convert_single_date_time_type(root)
    assert isinstance(res, str)

    # Negative case: If the single_date_time element is not present, the
    # function will return None.
    xml_content = """
    <root>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert convert_single_date_time_type(root) is None

    # Negative case: If the timeScaleAgeEstimate or timeScaleAgeUncertainty
    # elements are not numeric, the function will return None.
    # timescaleAgeEstimate is not numeric but timescaleAgeUncertainty is numeric
    xml_content = """
    <root>
        <alternativeTimeScale>
            <timeScaleName>Absolute Geologic Time Scale</timeScaleName>
            <timeScaleAgeEstimate>300 Ma</timeScaleAgeEstimate>
            <timeScaleAgeUncertainty>10</timeScaleAgeUncertainty>
        </alternativeTimeScale>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert convert_single_date_time_type(root) is None
    # timescaleAgeEstimate is numeric but timescaleAgeUncertainty is not numeric
    xml_content = """
        <root>
            <alternativeTimeScale>
                <timeScaleName>Absolute Geologic Time Scale</timeScaleName>
                <timeScaleAgeEstimate>300</timeScaleAgeEstimate>
                <timeScaleAgeUncertainty>+/- 10 Ma</timeScaleAgeUncertainty>
            </alternativeTimeScale>
        </root>
        """
    root = etree.fromstring(xml_content)
    assert convert_single_date_time_type(root) is None


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

    # Negative case: If the "beginDate" and "endDate" elements are not present
    # the function will return None.
    xml_content = """
    <root>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert convert_range_of_dates(root) is None


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
                <timeScaleAgeEstimate>300</timeScaleAgeEstimate>
                <timeScaleAgeUncertainty>5</timeScaleAgeUncertainty>
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


def test_get_spatial_type_returns_expected_value():
    """Test that the get_spatial_type function returns the expected value."""
    # The geographic coverage is a point if the north and south bounding
    # coordinates are equal and the east and west bounding coordinates are
    # equal.
    xml_content = """
    <root>
        <boundingCoordinates>
            <westBoundingCoordinate>10</westBoundingCoordinate>
            <eastBoundingCoordinate>10</eastBoundingCoordinate>
            <southBoundingCoordinate>20</southBoundingCoordinate>
            <northBoundingCoordinate>20</northBoundingCoordinate>
        </boundingCoordinates>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert get_spatial_type(root) == "Point"

    # The geographic coverage is a box if the north and south bounding
    # coordinates are not equal and the east and west bounding coordinates are
    # not equal.
    xml_content = """
    <root>
        <boundingCoordinates>
            <westBoundingCoordinate>10</westBoundingCoordinate>
            <eastBoundingCoordinate>20</eastBoundingCoordinate>
            <southBoundingCoordinate>10</southBoundingCoordinate>
            <northBoundingCoordinate>20</northBoundingCoordinate>
        </boundingCoordinates>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert get_spatial_type(root) == "Box"

    # The geographic coverage is a polygon if the gRing element is present and
    # contains a string.
    xml_content = """
    <root>
        <datasetGPolygon>
              <datasetGPolygonOuterGRing>
                <gRing>12.453,15.0 5,101 -111,45</gRing>
              </datasetGPolygonOuterGRing>
        </datasetGPolygon>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert get_spatial_type(root) == "Polygon"

    # Negative case: If the boundingCoordinates element is not present, and the
    # datasetGPolygon element is not present, the function will return None.
    xml_content = """
    <root>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert get_spatial_type(root) is None


def test_get_point_returns_expected_value_and_type():
    """Test that the get_point function returns the value as a dictionary."""
    # The function will return a dictionary with the latitude and longitude
    # values.
    xml_content = """
    <root>
        <boundingCoordinates>
            <westBoundingCoordinate>10</westBoundingCoordinate>
            <eastBoundingCoordinate>10</eastBoundingCoordinate>
            <southBoundingCoordinate>20</southBoundingCoordinate>
            <northBoundingCoordinate>20</northBoundingCoordinate>
        </boundingCoordinates>
    </root>
    """
    root = etree.fromstring(xml_content)
    res = get_point(root)
    assert isinstance(res, dict)
    assert res["latitude"] == "20"
    assert res["longitude"] == "10"

    # The function will return elevation if it is present.
    xml_content = """
    <root>
        <boundingCoordinates>
            <westBoundingCoordinate>10</westBoundingCoordinate>
            <eastBoundingCoordinate>10</eastBoundingCoordinate>
            <southBoundingCoordinate>20</southBoundingCoordinate>
            <northBoundingCoordinate>20</northBoundingCoordinate>
            <boundingAltitudes>
                <altitudeMinimum>100</altitudeMinimum>
                <altitudeMaximum>100</altitudeMaximum>
                <altitudeUnits>meter</altitudeUnits>
            </boundingAltitudes>
        </boundingCoordinates>
    </root>
    """
    root = etree.fromstring(xml_content)
    res = get_point(root)
    assert res["elevation"] == "100 meter"

    # Negative case: If the boundingCoordinates element is not present, the
    # function will return None.
    xml_content = """
    <root>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert get_point(root) is None


def test_get_elevation_returns_value_and_type():
    """Test that the get_elevation function returns the expected value as a
    string."""
    # The function will return a string with the elevation value if the
    # altitude values are equal.
    xml_content = """
    <root>
        <boundingCoordinates>
            <boundingAltitudes>
                <altitudeMinimum>100</altitudeMinimum>
                <altitudeMaximum>100</altitudeMaximum>
            </boundingAltitudes>
        </boundingCoordinates>
    </root>
    """
    root = etree.fromstring(xml_content)
    res = get_elevation(root)
    assert res == "100"

    # The function will return a string with the elevation value and units if
    # the altitude values are equal and the units are present.
    xml_content = """
    <root>
        <boundingCoordinates>
            <boundingAltitudes>
                <altitudeMinimum>100</altitudeMinimum>
                <altitudeMaximum>100</altitudeMaximum>
                <altitudeUnits>meter</altitudeUnits>
            </boundingAltitudes>
        </boundingCoordinates>
    </root>
    """
    root = etree.fromstring(xml_content)
    res = get_elevation(root)
    assert res == "100 meter"

    # The function will return None if the altitude values are not equal.
    xml_content = """
    <root>
        <boundingCoordinates>
            <boundingAltitudes>
                <altitudeMinimum>100</altitudeMinimum>
                <altitudeMaximum>200</altitudeMaximum>
            </boundingAltitudes>
        </boundingCoordinates>
    </root>
    """
    root = etree.fromstring(xml_content)
    res = get_elevation(root)
    assert res is None

    # Negative case: If the boundingCoordinates element is not present, the
    # function will return None.
    xml_content = """
    <root>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert get_elevation(root) is None


def test_get_box_returns_expected_value_and_type():
    """Test that the get_box function returns a dictionary with the expected
    value as a string."""
    # The function will return a dictionary, with the box field value as a
    # string with coordinates in the correct order (south, west, north, east)
    # and separated by spaces.
    xml_content = """
    <root>
        <boundingCoordinates>
            <westBoundingCoordinate>110</westBoundingCoordinate>
            <eastBoundingCoordinate>120</eastBoundingCoordinate>
            <southBoundingCoordinate>30</southBoundingCoordinate>
            <northBoundingCoordinate>40</northBoundingCoordinate>
        </boundingCoordinates>
    </root>
    """
    root = etree.fromstring(xml_content)
    res = get_box(root)
    assert isinstance(res, dict)
    assert res["box"] == "30 110 40 120"

    # Negative case: If the west, east, south, and north bounding coordinates
    # are not present, the function will return None.
    xml_content = """
    <root>
        <boundingCoordinates>
        </boundingCoordinates>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert get_box(root) is None


def test_get_polygon_returns_expected_value_and_type():
    """Test that the get_polygon function returns a dictionary with the
    expected value as a string."""
    # The function will return a dictionary, with the polygon value as a
    # string with coordinates in the correct order and separated by spaces.
    xml_content = """
    <root>
        <datasetGPolygon>
              <datasetGPolygonOuterGRing>
                <gRing>120,39 123,40 121,41 122,39 120,39</gRing>
              </datasetGPolygonOuterGRing>
        </datasetGPolygon>
    </root>
    """
    root = etree.fromstring(xml_content)
    res = get_polygon(root)
    assert isinstance(res, dict)
    assert res["polygon"] == "39 120 40 123 41 121 39 122 39 120"

    # The function will ensure that the first and last latitude/longitude
    # pairs are the same.
    xml_content = """
    <root>
        <datasetGPolygon>
              <datasetGPolygonOuterGRing>
                <gRing>120,39 123,40 121,41 122,39</gRing>
              </datasetGPolygonOuterGRing>
        </datasetGPolygon>
    </root>
    """
    root = etree.fromstring(xml_content)
    res = get_polygon(root)
    assert res["polygon"] == "39 120 40 123 41 121 39 122 39 120"

    # Negative case: If the gRing element is not present, the function will
    # return None.
    xml_content = """
    <root>
        <datasetGPolygon>
                <datasetGPolygonOuterGRing>
                </datasetGPolygonOuterGRing>
        </datasetGPolygon>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert get_polygon(root) is None


def test_convert_user_id_returns_value_and_type():
    """Test that the convert_user_id function returns the expected value and
    type."""
    # The function will return a dictionary formatted as a
    # schema:PropertyValue type.
    xml_content = """
    <userId directory="ORCID">https://orcid.org/0000-0002-6091-xxxx</userId>
    """
    root = etree.fromstring(xml_content)
    res = convert_user_id([root])  # requires element to be in a list
    assert isinstance(res, dict)
    assert res["@type"] == "PropertyValue"
    assert res["propertyID"] == "ORCID"
    assert res["value"] == "https://orcid.org/0000-0002-6091-xxxx"

    # Negative case: If the "userId" element is not present, the function will
    # return None.
    assert convert_user_id([]) is None


def test_get_data_entity_encoding_format_returns_value_and_type():
    """Test that the get_data_entity_encoding_format function returns the
    expected value as a string."""
    xml_content = """
    <root>
        <physical>
            <objectName>data_file.csv</objectName>
        </physical>
    </root>
    """
    root = etree.fromstring(xml_content)
    res = get_data_entity_encoding_format(root)
    assert isinstance(res, str)
    assert res == "text/csv"

    # Negative case: If the "objectName" element is not present, the function
    # will return None.
    xml_content = """
    <root>
        <physical>
        </physical>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert get_data_entity_encoding_format(root) is None


def test_get_person_or_organization_returns_value_and_type():
    """Test that the get_person function returns the expected value and
    type."""
    # The function will return a dictionary formatted as a schema:Person type
    # if the "individualName" element is present.
    xml_content = """
    <root>
        <individualName>
            <givenName>givenName</givenName>
            <surName>surName</surName>
        </individualName>
        <onlineUrl>https://organization.org/</onlineUrl>
        <userId directory="ORCID">https://orcid.org/0000-0002-6091-xxxx</userId>
    </root>"""
    root = etree.fromstring(xml_content)
    res = get_person_or_organization(root)
    assert isinstance(res, dict)
    assert res["@type"] == "Person"

    # The function will return a dictionary formatted as a schema:Organization
    # type if the "individualName" element is not present.
    xml_content = """
    <root>
        <organizationName>An Organization</organizationName>
        <userId directory="ROR">https://ror.org/xxxx</userId>
    </root>"""
    root = etree.fromstring(xml_content)
    res = get_person_or_organization(root)
    assert isinstance(res, dict)
    assert res["@type"] == "Organization"


def test_get_encoding_format():
    """Test that the get_encoding_format function returns the expected
    value."""
    eml = EML(file=get_example_metadata_file_path("EML"))
    res = get_encoding_format(metadata=eml.metadata)
    expected = ["application/xml", "https://eml.ecoinformatics.org/eml-2.2.0"]
    assert res == expected


def test_get_methods():
    """Test that the get_methods function returns the expected value."""
    # Strings are returned if the "methods" element is present.
    xml_content = """
    <root>
        <methods>
            <methodStep>
                <description>Step 1</description>
            </methodStep>
            <methodStep>
                <description>Step 2</description>
            </methodStep>
        </methods>
    </root>
    """
    root = etree.fromstring(xml_content)
    expected = "Step 1\n            \n            \n                Step 2"
    assert get_methods(root) == expected

    # None is returned if the "methods" element is not present.
    xml_content = """
    <root>
        <other_element>Content</other_element>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert get_methods(root) is None


def test_get_checksum():
    """Test that the get_checksum function returns the expected value."""

    # Recognized checksum algorithms are returned as a list of dict.
    xml_content = """
        <root>
            <physical>
                <authentication method="https://spdx.org/rdf/terms/#checksumAlgorithm_sha256">123456789</authentication>
            </physical>
        </root>"""
    root = etree.fromstring(xml_content)
    assert isinstance(get_checksum(root), list)
    assert len(get_checksum(root)) != 0

    # Unrecognized checksum algorithms are not returned.
    xml_content = """
    <root>
        <physical>
            <authentication method="MD5">123456789</authentication>
        </physical>
    </root>"""
    root = etree.fromstring(xml_content)
    assert get_checksum(root) is None

    # Missing checksum algorithms are not returned.
    xml_content = """
        <root>
            <physical>
                <authentication>123456789</authentication>
            </physical>
        </root>"""
    root = etree.fromstring(xml_content)
    assert get_checksum(root) is None

    # Multiple recognized checksum algorithms are returned as a list of dict.
    xml_content = """
    <root>
        <physical>
            <authentication method="https://spdx.org/rdf/terms/#checksumAlgorithm_sha256">123456789</authentication>
            <authentication method="https://spdx.org/rdf/terms/#checksumAlgorithm_md5">123456789</authentication>
        </physical>
    </root>"""
    root = etree.fromstring(xml_content)
    assert isinstance(get_checksum(root), list)
    assert len(get_checksum(root)) == 2

    # Negative case: If the "authentication" element is not present, the function
    # will return None.
    xml_content = """
    <root>
        <physical>
        </physical>
    </root>
    """
    root = etree.fromstring(xml_content)
    assert get_checksum(root) is None


def test_eml_file_input_must_be_xml():
    """Test that the EML() class raises an error if the file input is not XML."""
    not_xml = resources.files("soso.data").joinpath("soso-eml.sssom.tsv")
    try:
        EML(file=not_xml)
    except ValueError as error:
        assert "must be an XML file" in str(error)
