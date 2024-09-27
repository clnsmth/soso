"""The strategy interface module."""

from typing import Any


class StrategyInterface:
    """Define the interface that each conversion strategy must implement.

    Attributes:
        metadata:
            The metadata object, which could be an XML tree, a JSON object, or
            another suitable representation. This object is utilized by
            strategy methods to generate SOSO properties.

        file:
            The path to the metadata file.

        schema_version:
            The version of the metadata schema.

        kwargs:
            Additional keyword arguments for passing information to the chosen
            `strategy`. This can help in the case of unmappable properties.
            See the Notes section in the strategy's documentation for more
            information.
    """

    def __init__(
        self,
        metadata: Any = None,
        file: str = None,
        schema_version: str = None,
        **kwargs: dict
    ):
        """Return the strategy attributes."""
        self.metadata = metadata
        self.file = file
        self.schema_version = schema_version
        self.kwargs = kwargs

    def get_id(self):
        """
        :returns: The @id property for the dataset.
        """

    def get_name(self):
        """
        :returns: A descriptive name of a dataset.
        """

    def get_description(self):
        """
        :returns: A short summary describing a dataset.
        """

    def get_url(self):
        """
        :returns: The location of a page describing the dataset.
        """

    def get_same_as(self):
        """
        :returns:   Other URLs that can be used to access the dataset page,
                    usually in a different repository.
        """

    def get_version(self):
        """
        :returns: The version number or identifier for the dataset.
        """

    def get_is_accessible_for_free(self):
        """
        :returns: If the dataset is accessible for free.
        """

    def get_keywords(self):
        """
        :returns: Keywords summarizing the dataset.
        """

    def get_identifier(self):
        """
        :returns: The identifier for the dataset, such as a DOI.
        """

    def get_citation(self):
        """
        :returns: The citation for the dataset.
        """

    def get_variable_measured(self):
        """
        :returns: The measurement variables of the dataset.
        """

    def get_included_in_data_catalog(self):
        """
        :returns: The data catalog that the dataset is included in.
        """

    def get_subject_of(self):
        """
        :returns: The metadata record for the dataset.
        """

    def get_distribution(self):
        """
        :returns: Where to get the data and in what format.
        """

    def get_potential_action(self):
        """
        :returns: The query parameters and methods to actuate a data request.
        """

    def get_date_created(self):
        """
        :returns: The date the dataset was initially generated.
        """

    def get_date_modified(self):
        """
        :returns: The date the dataset was most recently updated or changed.
        """

    def get_date_published(self):
        """
        :returns:   The date when a dataset was made available to the public
                    through a publication process.
        """

    def get_expires(self):
        """
        :returns:   The date when the dataset expires and is no longer useful
                    or available.
        """

    def get_temporal_coverage(self):
        """
        :returns: The time period(s) that the content applies to.
        """

    def get_spatial_coverage(self):
        """
        :returns:   The location on Earth that is the focus of the dataset
                    content.
        """

    def get_creator(self):
        """
        :returns: The creator(s) of a dataset.
        """

    def get_contributor(self):
        """
        :returns: The contributor(s) of a dataset.
        """

    def get_provider(self):
        """
        :returns: The provider of a dataset.
        """

    def get_publisher(self):
        """
        :returns: The publisher of a dataset.
        """

    def get_funding(self):
        """
        :returns: The funding for a dataset.
        """

    def get_license(self):
        """
        :returns: The license of a dataset.
        """

    def get_was_revision_of(self):
        """
        :returns: A link to the prior version of the dataset.
        """

    def get_was_derived_from(self):
        """
        :returns: Links to source datasets.
        """

    def get_is_based_on(self):
        """
        :returns: Links to source datasets.
        """

    def get_was_generated_by(self):
        """
        :returns:   An execution linking a program to source and derived
                    products.
        """
