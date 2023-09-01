"""The EML strategy module."""

from lxml import etree
from soso.interface import StrategyInterface


class EML(StrategyInterface):
    """Define the conversion strategy for EML (Ecological Metadata Language).

    Parameters
    ----------
    file : str
        The path to the metadata file. This should be an XML file in EML
        format.
    **kwargs : dict
        Additional keyword arguments that can be utilized to define SOSO
        properties that don't directly correspond to metadata fields. See
        Notes for more information.

    Notes
    -----
    Not all SOSO properties have a direct mapping to EML metadata. Such properties
    can be specified using `kwargs`, where the keys represent property names, and
    the values define the property types (provided as strings or dictionaries).
    Refer to the `SOSO guidelines <https://github.com/ESIPFed/science-on-schema.org/blob
    /master/guides/Dataset.md>`_ for detailed insights into each property.

    Unmappable properties:

    - url
    - sameAs
    - version
    - isAccessibleForFree
    - citation
    - includedInDataCatalog
    - subjectOf
    - potentialAction
    - dateCreated
    - expires
    - wasRevisionOf
    """

    def __init__(self, file, **kwargs):
        """Initialize the strategy."""
        super().__init__(metadata=etree.parse(file))
        self.kwargs = kwargs

    def get_name(self):
        name = self.metadata.xpath(".//dataset/title")
        return name[0].text

    def get_description(self):
        description = self.metadata.xpath(".//dataset/abstract")
        return description[0].text

    def get_url(self):
        url = self.kwargs.get("url")
        return url

    def get_same_as(self):
        same_as = self.kwargs.get("sameAs")
        return same_as

    def get_version(self):
        version = self.kwargs.get("version")
        return version

    def get_is_accessible_for_free(self):
        is_accessible_for_free = self.kwargs.get("isAccessibleForFree")
        return is_accessible_for_free

    def get_keywords(self):
        keywords = []
        for item in self.metadata.xpath(".//dataset/keywordSet/keyword"):
            keywords.append(item.text)
        for item in self.metadata.xpath(".//dataset/annotation/valueURI"):
            defined_term = {
                "@type": "DefinedTerm",
                "name": item.attrib["label"],
                "url": item.text,
            }
            keywords.append(defined_term)
        return keywords

    def get_identifier(self):
        identifier = self.metadata.xpath("@packageId")
        return identifier[0]

    def get_citation(self):
        citation = self.kwargs.get("citation")
        return citation

    def get_variable_measured(self):
        variable_measured = []
        for item in self.metadata.xpath(".//attributeList/attribute"):
            property_value = {
                "@type": "PropertyValue",
                "name": item.findtext("attributeName"),
                "alternateName": item.findtext("attributeLabel"),
                "propertyID": item.findtext(".//valueURI"),
                "description": item.findtext("attributeDefinition"),
                "unitText": item.findtext(".//standardUnit")
                or item.findtext(".//customUnit"),
                "minValue": item.findtext(".//minimum"),
                "maxValue": item.findtext(".//maximum"),
            }
            property_value = {
                key: value for key, value in property_value.items() if value is not None
            }
            variable_measured.append(property_value)
        return variable_measured

    def get_included_in_data_catalog(self):
        included_in_data_catalog = self.kwargs.get("includedInDataCatalog")
        return included_in_data_catalog

    def get_subject_of(self):
        subject_of = self.kwargs.get("subjectOf")
        return subject_of

    def get_distribution(self):
        distribution = []
        data_entities = [
            "dataTable",
            "spatialRaster",
            "spatialVector",
            "storedProcedure",
            "view",
            "otherEntity",
        ]
        for data_entity in data_entities:
            for item in self.metadata.xpath(f".//{data_entity}"):
                data_download = {
                    "@type": "DataDownload",
                    "name": item.findtext(".//entityName"),
                    "description": item.findtext(".//entityDescription"),
                    "contentSize": get_content_size(item),
                    "contentURL": get_content_url(item),
                }
                distribution.append(data_download)
        return distribution

    def get_potential_action(self):
        potential_action = self.kwargs.get("potentialAction")
        return potential_action

    def get_date_created(self):
        date_created = self.kwargs.get("dateCreated")
        return date_created

    def get_date_modified(self):
        date_modified = self.metadata.xpath(".//dataset/pubDate")
        return date_modified[0].text

    def get_date_published(self):
        date_published = self.metadata.xpath(".//dataset/pubDate")
        return date_published[0].text

    def get_expires(self):
        expires = self.kwargs.get("expires")
        return expires

    def get_temporal_coverage(self):
        range_of_dates = self.metadata.xpath(
            ".//dataset/coverage/temporalCoverage/rangeOfDates"
        )
        single_date_time = self.metadata.xpath(
            ".//dataset/coverage/temporalCoverage/singleDateTime"
        )
        if range_of_dates:
            temporal_coverage = convert_range_of_dates(range_of_dates[0])
        elif single_date_time:
            if len(single_date_time) > 1:
                # schema:temporalCoverage only allows one but EML may have
                # many. There is no reliable way to determine which is the
                # most relevant, so we return None.
                temporal_coverage = None
            else:
                temporal_coverage = convert_single_date_time(single_date_time[0])
        return temporal_coverage

    def get_spatial_coverage(self):
        geo = []
        for item in self.metadata.xpath(".//dataset/coverage/geographicCoverage"):
            object_type = get_spatial_type(item)
            if object_type == "Point":
                geo.append(get_point(item))
            elif object_type == "Box":
                geo.append(get_box(item))
            elif object_type == "Polygon":
                geo.append(get_polygon(item))
        spatial_coverage = {"@type": "Place", "geo": geo}
        return spatial_coverage

    def get_creator(self):
        creator = []
        creators = self.metadata.xpath(".//dataset/creator")
        for item in creators:
            res = {
                "@type": "Person",
                "honorificPrefix": item.findtext("individualName/salutation"),
                "givenName": item.findtext("individualName/givenName"),
                "familyName": item.findtext("individualName/surName"),
                "url": item.findtext("onlineUrl"),
                "identifier": convert_user_id(item.xpath("userId")),
            }
            creator.append(res)
        if len(creator) != 0:
            creator = {"@list": creator}  # to preserve order
        else:
            creator = None  # for readability
        return creator

    def get_contributor(self):
        contributor = []
        contributors = self.metadata.xpath(".//dataset/associatedParty")
        for item in contributors:
            res = {
                "@type": "Role",
                "roleName": item.findtext("role"),
                "contributor": {
                    "@type": "Person",
                    "honorificPrefix": item.findtext("individualName/salutation"),
                    "givenName": item.findtext("individualName/givenName"),
                    "familyName": item.findtext("individualName/surName"),
                    "url": item.findtext("onlineUrl"),
                    "identifier": convert_user_id(item.xpath("userId")),
                },
            }
            contributor.append(res)
        if len(contributor) != 0:
            contributor = {"@list": contributor}  # to preserve order
        else:
            contributor = None  # for readability
        return contributor

    def get_provider(self):
        provider = self.kwargs.get("provider")
        return provider

    def get_publisher(self):
        publisher = self.kwargs.get("publisher")
        return publisher

    def get_funding(self):
        funding = []
        for item in self.metadata.xpath(".//dataset/project/award"):
            res = {
                "@type": "MonetaryGrant",
                "identifier": item.findtext("awardNumber"),
                "name": item.findtext("title"),
                "url": item.findtext("awardUrl"),
                "funder": {
                    "@type": "Organization",
                    "name": item.findtext("funderName"),
                    "identifier": item.findtext("funderIdentifier"),
                },
            }
            funding.append(res)
        funding = None if len(funding) == 0 else funding  # for readability
        return funding

    def get_license(self):
        license_url = self.metadata.findtext(".//dataset/licensed/url")
        return license_url

    def get_was_revision_of(self):
        was_revision_of = self.kwargs.get("wasRevisionOf")
        return was_revision_of

    # def get_was_derived_from(self):
    #     return "get_was_derived_from from EML"
    #
    # def get_is_based_on(self):
    #     return "get_is_based_on from EML"
    #
    # def get_was_generated_by(self):
    #     return "get_was_generated_by from EML"


