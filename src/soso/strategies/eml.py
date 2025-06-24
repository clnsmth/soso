"""The EML strategy module."""

from typing import Union
from lxml import etree
from soso.interface import StrategyInterface
from soso.utilities import (
    delete_null_values,
    limit_to_5000_characters,
    as_numeric,
    is_url,
    guess_mime_type_with_fallback,
)


class EML(StrategyInterface):
    """Define the conversion strategy for EML (Ecological Metadata Language).

    Attributes:
        file:   The path to the metadata file. This should be an XML file in
                EML format.
        schema_version: The version of the EML schema used in the metadata
            file.
        kwargs:   Additional keyword arguments for handling unmappable
                    properties. See the Notes section below for details.

    Notes:
        Some properties of this metadata standard don't directly map to SOSO.
        However, these properties can still be included by inputting the
        information as `kwargs`. Keys should match the property name, and
        values should be the desired value. For a deeper understanding of each
        SOSO property, refer to the `SOSO guidelines
        <https://github.com/ESIPFed/science-on-schema.org/blob/master/guides/Dataset.md>`_.

        Below are unmappable properties for this strategy:
            - @id of the Dataset
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
            - provider
            - publisher
            - prov:wasRevisionOf
            - prov:wasGeneratedBy
    """

    def __init__(self, file: str, **kwargs: dict):
        """Initialize the strategy."""
        file = str(file)  # incase file is a Path object
        if not file.endswith(".xml"):  # file should be XML
            raise ValueError(file + " must be an XML file.")
        super().__init__(metadata=etree.parse(file))
        self.file = file
        self.schema_version = get_schema_version(self.metadata)
        self.kwargs = kwargs

    def get_id(self) -> None:
        dataset_id = None  # EML does not map to the @id of the Dataset type
        return delete_null_values(dataset_id)

    def get_name(self) -> Union[str, None]:
        name = self.metadata.findtext(".//dataset/title")
        return delete_null_values(name)

    def get_description(self) -> Union[str, None]:
        description = self.metadata.xpath(".//dataset/abstract")
        if len(description) == 0:
            return None
        description = etree.tostring(description[0], encoding="utf-8", method="text")
        description = description.decode("utf-8").strip()
        description = limit_to_5000_characters(description)  # Google recommendations
        return delete_null_values(description)

    def get_url(self) -> None:
        url = None  # EML does not map to schema:url
        return delete_null_values(url)

    def get_same_as(self) -> None:
        same_as = None  # EML does not map to schema:sameAs
        return delete_null_values(same_as)

    def get_version(self) -> None:
        version = None  # EML does not map to schema:version
        return delete_null_values(version)

    def get_is_accessible_for_free(self) -> None:
        is_accessible_for_free = None  # EML does not map to schema:isAccessibleForFree
        return delete_null_values(is_accessible_for_free)

    def get_keywords(self) -> Union[list, None]:
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
        return delete_null_values(keywords)

    def get_identifier(self) -> Union[str, None]:
        identifier = self.metadata.xpath("@packageId")
        if identifier:
            return delete_null_values(identifier[0])
        return None

    def get_citation(self) -> None:
        citation = None  # EML does not map to schema:citation
        return delete_null_values(citation)

    def get_variable_measured(self) -> Union[list, None]:
        variable_measured = []
        for item in self.metadata.xpath(".//attributeList/attribute"):
            property_value = {
                "@type": "PropertyValue",
                "name": item.findtext("attributeName"),
                "alternateName": item.findtext("attributeLabel"),
                "propertyID": item.findtext(".//valueURI"),
                "description": item.findtext("attributeDefinition"),
                "measurementTechnique": get_methods(item),
                "unitText": item.findtext(".//standardUnit")
                or item.findtext(".//customUnit"),
            }
            property_value = {
                key: value for key, value in property_value.items() if value is not None
            }
            variable_measured.append(property_value)
        return delete_null_values(variable_measured)

    def get_included_in_data_catalog(self) -> None:
        included_in_data_catalog = (
            None  # EML does not map to schema:includedInDataCatalog
        )
        return delete_null_values(included_in_data_catalog)

    def get_subject_of(self) -> Union[dict, None]:
        encoding_format = get_encoding_format(self.metadata)
        date_modified = self.get_date_modified()
        if encoding_format and date_modified:
            subject_of = {
                "@type": "DataDownload",
                "name": "EML metadata for dataset",
                "description": "EML metadata describing the dataset",
                "encodingFormat": encoding_format,
                "contentUrl": None,  # EML does not map to schema:contentUrl
                "dateModified": date_modified,
            }
            if subject_of["contentUrl"] is None:
                return None  # subjectOf is not useful without contentUrl
            return delete_null_values(subject_of)
        return None

    def get_distribution(self) -> Union[list, None]:
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
                    "contentUrl": get_content_url(item),
                    "encodingFormat": get_data_entity_encoding_format(item),
                    "spdx:checksum": get_checksum(item),
                }
                distribution.append(data_download)
        return delete_null_values(distribution)

    def get_potential_action(self) -> None:
        potential_action = None  # EML does not map to schema:potentialAction
        return delete_null_values(potential_action)

    def get_date_created(self) -> None:
        date_created = None  # EML does not map to schema:dateCreated
        return delete_null_values(date_created)

    def get_date_modified(self) -> Union[str, None]:
        date_modified = self.metadata.findtext(".//dataset/pubDate")
        return delete_null_values(date_modified)

    def get_date_published(self) -> Union[str, None]:
        date_published = self.metadata.findtext(".//dataset/pubDate")
        return delete_null_values(date_published)

    def get_expires(self) -> None:
        expires = None  # EML does not map to schema:expires
        return delete_null_values(expires)

    def get_temporal_coverage(self) -> Union[str, dict, None]:
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
        else:
            temporal_coverage = None
        return delete_null_values(temporal_coverage)

    def get_spatial_coverage(self) -> Union[list, None]:
        geo = []
        for item in self.metadata.xpath(".//dataset/coverage/geographicCoverage"):
            object_type = get_spatial_type(item)
            if object_type == "Point":
                geo.append(get_point(item))
            elif object_type == "Box":
                geo.append(get_box(item))
            elif object_type == "Polygon":
                geo.append(get_polygon(item))
        if geo:
            spatial_coverage = {"@type": "Place", "geo": geo}
            return delete_null_values(spatial_coverage)
        return None

    def get_creator(self) -> Union[list, None]:
        creator = []
        creators = self.metadata.xpath(".//dataset/creator")
        for item in creators:
            creator.append(get_person_or_organization(item))  # can be either
        if len(creator) != 0:
            creator = {"@list": creator}  # to preserve order
        else:
            creator = None  # for readability
        return delete_null_values(creator)

    def get_contributor(self) -> Union[list, None]:
        contributor = []
        contributors = get_contributor_elements(self.metadata)
        for item in contributors:
            role = item.findtext("role")
            if item.tag == "contact":
                role = "contact"  # contact has no role
            res = {
                "@type": "Role",
                "roleName": role,
                "contributor": get_person_or_organization(item),  # can be either
            }
            contributor.append(res)
        if len(contributor) != 0:
            contributor = {"@list": contributor}  # to preserve order
        else:
            contributor = None  # for readability
        return delete_null_values(contributor)

    def get_provider(self) -> None:
        provider = None  # EML does not map to schema:provider
        return delete_null_values(provider)

    def get_publisher(self) -> None:
        publisher = None  # EML does not map to schema:publisher
        return delete_null_values(publisher)

    def get_funding(self) -> Union[list, None]:
        funding = []
        for item in self.metadata.xpath(".//dataset/project/award"):
            res = {
                "@id": item.findtext("awardUrl"),
                "@type": "MonetaryGrant",
                "identifier": item.findtext("awardNumber"),
                "name": item.findtext("title"),
                "url": item.findtext("awardUrl"),
                "funder": {
                    "@id": item.findtext("funderIdentifier"),
                    "@type": "Organization",
                    "name": item.findtext("funderName"),
                    "identifier": item.findtext("funderIdentifier"),
                },
            }
            funding.append(res)
        funding = None if len(funding) == 0 else funding  # for readability
        return delete_null_values(funding)

    def get_license(self) -> Union[str, None]:
        license_url = self.metadata.findtext(".//dataset/licensed/url")
        if license_url and "spdx.org" in license_url and ".html" in license_url:
            license_url = license_url[:-5]
            return delete_null_values(license_url)
        return None

    def get_was_revision_of(self) -> None:
        was_revision_of = None  # EML does not map to prov:wasRevisionOf
        return delete_null_values(was_revision_of)

    def get_was_derived_from(self) -> Union[list, None]:
        was_derived_from = []
        datasource = self.metadata.xpath(".//dataSource")
        for item in datasource:
            url = item.findtext(".//distribution/online/url")
            if url:
                was_derived_from.append({"@id": url})
        if len(was_derived_from) == 0:
            was_derived_from = None  # for readability
        return delete_null_values(was_derived_from)

    def get_is_based_on(self) -> Union[list, None]:
        is_based_on = self.get_was_derived_from()  # duplicate for discovery
        return delete_null_values(is_based_on)

    def get_was_generated_by(self) -> None:
        was_generated_by = None  # EML does not map to prov:wasGeneratedBy
        return delete_null_values(was_generated_by)


