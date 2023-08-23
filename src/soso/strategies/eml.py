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
                "name": "latitude",
                "propertyID":"http://purl.obolibrary.org/obo/NCIT_C68642",
                "url": "https://www.sample-data-repository.org/dataset-parameter/665787",
                "description": "Latitude where water samples were collected; north is positive. Latitude is a geographic coordinate which refers to the angle from a point on the Earth's surface to the equatorial plane",
                "unitText": "decimal degrees",
                "unitCode":"http://qudt.org/vocab/unit/DEG",
                "minValue": "45.0",
                "maxValue": "15.0"
            }
        return "get_variable_measured from EML"

    # def get_included_in_data_catalog(self):
    #     return "get_included_in_data_catalog from EML"
    #
    # def get_subject_of(self):
    #     return "get_subject_of from EML"
    #
    # def get_distribution(self):
    #     return "get_distribution from EML"
    #
    # def get_date_created(self):
    #     return "get_date_created from EML"
    #
    # def get_date_modified(self):
    #     return "get_date_modified from EML"
    #
    # def get_date_published(self):
    #     return "get_date_published from EML"
    #
    # def get_expires(self):
    #     return "get_expires from EML"
    #
    # def get_temporal_coverage(self):
    #     return "get_temporal_coverage from EML"
    #
    # def get_spatial_coverage(self):
    #     return "get_spatial_coverage from EML"
    #
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
    #
    # def get_checksum(self):
    #     return "get_checksum from EML"