# Below are utility functions for the EML strategy.


def get_content_size(data_entity_element):
    """Return the content size for a data entity element.

    The If the "unit" attribute of the "size" element is defined, it will be
    appended to the content size value.

    Parameters
    ----------
    data_entity_element : lxml.etree._Element
        The data entity element to get the content size from.

    Returns
    -------
    str
    """
    size_element = data_entity_element.xpath(".//physical/size")
    size = size_element[0].text
    unit = size_element[0].get("unit")
    if unit:
        size += " " + unit
    return size


def get_content_url(data_entity_element):
    """Return the content url for a data entity element.

    If the "function" attribute of the data entity element is "information",
    the url elements value does not semantically match the SOSO contentUrl
    property definition and None is returned.

    Parameters
    ----------
    data_entity_element : lxml.etree._Element
        The data entity element to get the content url from.

    Returns
    -------
    str or None
    """
    url_element = data_entity_element.xpath(".//distribution/online/url")
    if url_element[0].get("function") != "information":
        return url_element[0].text
    return None


def convert_range_of_dates(range_of_dates):
    """Return EML rangeOfDates as a calendar datetime or geologic age interval.

    Parameters
    ----------
    range_of_dates : lxml.etree._Element
        The EML rangeOfDates element to convert.

    Returns
    -------
    str or dict
        A string if `range_of_dates` represents a calendar datetime, or a dict
        if it represents a geologic age. The dict is formatted as an OWL-Time
        ProperInterval type.
    """
    begin_date = convert_single_date_time_type(range_of_dates.xpath(".//beginDate")[0])
    end_date = convert_single_date_time_type(range_of_dates.xpath(".//endDate")[0])
    # To finish processing, we need to know if the begin_date and end_date are
    # calendar dates/times (str) or geologic ages (dict).
    if isinstance(begin_date, str) and isinstance(end_date, str):
        interval = begin_date + "/" + end_date
    else:
        interval = {
            "@type": "time:ProperInterval",
            "hasBeginning": begin_date,
            "hasEnd": end_date,
        }
    return interval