# Below are utility functions for the EML strategy.


def get_content_size(data_entity_element: etree._Element) -> Union[str, None]:
    """
    :param data_entity_element:     The data entity element to get the content
                                    size from.

    :returns: The content size of a data entity element.
    """
    size_element = data_entity_element.xpath(".//physical/size")
    if size_element:
        size = size_element[0].text
        unit = size_element[0].get("unit")
        if size and unit:
            return size + " " + unit
        return size
    return None


def get_content_url(data_entity_element: etree._Element) -> Union[str, None]:
    """
    :param data_entity_element:     The data entity element to get the content
                                    url from.

    :returns: The content url for a data entity element.

    Notes:
        If the "function" attribute of the data entity element is
        "information", the url elements value does not semantically match the
        SOSO contentUrl property definition and None is returned.
    """
    url_element = data_entity_element.xpath(".//distribution/online/url")
    if url_element:
        if url_element[0].get("function") != "information":
            return url_element[0].text
    return None


def convert_range_of_dates(range_of_dates: etree._Element) -> Union[str, dict, None]:
    """
    :param range_of_dates:  The EML rangeOfDates element to convert.

    :returns:   The EML rangeOfDates as a calendar datetime or geologic age
                interval. A string if `range_of_dates` represents a calendar
                datetime, or a dict if it represents a geologic age. The dict
                is formatted as an OWL-Time ProperInterval type.
    """
    begin_date = range_of_dates.xpath(".//beginDate")
    end_date = range_of_dates.xpath(".//endDate")
    if not begin_date or not end_date:
        return None
    begin_date = convert_single_date_time_type(begin_date[0])
    end_date = convert_single_date_time_type(end_date[0])
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


