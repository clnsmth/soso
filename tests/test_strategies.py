"""Test the strategies."""

from numbers import Number
from soso.interface import StrategyInterface
from tests.conftest import is_url


def test_strategy_inherits_strategy_interface(strategy_instance):
    """Test that each strategy inherits the StrategyInterface class."""
    assert isinstance(strategy_instance, StrategyInterface)


# Each strategy should read a metadata document and store it as an attribute
# for class methods to access.


def test_strategy_reads_metadata(strategy_instance):
    """Test that each strategy reads a metadata document."""
    assert strategy_instance.metadata is not None


# SOSO properties are not universally shared across metadata dialects. In cases
# where a property is not available, the corresponding strategy method will
# return None. Therefore, each method test below first checks if the return
# value is not None before checking the type of the returned value. This
# approach allows for the flexibility of the SOSO guidelines while providing a
# consistent test suite.


def test_get_name_returns_expected_type(strategy_instance):
    """Test that the get_name method returns a string."""
    res = strategy_instance.get_name()
    if res is not None:
        assert isinstance(res, str)


def test_get_description_returns_expected_type(strategy_instance):
    """Test that the get_description method returns a string."""
    res = strategy_instance.get_description()
    if res is not None:
        assert isinstance(res, str)


def test_get_url_returns_expected_type(strategy_instance):
    """Test that the get_url method returns a URL formatted string."""
    # url doesn't map to EML so use kwargs
    strategy_instance.kwargs = {"url": "https://example.com"}
    res = strategy_instance.get_url()
    if res is not None:
        assert is_url(res)


def test_get_same_as_returns_expected_type(strategy_instance):
    """Test that the get_same_as method returns a URL formatted string."""
    strategy_instance.kwargs = {"sameAs": "https://example.com"}
    res = strategy_instance.get_same_as()
    if res is not None:
        assert is_url(res)


def test_get_version_returns_expected_type(strategy_instance):
    """Test that the get_version method returns a string or number."""
    version_values = ["1.0", 1.0]
    for value in version_values:
        strategy_instance.kwargs = {"version": value}
        res = strategy_instance.get_version()
        if res is not None:
            assert isinstance(res, (str, Number))


def test_get_get_is_accessible_for_free_returns_expected_type(strategy_instance):
    """Test that the get_is_accessible_for_free method returns a boolean."""
    strategy_instance.kwargs = {"isAccessibleForFree": True}
    res = strategy_instance.get_is_accessible_for_free()
    if res is not None:
        assert isinstance(res, bool)


def test_get_keywords_returns_expected_type(strategy_instance):
    """Test that the get_keywords method returns a list of strings and/or
    dictionaries."""
    res = strategy_instance.get_keywords()
    if res is not None:
        for item in res:
            assert isinstance(item, (str, dict))


def test_get_identifier_returns_expected_type(strategy_instance):
    """Test that the get_identifier method returns a string, URL, or
    dictionary."""
    res = strategy_instance.get_identifier()
    if res is not None:
        assert isinstance(res, (str, dict))  # str includes URL


def test_get_citation_returns_expected_type(strategy_instance):
    """Test that the get_citation method returns a string or dictionary."""
    res = strategy_instance.get_citation()
    if res is not None:
        assert isinstance(res, (str, dict))


def test_get_variable_measured_returns_expected_type(strategy_instance):
    """Test that the get_variable_measured method returns the expected type."""
    res = strategy_instance.get_variable_measured()
    if res is not None:
        assert isinstance(res, list)