def convert_single_date_time(single_date_time):
    """Return EML singleDateTime as a calendar datetime or geologic age
    instant.

    Parameters
    ----------
    single_date_time : lxml.etree._Element
        The EML singleDateTime element to convert.

    Returns
    -------
    str or dict
        A string if `single_date_time` represents a calendar datetime, or a
        dict if it represents a geologic age. The dict is formatted as an
        OWL-Time Instant type.
    """
    return convert_single_date_time_type(single_date_time)


def convert_single_date_time_type(single_date_time):
    """Convert EML SingleDateTimeType to a calendar datetime or geologic age
    instant.

    Parameters
    ----------
    single_date_time : lxml.etree._Element
        The EML SingleDateTimeType element to convert.

    Returns
    -------
    str or dict
        A string if `single_date_time` represents a calendar datetime, or a
        dict if it represents a geologic age. The dict is formatted as an
        OWL-Time Instant type.

    Notes
    -----
    The return type is governed by the presence/absense of the EML
    alternativeTimeScale element. The presence of which indicates that the
    SingleDateTimeType element represents a geologic age, otherwise it
    represents a calendar date and/or time.
    """
    if not single_date_time.xpath(".//alternativeTimeScale"):
        calendar_date = single_date_time.findtext(".//calendarDate")
        time = single_date_time.findtext(".//time")
        instant = (
            calendar_date + "T" + time if calendar_date and time else calendar_date
        )
    else:
        instant = {
            "@type": "time:Instant",
            "time:inTimePosition": {
                "@type": "time:TimePosition",
                "time:numericPosition": {
                    "@type": "xsd:decimal",
                    "value": single_date_time.findtext(".//timeScaleAgeEstimate"),
                },
            },
            "gstime:uncertainty": {
                "@type": "xsd:decimal",
                "value": single_date_time.findtext(".//timeScaleAgeUncertainty"),
            },
            "time:hasTRS": {
                "@type": "xsd:string",
                "value": single_date_time.findtext(".//timeScaleName"),
            },
        }
    return instant


def get_spatial_type(geographic_coverage):
    """Return the object type for a geographic coverage element.

    Parameters
    ----------
    geographic_coverage : lxml.etree._Element
        The EML geographicCoverage element to get the object type from.

    Returns
    -------
    str
        One of "Point", "Box", or "Polygon".
    """
    # If the "boundingCoordinates" element is present, the object type is a
    # point if the north and south bounding coordinates are equal and the east
    # and west bounding coordinates are equal. Otherwise, the object type is a
    # box.
    if geographic_coverage.xpath(".//boundingCoordinates"):
        west = geographic_coverage.findtext(".//westBoundingCoordinate")
        east = geographic_coverage.findtext(".//eastBoundingCoordinate")
        south = geographic_coverage.findtext(".//southBoundingCoordinate")
        north = geographic_coverage.findtext(".//northBoundingCoordinate")
        if west == east and south == north:
            spatial_type = "Point"
        else:
            spatial_type = "Box"
    elif geographic_coverage.xpath(".//gRing"):
        # The geographic coverage is a polygon if the gRing element is present.
        spatial_type = "Polygon"
    return spatial_type