def convert_single_date_time(single_date_time: etree._Element) -> Union[str, dict]:
    """
    :param single_date_time:    The EML singleDateTime element to convert.

    :returns:   EML singleDateTime as a calendar datetime or geologic age
                instant. A string if `single_date_time` represents a calendar
                datetime, or a dict if it represents a geologic age. The dict
                is formatted as an OWL-Time Instant type.
    """
    return convert_single_date_time_type(single_date_time)


def convert_single_date_time_type(
    single_date_time: etree._Element,
) -> Union[str, dict, None]:
    """
    :param single_date_time:    The EML SingleDateTimeType element to convert.

    :returns:   The EML SingleDateTimeType element as a calendar datetime or
                geologic age instant. A string if `single_date_time`
                represents a calendar datetime, or a dict if it represents a
                geologic age. The dict is formatted as an OWL-Time Instant
                type.

    Notes:
        The return type is governed by the presence/absense of the EML
        alternativeTimeScale element. The presence of which indicates that the
        SingleDateTimeType element represents a geologic age, otherwise it
        represents a calendar date and/or time.
    """
    if len(single_date_time) == 0:
        return None
    if len(single_date_time.xpath(".//alternativeTimeScale")) == 0:
        calendar_date = single_date_time.findtext(".//calendarDate")
        time = single_date_time.findtext(".//time")
        instant = (
            calendar_date + "T" + time if calendar_date and time else calendar_date
        )
    else:
        numeric_position = as_numeric(
            single_date_time.findtext(".//timeScaleAgeEstimate")
        )
        uncertainty = as_numeric(
            single_date_time.findtext(".//timeScaleAgeUncertainty")
        )
        if not numeric_position or not uncertainty:
            return None
        instant = {
            "@type": "time:Instant",
            "time:inTimePosition": {
                "@type": "time:TimePosition",
                "time:hasTRS": {
                    "@type": "xsd:string",
                    "value": single_date_time.findtext(".//timeScaleName"),
                },
                "time:numericPosition": {
                    "@type": "xsd:decimal",
                    "value": numeric_position,
                },
            },
            "gstime:uncertainty": {"@type": "xsd:decimal", "value": uncertainty},
        }
    return instant


