"""Configure the test suite."""

import pytest
from soso.strategies.eml import EML
from soso.strategies.iso19115 import ISO19115


@pytest.fixture
def strategy_names():
    """Return the names of available strategies."""
    return ["eml", "iso19115"]


@pytest.fixture(params=[EML, ISO19115])
def strategy_instance(request):
    """Return the strategy instances."""
    return request.param()


@pytest.fixture
def soso_properties():
    """Return the names of SOSO properties."""
    return [
        "name",
        "description",
        "url",
        "sameAs",
        "version",
        "isAccessibleForFree",
        "keywords",
        "identifier",
        "citation",
        "variableMeasured",
        "includedInDataCatalog",
        "subjectOf",
        "distribution",
        "dateCreated",
        "dateModified",
        "datePublished",
        "expires",
        "temporalCoverage",
        "spatialCoverage",
        "creator",
        "contributor",
        "provider",
        "publisher",
        "funding",
        "license",
        "wasRevisionOf",
        "wasDerivedFrom",
        "isBasedOn",
        "wasGeneratedBy",
        "checksum",
    ]


@pytest.fixture
def interface_methods():
    """Return the names of strategy methods."""
    res = [
        "get_name",
        "get_description",
        "get_url",
        "get_same_as",
        "get_version",
        "get_is_accessible_for_free",
        "get_keywords",
        "get_identifier",
        "get_citation",
        "get_variable_measured",
        "get_included_in_data_catalog",
        "get_subject_of",
        "get_distribution",
        "get_date_created",
        "get_date_modified",
        "get_date_published",
        "get_expires",
        "get_temporal_coverage",
        "get_spatial_coverage",
        "get_creator",
        "get_contributor",
        "get_provider",
        "get_publisher",
        "get_funding",
        "get_license",
        "get_was_revision_of",
        "get_was_derived_from",
        "get_is_based_on",
        "get_was_generated_by",
        "get_checksum",
    ]
    return res
