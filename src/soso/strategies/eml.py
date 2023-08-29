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
        # EML geographic coverage can have several elements. So get geographic coverage and iterate over each item.
        spatial_coverage = []
        for item in self.metadata.xpath(".//dataset/coverage/geographicCoverage"):
            # For each item determine the object type either as point, box, or polygon. Use a helper function to determine the type.
            object_type = get_spatial_type(item)
            # Based on the object type, call one of three additional helper functions to parse the content and return result as a dictionary.
            if object_type == "Point":
                spatial_coverage.append(get_point(item))
            elif object_type == "Box":
                spatial_coverage.append(get_box(item))
            elif object_type == "Polygon":
                spatial_coverage.append(get_polygon(item))
        return spatial_coverage

    # def get_creator(self):
    #     return "get_creator from EML"
    #
    # def get_contributor(self):
    #     return "get_contributor from EML"
    #
    # def get_provider(self):
    #     return "get_provider from EML"
    #
    # def get_publisher(self):
    #     return "get_publisher from EML"
    #
    # def get_funding(self):
    #     return "get_funding from EML"
    #
    # def get_license(self):
    #     return "get_license from EML"
    #
    # def get_was_revision_of(self):
    #     return "get_was_revision_of from EML"
    #
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


def get_spatial_type(item):
    pass


def get_point(item):
    pass


def get_box(item):
    pass


def get_polygon(item):
    pass