def get_spatial_type(geographic_coverage: etree._Element) -> Union[str, None]:
    """
    :param geographic_coverage: The EML geographicCoverage element to get the
                                object type from.

    :returns:   The object type for an EML geographic coverage element. One of
                "Point", "Box", or "Polygon".
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
    else:
        spatial_type = None
    return spatial_type


def get_point(geographic_coverage: etree._Element) -> Union[dict, None]:
    """
    :param geographic_coverage: The EML geographicCoverage element to convert.

    :returns:   The geographic coverage as a point.

    Notes:
        This function assumes that the geographic coverage is a point. It does
        not check if the geographic coverage is a point. Use the
        `get_spatial_type` function to determine the object type.
    """
    north = geographic_coverage.findtext(".//northBoundingCoordinate")
    west = geographic_coverage.findtext(".//westBoundingCoordinate")
    if north and west:
        point = {
            "@type": "GeoCoordinates",
            "latitude": north,
            "longitude": west,
        }
        elevation = get_elevation(geographic_coverage)
        if elevation:
            point["elevation"] = elevation
    else:
        point = None
    return point


def get_elevation(geographic_coverage: etree._Element) -> Union[str, None]:
    """
    :param geographic_coverage: The EML geographicCoverage element to get the
                                elevation from.

    :returns:   The elevation for a geographic coverage element.
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


def get_box(geographic_coverage: etree._Element) -> Union[dict, None]:
    """
    :param geographic_coverage: The EML geographicCoverage element to convert.

    :returns:   The geographic coverage as a box.

    Notes:
        This function assumes that the geographic coverage is a box. It does
        not check if the geographic coverage is a box. Use the
        `get_spatial_type` function to determine the object type.
    """
    north = geographic_coverage.findtext(".//northBoundingCoordinate")
    west = geographic_coverage.findtext(".//westBoundingCoordinate")
    south = geographic_coverage.findtext(".//southBoundingCoordinate")
    east = geographic_coverage.findtext(".//eastBoundingCoordinate")
    if north and west and south and east:
        box = {
            "@type": "GeoShape",
            "box": south + " " + west + " " + north + " " + east,
        }
    else:
        box = None
    return box


def get_polygon(geographic_coverage: etree._Element) -> Union[dict, None]:
    """
    :param geographic_coverage: The EML geographicCoverage element to convert.

    :returns:   The geographic coverage as a polygon.

    Notes:
        This function assumes that the geographic coverage is a polygon. It
        does not check if the geographic coverage is a polygon. Use the
        `get_spatial_type` function to determine the object type.

        This function assumes, as per the EML 2.2.0 specification, that the
        GRingType is a "set of ordered pairs of floating-point numbers,
        separated by commas, in which the first number in each pair is the
        longitude of a point and the second is the latitude of the point.".
    """
    g_ring = geographic_coverage.findtext(".//gRing")
    if g_ring:
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
    else:
        polygon = None
    return polygon


def convert_user_id(user_id: list) -> Union[dict, None]:
    """
    :param user_id: The EML userId element to convert.

    :returns:   The user ID as a PropertyValue if the `user_id` is not empty,
                otherwise None.
    """
    if len(user_id) != 0:
        url = user_id[0].text if is_url(user_id[0].text) else None
        property_value = {
            "@id": url,
            "@type": "PropertyValue",
            "propertyID": user_id[0].get("directory"),
            "url": url,
            "value": user_id[0].text,
        }
    else:
        property_value = None
    return property_value


