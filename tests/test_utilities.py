"""For testing the validator module."""

import warnings
from pathlib import PosixPath
from json import dumps
import pytest
from soso.utilities import validate
from soso.utilities import get_example_metadata_file_path, get_empty_metadata_file_path
from soso.utilities import get_shacl_file_path
from soso.utilities import delete_null_values
from soso.utilities import delete_unused_vocabularies
from soso.utilities import generate_citation_from_doi
from soso.utilities import limit_to_5000_characters
from soso.utilities import as_numeric


@pytest.mark.internet_required
def test_validate_returns_warning_when_invalid(internet_connection):
    """Test validate returns a warning when the graph is invalid."""
    if not internet_connection:
        pytest.skip("Internet connection is not available.")
    with pytest.warns(UserWarning, match="Validation Report"):
        validate("tests/incomplete.jsonld")


@pytest.mark.internet_required
def test_validate_returns_no_warning_when_valid(internet_connection):
    """Test validate returns no warning when the graph is valid."""
    if not internet_connection:
        pytest.skip("Internet connection is not available.")
    with warnings.catch_warnings(record=True) as list_of_warnings:
        validate("tests/full.jsonld")
        for warning in list_of_warnings:
            assert not issubclass(warning.category, UserWarning)


@pytest.mark.internet_required
def test_validate_returns_true_when_valid(internet_connection):
    """Test validate returns True when the graph is valid."""
    if not internet_connection:
        pytest.skip("Internet connection is not available.")
    assert validate("tests/full.jsonld") is True


@pytest.mark.internet_required
def test_validate_returns_false_when_invalid(internet_connection):
    """Test validate returns False when the graph is invalid."""
    if not internet_connection:
        pytest.skip("Internet connection is not available.")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert validate("tests/incomplete.jsonld") is False


def test_get_example_metadata_file_path_returns_path(strategy_names):
    """Test that get_example_metadata returns a path."""
    for strategy in strategy_names:
        file_path = get_example_metadata_file_path(strategy=strategy)
        assert isinstance(file_path, PosixPath)


def test_get_empty_metadata_file_path_returns_path(strategy_names):
    """Test that get_empty_metadata_file_path returns a path."""
    for strategy in strategy_names:
        file_path = get_empty_metadata_file_path(strategy=strategy)
        assert isinstance(file_path, PosixPath)


def test_get_shacl_file_path_returns_path():
    """Test that get_shacl_file_path returns a path."""
    file_path = get_shacl_file_path()
    assert isinstance(file_path, PosixPath)


def test_rm_null_values():
    """Test that delete_null_values removes null values from input data
    objeccts (JSON-LD values represented as Python objects)."""
    # Dictionary is empty / non-empty
    assert delete_null_values({}) is None
    assert delete_null_values({"name": "John Doe"}) == {"name": "John Doe"}

    # Dictionary only contains @type / has more than @type
    assert delete_null_values({"@type": "schema:Thing"}) is None
    data = delete_null_values({"@type": "schema:Thing", "name": "John Doe"})
    expected = {"@type": "schema:Thing", "name": "John Doe"}
    assert data == expected

    # Nested dictionary is empty / non-empty
    data = {"address": {}}
    assert delete_null_values(data) is None
    data = {"address": {"street": "123 Main St"}}
    expected = {"address": {"street": "123 Main St"}}
    assert delete_null_values(data) == expected

    # Nested dictionary only contains @type / has more than @type
    data = {"role": {"@type": "Role"}}
    assert delete_null_values(data) is None
    data = {"role": {"@type": "Role", "name": "Manager"}}
    expected = {"role": {"@type": "Role", "name": "Manager"}}
    assert delete_null_values(data) == expected

    # List is empty / non-empty
    assert delete_null_values([]) is None
    data = ["John Doe", 123, True]
    expected = ["John Doe", 123, True]
    assert delete_null_values(data) == expected

    # List contains empty dictionaries / non-empty dictionaries
    data = [{}, {}]
    assert delete_null_values(data) is None
    data = [{"name": "John Doe"}, {"name": "Jane Doe"}]
    res = delete_null_values(data)
    expected = [{"name": "John Doe"}, {"name": "Jane Doe"}]
    set1 = {frozenset(item.items()) for item in res}
    set2 = {frozenset(item.items()) for item in expected}
    assert set1 == set2

    # List contains empty lists / non-empty lists
    data = [[], []]
    assert delete_null_values(data) is None
    data = [["John Doe"], ["Jane Doe"]]
    expected = [["John Doe"], ["Jane Doe"]]
    assert delete_null_values(data) == expected

    # Text string is empty / non-empty
    assert delete_null_values("") is None
    assert delete_null_values("John Doe") == "John Doe"

    # Number is non-empty
    assert delete_null_values(123) == 123

    # Boolean is non-empty
    assert delete_null_values(True) is True

    # None is None
    assert delete_null_values(None) is None