def get_point(geographic_coverage):
    """Return the geographic coverage as a point.

    Parameters
    ----------
    geographic_coverage : lxml.etree._Element
        The EML geographicCoverage element to convert.

    Returns
    -------
    dict
        The geographic coverage as a point.

    Notes
    -----
    This function assumes that the geographic coverage is a point. It does not
    check if the geographic coverage is a point. Use the `get_spatial_type`
    function to determine the object type.
    """
    north = geographic_coverage.findtext(".//northBoundingCoordinate")
    west = geographic_coverage.findtext(".//westBoundingCoordinate")
    point = {
        "@type": "GeoCoordinates",
        "latitude": north,
        "longitude": west,
    }
    elevation = get_elevation(geographic_coverage)
    if elevation:
        point["elevation"] = elevation
    return point


def get_elevation(geographic_coverage):
    """Return the elevation for a geographic coverage element.

    Parameters
    ----------
    geographic_coverage : lxml.etree._Element
        The EML geographicCoverage element to get the elevation from.

    Returns
    -------
    str
        The elevation.
    """
    # The elevation is the altitudeMinimum if it is equal to the
    # altitudeMaximum. A range of elevations is not supported.
    altitude_minimum = geographic_coverage.findtext(".//altitudeMinimum")
    altitude_maximum = geographic_coverage.findtext(".//altitudeMaximum")
    altitude_units = geographic_coverage.findtext(".//altitudeUnits")
    if altitude_minimum == altitude_maximum:
        elevation = altitude_minimum
        if altitude_units:  # add units if present
            elevation += " " + altitude_units
    else:
        elevation = None
    return elevation


def get_box(geographic_coverage):
    """Return the geographic coverage as a box.

    Parameters
    ----------
    geographic_coverage : lxml.etree._Element
        The EML geographicCoverage element to convert.

    Returns
    -------
    dict
        The geographic coverage as a box.

    Notes
    -----
    This function assumes that the geographic coverage is a box. It does not
    check if the geographic coverage is a box. Use the `get_spatial_type`
    function to determine the object type.
    """
    north = geographic_coverage.findtext(".//northBoundingCoordinate")
    west = geographic_coverage.findtext(".//westBoundingCoordinate")
    south = geographic_coverage.findtext(".//southBoundingCoordinate")
    east = geographic_coverage.findtext(".//eastBoundingCoordinate")
    box = {"@type": "GeoShape", "box": south + " " + west + " " + north + " " + east}
    return box


def get_polygon(geographic_coverage):
    """Return the geographic coverage as a polygon.

    Parameters
    ----------
    geographic_coverage : lxml.etree._Element
        The EML geographicCoverage element to convert.

    Returns
    -------
    dict
        The geographic coverage as a polygon.

    Notes
    -----
    This function assumes that the geographic coverage is a polygon. It does
    not check if the geographic coverage is a polygon. Use the
    `get_spatial_type` function to determine the object type.

    This function assumes, as per the EML 2.2.0 specification, that the
    GRingType is a "set of ordered pairs of floating-point numbers, separated
    by commas, in which the first number in each pair is the longitude of a
    point and the second is the latitude of the point.".
    """
    g_ring = geographic_coverage.findtext(".//gRing")
    # Parse g_ring into tuples of longitude/latitude pairs.
    res = []
    for pair in g_ring.split():
        res.append(tuple(pair.split(",")))
    # Reverse the order of the longitude/latitude pairs.
    res = [pair[::-1] for pair in res]
    # Ensure the first and last pairs are the same.
    if res[0] != res[-1]:
        res.append(res[0])
    # Convert the list of tuples to a space separated string.
    res = " ".join([" ".join(pair) for pair in res])
    # Create the polygon.
    polygon = {"@type": "GeoShape", "polygon": res}
    return polygon


def convert_user_id(user_id):
    """Return the user ID as a PropertyValue.

    Parameters
    ----------
    user_id : list of lxml.etree._Element
        The EML userId element to convert.

    Returns
    -------
    dict or None
        A PropertyValue if the `user_id` is not empty, otherwise None.
    """
    if len(user_id) != 0:
        property_value = {
            "@type": "PropertyValue",
            "propertyID": user_id[0].get("directory"),
            "value": user_id[0].text,
        }
    else:
        property_value = None
    return property_value
