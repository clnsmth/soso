"""The strategy interface module."""


class StrategyInterface:
    """Define the interface that each conversion strategy must implement.

    Attributes
    ----------
    metadata : object or None
        The metadata object, which could be an XML tree, a JSON object, or
        another suitable representation. This object is utilized by strategy
        methods to generate SOSO properties.
    kwargs : dict or None
        Additional keyword arguments that can be utilized to define SOSO
        properties that don't directly correspond to metadata fields.
    """

    def __init__(self, metadata=None, **kwargs):
        """Return the strategy attributes."""
        self.metadata = metadata
        self.kwargs = kwargs

    def get_name(self):
        """Return a descriptive name of a dataset.

        Returns
        -------
        str"""

    def get_description(self):
        """Return a short summary describing a dataset.

        Returns
        -------
        str"""

    def get_url(self):
        """Return the location of a page describing the dataset.

        Returns
        -------
        str
            A URL.
        """

    def get_same_as(self):
        """Return other URLs that can be used to access the dataset page.

        A link to a page that provides more information about the same dataset,
        usually in a different repository.

        Returns
        -------
        str
            A URL.
        """

    def get_version(self):
        """Return the version number or identifier for the dataset.

        Returns
        -------
        str or numbers.Number
        """

    def get_is_accessible_for_free(self):
        """Return if the dataset is accessible for free.

        Returns
        -------
        bool
        """

    def get_keywords(self):
        """Return keywords summarizing the dataset.

        Adding the schema:keywords field can be done in two ways - a text
        description, or by using schema:DefinedTerm. We recommend using
        schema:DefinedTerm if a keyword comes from a controlled vocabulary.

        Returns
        -------
        list
        """

    def get_identifier(self):
        """Return the identifier for the dataset, such as a DOI.

        Adding the schema:identifier field can be done in three ways - a text
        description, a URL, or by using the schema:PropertyValue field.

        Returns
        -------
        str or dict
        """

    def get_citation(self):
        """Return the citation for the dataset.

        Adding the schema:citation field can be done in two ways - as either
        text or a schema:CreativeWork.

        Returns
        -------
        str or dict
        """

    def get_variable_measured(self):
        """Return the measurement variables of the dataset.

        Adding the schema:variableMeasured field can be done in three ways - as
        a simple list of variable names, names of variables with formal
        property types, or, for numeric types, additional numeric
        properties.

        Returns
        -------
        list
        """

    def get_included_in_data_catalog(self):
        """Return the data catalog that the dataset is included in.

        Returns
        -------
        dict
        """

    def get_subject_of(self):
        """Return the metadata record for the dataset.

        Returns
        -------
        dict
        """

    def get_distribution(self):
        """Return the where to get the dataset and in what format."""

    def get_date_created(self):
        """Return the date the dataset was initially generated."""

    def get_date_modified(self):
        """Return the date the dataset was most recently updated or changed."""

    def get_date_published(self):
        """Return the date when a dataset was made available to the public
        through a publication process."""

    def get_expires(self):
        """Return the date when the dataset expires and is no longer useful or
        available."""

    def get_temporal_coverage(self):
        """Return the time period(s) that the content applies to."""

    def get_spatial_coverage(self):
        """Return the location on Earth that is the focus of the dataset
        content."""

    def get_creator(self):
        """Return the creator(s) of a dataset."""

    def get_contributor(self):
        """Return the contributor(s) of a dataset."""

    def get_provider(self):
        """Return the provider of a dataset."""

    def get_publisher(self):
        """Return the publisher of a dataset."""

    def get_funding(self):
        """Return the funding for a dataset."""

    def get_license(self):
        """Return the license of a dataset."""

    def get_was_revision_of(self):
        """Return a link to the prior version of the dataset."""

    def get_was_derived_from(self):
        """Return a link to a source dataset."""

    def get_is_based_on(self):
        """Return a link to a source dataset."""

    def get_was_generated_by(self):
        """Return an execution linking a program to source and derived
        products."""

    def get_checksum(self):
        """Return a cryptographic checksum value that can be used to
        characterize the contents of the object."""