def test_clean_context():
    """Test that the delete_unused_vocabularies function removes unused vocabularies from
    the @context."""
    # A context with a superset of vocabularies
    context = {
        "@context": {
            "@vocab": "https://schema.org/",
            "prov": "http://www.w3.org/ns/prov#",
            "provone": "http://purl.dataone.org/provone/2015/01/15/ontology#",
            "rdfs": "https://www.w3.org/2001/sw/RDFCore/Schema/200212/",
        }
    }
    # A graph using a subset of vocabularies. Note, rdfs is unused.
    graph = {
        "@context": context["@context"],
        "@type": "Dataset",
        "prov:wasGeneratedBy": {
            "@type": "provone:Execution",
            "prov:hadPlan": "https://somerepository.org/datasets/10.xxxx/"
            "Dataset-2.v2/process-script.R",
            "prov:used": {"@id": "https://doi.org/10.xxxx/Dataset-1"},
        },
    }
    # Define the expected cleaned graph
    cleaned_graph = {
        "@context": {
            "@vocab": "https://schema.org/",
            "prov": "http://www.w3.org/ns/prov#",
            "provone": "http://purl.dataone.org/provone/2015/01/15/ontology#",
        },
        "@type": "Dataset",
        "prov:wasGeneratedBy": {
            "@type": "provone:Execution",
            "prov:hadPlan": "https://somerepository.org/datasets/10.xxxx/"
            "Dataset-2.v2/process-script.R",
            "prov:used": {"@id": "https://doi.org/10.xxxx/Dataset-1"},
        },
    }
    # Test that unused vocabularies are removed from the @context, except
    # @vocab which is always kept.
    assert dumps(delete_unused_vocabularies(graph)) == dumps(cleaned_graph)


def test_generate_citation_from_doi():
    """Test that the generate_citation_from_doi function returns a citation
    for a valid DOI and set of parameters, and that it returns None
    otherwise."""
    # success
    doi = "https://doi.org/10.6073/pasta/e6c261fbd143e720af5a46a9a131a616"
    citation = generate_citation_from_doi(doi, style="apa", locale="en-US")
    assert isinstance(citation, str) and len(citation) > 0
    # failure
    doi = "10.6073/pasta/e6c261fbd143e720af5a46a9a131a616"
    citation = generate_citation_from_doi(doi, style="apa", locale="en-US")
    assert citation is None


def test_limit_to_5000_characters():
    """Test that the limit_to_5000_characters function returns a string
    that is 5000 characters or less."""
    text = "a" * 5001
    assert len(text) > 5000
    assert len(limit_to_5000_characters(text)) <= 5000
    assert limit_to_5000_characters(text) == text[:5000]
    assert limit_to_5000_characters("") == ""


def test_as_numeric():
    """Test that the as_numeric function returns the expected value."""
    assert as_numeric("1") == 1
    assert as_numeric("1.0") == 1.0
    assert as_numeric("text") is None
    assert as_numeric(None) is None
