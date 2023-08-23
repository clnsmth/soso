"""Configure the test suite."""

import socket
from urllib.parse import urlparse
import pytest
from soso.strategies.eml import EML
from soso.utilities import get_example_metadata_file_path


@pytest.fixture
def strategy_names():
    """Return the names of available strategies."""
    return ["eml"]


@pytest.fixture(params=[EML])
def strategy_instance(request):
    """Return the strategy instances."""
    if request.param is EML:
        res = request.param(file=get_example_metadata_file_path("EML"))
    return res


@pytest.fixture
def soso_properties():
    """Return the names of SOSO properties."""
    return [
        "@context",
        "@type",
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
        # "subjectOf",
        # "distribution",
        # "dateCreated",
        # "dateModified",
        # "datePublished",
        # "expires",
        # "temporalCoverage",
        # "spatialCoverage",
        # "creator",
        # "contributor",
        # "provider",
        # "publisher",
        # "funding",
        # "license",
        # "wasRevisionOf",
        # "wasDerivedFrom",
        # "isBasedOn",
        # "wasGeneratedBy",
        # "checksum",
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
        # "get_subject_of",
        # "get_distribution",
        # "get_date_created",
        # "get_date_modified",
        # "get_date_published",
        # "get_expires",
        # "get_temporal_coverage",
        # "get_spatial_coverage",
        # "get_creator",
        # "get_contributor",
        # "get_provider",
        # "get_publisher",
        # "get_funding",
        # "get_license",
        # "get_was_revision_of",
        # "get_was_derived_from",
        # "get_is_based_on",
        # "get_was_generated_by",
        # "get_checksum",
    ]
    return res


def pytest_configure(config):
    """A marker for tests that require internet connection."""
    config.addinivalue_line(
        "markers", "internet_required: mark test as requiring internet " + "connection"
    )


@pytest.fixture(scope="session")
def internet_connection():
    """Check if there is an internet connection."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False


def is_url(url):
    """Check if a string is a URL."""
    try:
        res = urlparse(url)
        return all([res.scheme, res.netloc])
    except ValueError:
        return False