def get_data_entity_encoding_format(
    data_entity_element: etree._Element,
) -> Union[str, None]:
    """
    :param data_entity_element: The data entity element to get the encoding
                                format from.

    :returns:   The encoding format (as a MIME type) for a data entity element.
    """
    object_name = data_entity_element.findtext(".//physical/objectName")
    if object_name:
        encoding_format = guess_mime_type_with_fallback(object_name)
    else:
        encoding_format = None
    return encoding_format


def get_person_or_organization(responsible_party: etree._Element) -> dict:
    """
    :param responsible_party: The EML responsibleParty element to convert.

    :returns:   The responsible party as a schema:Person or
    schema:Organization.

    Notes:
        The Person and Organization types are very similar, so this function
        handles them both and determines which type to return based on the
        presence/absense of the individualName element.
    """
    if responsible_party.xpath("individualName"):
        res = {
            "@type": "Person",
            "honorificPrefix": responsible_party.findtext("salutation"),
            "givenName": responsible_party.findtext("individualName/givenName"),
            "familyName": responsible_party.findtext("individualName/surName"),
            "url": responsible_party.findtext("onlineUrl"),
            "identifier": convert_user_id(responsible_party.xpath("userId")),
        }
    else:
        res = {
            "@type": "Organization",
            "name": responsible_party.findtext("organizationName"),
            "identifier": convert_user_id(responsible_party.xpath("userId")),
        }
    return res


def get_encoding_format(metadata: etree.ElementTree) -> str:
    """
    :param metadata:    The metadata object as an XML tree.

    :returns:   The encoding format of an EML metadata record.
    """
    schema_location = metadata.getroot().nsmap.get("eml", None)
    encoding_format = ["application/xml", schema_location]
    return encoding_format


def get_methods(xml: etree._Element) -> Union[str, None]:
    """
    :param xml: The EML metadata record.

    :returns:   The methods section of an EML metadata record with XML tags
                removed, and leading and trailing whitespace removed. None if
                the methods section is not found.
    """
    methods = xml.xpath(".//methods")
    if len(methods) == 0:
        return None
    methods = etree.tostring(methods[0], encoding="utf-8", method="text")
    methods = methods.decode("utf-8").strip()
    return methods


def get_checksum(data_entity_element: etree._Element) -> Union[list, None]:
    """
    :param data_entity_element: The data entity element to get the checksum(s)
                                from.

    :returns:   A list of dictionaries formatted as spdx:Checksum, for each
                method attribute of the authentication element containing an
                spdx:algorithm. Otherwise None.
    """
    checksum = []
    for item in data_entity_element.xpath(".//physical/authentication"):
        if item.get("method") is not None and "spdx.org" in item.get("method"):
            algorithm = item.get("method").split("#")[-1]
            res = {
                "@type": "spdx:Checksum",
                "spdx:checksumValue": item.text,
                "spdx:algorithm": {"@id": "spdx:" + algorithm},
            }
            checksum.append(res)
    if len(checksum) == 0:
        checksum = None
    return checksum


def get_contributor_elements(metadata: etree.ElementTree) -> Union[list, None]:
    """
    :param metadata:    The metadata object as an XML tree.

    :returns:   Contributors to a dataset. These are the contact,
        associatedParty, and top level personnel elements.
    """
    elements = ["contact", "associatedParty", "personnel"]
    contributors = []
    for element in elements:
        xpath = ".//dataset/" + element
        if element == "personnel":  # personnel are in project not dataset
            xpath = ".//project/" + element  # nested projects are out of scope
        for item in metadata.xpath(xpath):
            contributors.append(item)
    return contributors


def get_schema_version(metadata: etree.ElementTree) -> str:
    """
    :param metadata:    The EML metadata object as an XML tree.

    :returns:   The version of the EML schema used in the metadata record.
    """
    name_space = metadata.getroot().nsmap.get("eml", None)
    if name_space is None:
        return None
    schema_version = name_space.split("/eml-")[-1]
    return schema_version
