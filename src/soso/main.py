"""The converter module."""

from json import dumps
from soso.strategies.eml import EML


def convert(file, strategy, **kwargs):
    """Return SOSO markup for a metadata file and specified strategy.

    Parameters
    ----------
    file : str
        The path to the metadata file. Refer to the strategy's documentation
        for a list of supported file types.
    strategy : str
        The conversion strategy to be employed. Available strategies include:
        "EML".
    **kwargs : dict
        Additional keyword arguments for creating SOSO properties not covered
        by the chosen `strategy`. Check the Notes section in the strategy's
        documentation for more information.

    Returns
    -------
    str
        The SOSO graph in JSON-LD format.
    """

    # Load the strategy based on user choice. Pass kwargs, so the strategy can
    # operate on them.
    if strategy == "eml":
        strategy = EML(file, **kwargs)
    else:
        raise ValueError("Invalid choice!")

    # Build the graph
    graph = {
        "@context": {"@vocab": "https://schema.org/"},
        "@type": "Dataset",
        "name": strategy.get_name(),
        "description": strategy.get_description(),
        "url": strategy.get_url(),
        "sameAs": strategy.get_same_as(),
        "version": strategy.get_version(),
        "isAccessibleForFree": strategy.get_is_accessible_for_free(),
        "keywords": strategy.get_keywords(),
        "identifier": strategy.get_identifier(),
        "citation": strategy.get_citation(),
        "variableMeasured": strategy.get_variable_measured(),
        "includedInDataCatalog": strategy.get_included_in_data_catalog(),
        # "subjectOf": strategy.get_subject_of(),
        # "distribution": strategy.get_distribution(),
        # "dateCreated": strategy.get_date_created(),
        # "dateModified": strategy.get_date_modified(),
        # "datePublished": strategy.get_date_published(),
        # "expires": strategy.get_expires(),
        # "temporalCoverage": strategy.get_temporal_coverage(),
        # "spatialCoverage": strategy.get_spatial_coverage(),
        # "creator": strategy.get_creator(),
        # "contributor": strategy.get_creator(),
        # "provider": strategy.get_provider(),
        # "publisher": strategy.get_publisher(),
        # "funding": strategy.get_funding(),
        # "license": strategy.get_license(),
        # "wasRevisionOf": strategy.get_was_revision_of(),
        # "wasDerivedFrom": strategy.get_was_derived_from(),
        # "isBasedOn": strategy.get_is_based_on(),
        # "wasGeneratedBy": strategy.get_was_generated_by(),
        # "checksum": strategy.get_checksum(),
    }

    # Remove properties where get methods returned None, so the user is
    # return a clean graph.
    for key, value in list(graph.items()):
        if value is None:
            del graph[key]

    return dumps(graph)
