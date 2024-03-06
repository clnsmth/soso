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
        "subjectOf",
        "distribution",
        "potentialAction",
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
        "get_potential_action",
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


def is_property_type(result, expected_type):
    """
    Parameters
    ----------
    result : Any
        The result to be checked.
    expected_type : List
        The expected type(s) as a list of strings. See below for the list of
        expected types.

    Returns
    -------
    bool
        True if the result is one of the expected types.

    Notes
    -----
    Expected types are usually one or more of:
    - schema:Text
    - schema:URL
    - schema:Number
    - schema:Boolean
    - schema:DefinedTerm
    - schema:PropertyValue
    - schema:DataCatalog
    - schema:DataDownload
    - time:ProperInterval
    - time:Instant
    - schema:Place
    - schema:Person
    - schema:Organization
    - schema:MonetaryGrant
    - @id
    where schema and time are the namespaces of https://schema.org/ and
    http://www.w3.org/2006/time#, respectively.

    The namespace prefix of an expected type is not currently used to determine
    if the result is a member of the type, only the suffix is used, currently.
    """
    # Ensure arguments are lists for iteration
    if not isinstance(result, list):
        result = [result]
    if not isinstance(expected_type, list):
        expected_type = [expected_type]
    # Check that the result is at least one of the expected types
    results = []
    for res in result:
        is_expected_type = []
        for extype in expected_type:
            if extype == "schema:Text":
                is_expected_type.append(isinstance(res, str))
            elif extype == "schema:URL":
                is_expected_type.append(is_url(res))
            elif extype == "schema:Number":
                is_expected_type.append(isinstance(res, (int, float)))
            elif extype == "schema:Boolean":
                is_expected_type.append(isinstance(res, bool))
            elif extype == "schema:Date":
                # TODO: implement this check
                is_expected_type.append(isinstance(res, str))
            elif extype == "schema:DateTime":
                # TODO: implement this check
                is_expected_type.append(isinstance(res, str))
            elif extype == "@id":
                is_expected_type.append(is_url(res.get("@id")))
            elif isinstance(res, dict):  # schema:Thing or @id
                if res.get("@type") is not None:
                    is_type = extype.split(":")[1] in res.get("@type")
                    is_expected_type.append(is_type)
            else:
                is_expected_type.append(False)
        results.append(any(is_expected_type))
    return any(results)
