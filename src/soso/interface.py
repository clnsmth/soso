"""The strategy interface module."""
from typing import Any


class StrategyInterface:
    """Define the interface that each conversion strategy must implement.

    Attributes
    ----------
    metadata : object or None
        The metadata object, which could be an XML tree, a JSON object, or
        another suitable representation. This object is utilized by strategy
        methods to generate SOSO properties.
    kwargs : dict or None
        Additional keyword arguments for passing information to the chosen
        `strategy`. This can help in the case of unmappable properties. See the
        Notes section in the strategy's documentation for more information.

    Returns
    -------
    Any
        Methods of the Strategy Interface return a Python value that, when
        serialized, follows SOSO conventions in JSON-LD format. None is
        returned for 'NULL' values.
    """

    def __init__(self, metadata: Any = None, **kwargs: dict):
        """Return the strategy attributes."""
        self.metadata = metadata
        self.kwargs = kwargs

    def get_name(self):
        """
        Returns
        -------
        Any
            A descriptive name of a dataset.
        """

    def get_description(self):
        """
        Returns
        -------
        Any
            A short summary describing a dataset.
        """

    def get_url(self):
        """
        Returns
        -------
        Any
            The location of a page describing the dataset.
        """

    def get_same_as(self):
        """
        Returns
        -------
        Any
            Other URLs that can be used to access the dataset page, usually in
            a different repository.
        """

    def get_version(self):
        """
        Returns
        -------
        Any
            The version number or identifier for the dataset.
        """

    def get_is_accessible_for_free(self):
        """
        Returns
        -------
        Any
            If the dataset is accessible for free.
        """

    def get_keywords(self):
        """
        Returns
        -------
        Any
            Keywords summarizing the dataset.
        """

    def get_identifier(self):
        """
        Returns
        -------
        Any
            The identifier for the dataset, such as a DOI.
        """

    def get_citation(self):
        """
        Returns
        -------
        Any
            The citation for the dataset.
        """

    def get_variable_measured(self):
        """
        Returns
        -------
        Any
            The measurement variables of the dataset.
        """

    def get_included_in_data_catalog(self):
        """
        Returns
        -------
        Any
            The data catalog that the dataset is included in.
        """

    def get_subject_of(self):
        """
        Returns
        -------
        Any
            The metadata record for the dataset.
        """

    def get_distribution(self):
        """
        Returns
        -------
        Any
            Where to get the data and in what format.
        """

    def get_potential_action(self):
        """
        Returns
        -------
        Any
            The query parameters and methods to actuate a data request.
        """

    def get_date_created(self):
        """
        Returns
        -------
        Any
            The date the dataset was initially generated.
        """

    def get_date_modified(self):
        """
        Returns
        -------
        Any
            The date the dataset was most recently updated or changed.
        """

    def get_date_published(self):
        """
        Returns
        -------
        Any
            The date when a dataset was made available to the public through a
            publication process.
        """

    def get_expires(self):
        """
        Returns
        -------
        Any
            The date when the dataset expires and is no longer useful or
            available.
        """

    def get_temporal_coverage(self):
        """
        Returns
        -------
        Any
            The time period(s) that the content applies to.
        """

    def get_spatial_coverage(self):
        """
        Returns
        -------
        Any
            The location on Earth that is the focus of the dataset content.
        """

    def get_creator(self):
        """
        Returns
        -------
        Any
            The creator(s) of a dataset.
        """

    def get_contributor(self):
        """
        Returns
        -------
        Any
            The contributor(s) of a dataset.
        """

    def get_provider(self):
        """
        Returns
        -------
        Any
            The provider of a dataset.
        """

    def get_publisher(self):
        """
        Returns
        -------
        Any
            The publisher of a dataset.
        """

    def get_funding(self):
        """
        Returns
        -------
        Any
            The funding for a dataset.
        """

    def get_license(self):
        """
        Returns
        -------
        Any
            The license of a dataset.
        """

    def get_was_revision_of(self):
        """
        Returns
        -------
        Any
            A link to the prior version of the dataset.
        """

    def get_was_derived_from(self):
        """
        Returns
        -------
        Any
            Links to source datasets.
        """

    def get_is_based_on(self):
        """
        Returns
        -------
        Any
            Links to source datasets.
        """

    def get_was_generated_by(self):
        """
        Returns
        -------
        Any
            An execution linking a program to source and derived products.
        """
