"""The SPASE strategy module."""

from lxml import etree
from soso.interface import StrategyInterface
from soso.utilities import (
    delete_null_values,
)

# pylint: disable=duplicate-code


class SPASE(StrategyInterface):
    """Define the conversion strategy for SPASE (Space Physics Archive Search
    and Extract).

    Attributes:
        file: The path to the metadata file. This should be an XML file in
            SPASE format.
        schema_version: The version of the SPASE schema used in the metadata
            file.
        kwargs: Additional keyword arguments for handling unmappable
            properties. See the Notes section below for details.

    Notes:
        Some properties of this metadata standard don't directly map to SOSO.
        However, these properties can still be included by inputting the
        information as `kwargs`. Keys should match the property name, and
        values should be the desired value. For a deeper understanding of each
        SOSO property, refer to the `SOSO guidelines
        <https://github.com/ESIPFed/science-on-schema.org/blob/master/guides/Dataset.md>`_.

        Below are unmappable properties for this strategy:
            - [Add unmappable properties here]
    """

    def __init__(self, file: str, **kwargs: dict):
        """Initialize the strategy."""
        file = str(file)  # incase file is a Path object
        if not file.endswith(".xml"):  # file should be XML
            raise ValueError(file + " must be an XML file.")
        super().__init__(metadata=etree.parse(file))
        self.file = file
        self.schema_version = get_schema_version(self.metadata)
        self.namespaces = {"spase": "http://www.spase-group.org/data/schema"}
        self.kwargs = kwargs

    def get_id(self) -> None:
        """schema:identifier: spase:ResourceID)"""
        dataset_id = self.metadata.findtext(
            ".//spase:NumericalData/spase:ResourceID",
            namespaces=self.namespaces
        )
        return delete_null_values(dataset_id)

    def get_name(self) -> None:
        """schema:description: spase:ResourceHeader/ResourceName"""
        name = self.metadata.findtext(
            ".//spase:NumericalData/spase:ResourceHeader/spase:ResourceName",
            namespaces=self.namespaces
        )
        return delete_null_values(name)

    def get_description(self) -> None:
        """schema:description: spase:ResourceHeader/Description"""
        description = self.metadata.findtext(
            ".//spase:NumericalData/spase:ResourceHeader/spase:Description",
            namespaces=self.namespaces
        )
        return delete_null_values(description)

    def get_url(self) -> None:
        """schema:url: spase:ResourceHeader/DOI (or spase:ResourceID updated to https://hpde.io domain, if no DOI)"""
        url = self.metadata.findtext(
            ".//spase:NumericalData/spase:ResourceHeader/spase:DOI",
            namespaces=self.namespaces
        )
        if delete_null_values(url) is None:
            url = self.metadata.findtext(
                ".//spase:NumericalData/spase:ResourceID",
                namespaces=self.namespaces
            ).replace("spase://", "https://hpde.io/")
        return delete_null_values(url)

    def get_same_as(self) -> None:
        same_as = None
        return delete_null_values(same_as)

    def get_version(self) -> None:
        version = None
        return delete_null_values(version)

    def get_is_accessible_for_free(self) -> None:
        is_accessible_for_free = None
        return delete_null_values(is_accessible_for_free)

    def get_keywords(self) -> None:
        keywords = None
        return delete_null_values(keywords)

    def get_identifier(self) -> None:
        identifier = None
        return identifier

    def get_citation(self) -> None:
        citation = None
        return delete_null_values(citation)

    def get_variable_measured(self) -> None:
        variable_measured = None
        return delete_null_values(variable_measured)

    def get_included_in_data_catalog(self) -> None:
        included_in_data_catalog = None
        return delete_null_values(included_in_data_catalog)

    def get_subject_of(self) -> None:
        encoding_format = None
        return delete_null_values(encoding_format)

    def get_distribution(self) -> None:
        distribution = None
        return delete_null_values(distribution)

    def get_potential_action(self) -> None:
        potential_action = None
        return delete_null_values(potential_action)

    def get_date_created(self) -> None:
        date_created = None
        return delete_null_values(date_created)

    def get_date_modified(self) -> None:
        date_modified = None
        return delete_null_values(date_modified)

    def get_date_published(self) -> None:
        date_published = None
        return delete_null_values(date_published)

    def get_expires(self) -> None:
        expires = None
        return delete_null_values(expires)

    def get_temporal_coverage(self) -> None:
        temporal_coverage = None
        return delete_null_values(temporal_coverage)

    def get_spatial_coverage(self) -> None:
        spatial_coverage = None
        return spatial_coverage

    def get_creator(self) -> None:
        creator = None
        return delete_null_values(creator)

    def get_contributor(self) -> None:
        contributor = None
        return delete_null_values(contributor)

    def get_provider(self) -> None:
        provider = None
        return delete_null_values(provider)

    def get_publisher(self) -> None:
        publisher = None
        return delete_null_values(publisher)

    def get_funding(self) -> None:
        funding = None
        return delete_null_values(funding)

    def get_license(self) -> None:
        license_url = None
        return license_url

    def get_was_revision_of(self) -> None:
        was_revision_of = None
        return delete_null_values(was_revision_of)

    def get_was_derived_from(self) -> None:
        was_derived_from = None
        return delete_null_values(was_derived_from)

    def get_is_based_on(self) -> None:
        is_based_on = None
        return delete_null_values(is_based_on)

    def get_was_generated_by(self) -> None:
        was_generated_by = None
        return delete_null_values(was_generated_by)


# Below are utility functions for the SPASE strategy.


def get_schema_version(metadata: etree.ElementTree) -> str:
    """
    :param metadata:    The SPASE metadata object as an XML tree.

    :returns:   The version of the SPASE schema used in the metadata record.
    """
    schema_version = metadata.findtext(
        "{http://www.spase-group.org/data/schema}Version"
    )
    return schema_version
