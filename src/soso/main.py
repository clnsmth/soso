"""The converter module."""

from soso.strategies.eml import EML
from soso.strategies.iso19115 import ISO19115


def convert(strategy):
    """Return SOSO markup for a metadata document and specified strategy."""

    # Load the strategy based on user choice
    if strategy == "eml":
        strategy = EML()
    elif strategy == "iso19115":
        strategy = ISO19115()
    else:
        raise ValueError("Invalid choice!")

    # Build the graph
    res = {
        "name": strategy.get_name(),
        "description": strategy.get_description(),
        "url": strategy.get_url(),
        "sameAs": strategy.get_same_as(),
        "version": strategy.get_version(),
        "isAccessibleForFree": strategy.get_is_accessible_for_free(),
        "keywords": strategy.get_keywords(),
        "identifier": strategy.get_identifier(),
        "citation": strategy.get_citation(),
        "variableMeasured": strategy.get_citation(),
        "includedInDataCatalog": strategy.get_included_in_data_catalog(),
        "subjectOf": strategy.get_subject_of(),
        "distribution": strategy.get_distribution(),
        "dateCreated": strategy.get_date_created(),
        "dateModified": strategy.get_date_modified(),
        "datePublished": strategy.get_date_published(),
        "expires": strategy.get_expires(),
        "temporalCoverage": strategy.get_temporal_coverage(),
        "spatialCoverage": strategy.get_spatial_coverage(),
        "creator": strategy.get_creator(),
        "contributor": strategy.get_creator(),
        "provider": strategy.get_provider(),
        "publisher": strategy.get_publisher(),
        "funding": strategy.get_funding(),
        "license": strategy.get_license(),
        "wasRevisionOf": strategy.get_was_revision_of(),
        "wasDerivedFrom": strategy.get_was_derived_from(),
        "isBasedOn": strategy.get_is_based_on(),
        "wasGeneratedBy": strategy.get_was_generated_by(),
        "checksum": strategy.get_checksum(),
    }
    return res