# def test_get_included_in_data_catalog_returns_expected_type(strategy_instance):
#     """Test that the get_included_in_data_catalog method returns the expected
#     type."""
#     res = strategy_instance.get_included_in_data_catalog()
#     if res is not None:
#         # Test for URL (and other properties listed in SSSOM?).
#         assert True
#
#
# def test_get_subject_of_returns_expected_type(strategy_instance):
#     """Test that the get_subject_of method returns the expected type."""
#     res = strategy_instance.get_subject_of()
#     if res is not None:
#         # Test for subjectOf.
#         assert True
#
#
# def test_get_distribution_returns_expected_type(strategy_instance):
#     """Test that the get_distribution method returns the expected type."""
#     res = strategy_instance.get_distribution()
#     if res is not None:
#         # Test for distribution.
#         assert True
#
#
# def test_get_date_created_returns_expected_type(strategy_instance):
#     """Test that the get_date_created method returns the expected type."""
#     res = strategy_instance.get_date_created()
#     if res is not None:
#         # Test for string (or date?).
#         assert True
#
#
# def test_get_date_modified_returns_expected_type(strategy_instance):
#     """Test that the get_date_modified method returns the expected type."""
#     res = strategy_instance.get_date_modified()
#     if res is not None:
#         # Test for string (or date?).
#         assert True
#
#
# def test_get_date_published_returns_expected_type(strategy_instance):
#     """Test that the get_date_published method returns the expected type."""
#     res = strategy_instance.get_date_published()
#     if res is not None:
#         # Test for string (or date?).
#         assert True
#
#
# def test_get_expires_returns_expected_type(strategy_instance):
#     """Test that the get_expires method returns the expected type."""
#     res = strategy_instance.get_expires()
#     if res is not None:
#         # Test for string (or date?).
#         assert True
#
#
# def test_get_temporal_coverage_returns_expected_type(strategy_instance):
#     """Test that the get_temporal_coverage method returns the expected type."""
#     res = strategy_instance.get_temporal_coverage()
#     if res is not None:
#         # Test for string, date, datetime, URL.
#         assert True
#
#
# def test_get_spatial_coverage_returns_expected_type(strategy_instance):
#     """Test that the get_spatial_coverage method returns the expected type."""
#     res = strategy_instance.get_spatial_coverage()
#     if res is not None:
#         # Test for schema:geo.
#         assert True
#
#
# def test_get_creator_returns_expected_type(strategy_instance):
#     """Test that the get_creator method returns the expected type."""
#     res = strategy_instance.get_creator()
#     if res is not None:
#         # Test for schema:Role.
#         assert True
#
#
# def test_get_contributor_returns_expected_type(strategy_instance):
#     """Test that the get_contributor method returns the expected type."""
#     res = strategy_instance.get_contributor()
#     if res is not None:
#         # Test for schema:Role.
#         assert True
#
#
# def test_get_provider_returns_expected_type(strategy_instance):
#     """Test that the get_provider method returns the expected type."""
#     res = strategy_instance.get_provider()
#     if res is not None:
#         # Test for URL.
#         assert True
#
#
# def test_get_publisher_returns_expected_type(strategy_instance):
#     """Test that the get_publisher method returns the expected type."""
#     res = strategy_instance.get_publisher()
#     if res is not None:
#         # Test for URL.
#         assert True
#
#
# def test_get_funding_returns_expected_type(strategy_instance):
#     """Test that the get_funding method returns the expected type."""
#     res = strategy_instance.get_funding()
#     if res is not None:
#         # Test for MonetaryGrant.
#         assert True
#
#
# def test_get_license_returns_expected_type(strategy_instance):
#     """Test that the get_license method returns the expected type."""
#     res = strategy_instance.get_license()
#     if res is not None:
#         # Test for license.
#         assert True
#
#
# def test_get_was_revision_of_returns_expected_type(strategy_instance):
#     """Test that the get_was_revision_of method returns the expected type."""
#     res = strategy_instance.get_was_revision_of()
#     if res is not None:
#         # Test for IRI.
#         assert True
#
#
# def test_get_was_derived_from_returns_expected_type(strategy_instance):
#     """Test that the get_was_derived_from method returns the expected type."""
#     res = strategy_instance.get_was_derived_from()
#     if res is not None:
#         # Test for IRI.
#         assert True
#
#
# def test_get_is_based_on_returns_expected_type(strategy_instance):
#     """Test that the get_is_based_on method returns the expected type."""
#     res = strategy_instance.get_is_based_on()
#     if res is not None:
#         # Test for URL.
#         assert True
#
#
# def test_get_was_generated_by_returns_expected_type(strategy_instance):
#     """Test that the get_was_generated_by method returns the expected type."""
#     res = strategy_instance.get_was_generated_by()
#     if res is not None:
#         # Test for provone:Execution.
#         assert True
#
#
# def test_get_checksum_returns_expected_type(strategy_instance):
#     """Test that the get_checksum method returns the expected type."""
#     res = strategy_instance.get_checksum()
#     if res is not None:
#         # Test for spdx:Checksum.
#         assert True
