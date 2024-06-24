"""Test the strategy implementations.

This module contains tests for the methods of each strategy implementation.

Each test uses two types of strategy instances:
- A "positive" strategy instance with a complete metadata record.
- A "negative" strategy instance with an empty metadata record.

Tests are skipped for methods that do not apply to a specific strategy. To skip
tests, we use the @pytest.mark.skipif decorator with one of the following
explanations (other rationales may be used as necessary):
- "Method Not Yet Implemented": Used during active development when a strategy
method has not been implemented yet but is planned to be. This tag is removed
incrementally as methods are implemented.
- "Property Not in Schema": Applied when the source metadata does not include
content within the schema for the target property the strategy method is
intended to extract. In such cases, the corresponding test is skipped
indefinitely.
"""

import pytest
from soso.interface import StrategyInterface
from tests.conftest import is_property_type
from tests.conftest import is_not_null


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


def test_get_name_returns_expected_type(strategy_instance, strategy_instance_no_meta):
    """Test that the get_name method returns the expected type."""
    # Positive case
    res = strategy_instance.get_name()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:Text"])
    # Negative case
    res = strategy_instance_no_meta.get_name()
    assert res is None


def test_get_description_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_description method returns the expected type."""
    # Positive case
    res = strategy_instance.get_description()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:Text"])
    # Negative case
    res = strategy_instance_no_meta.get_description()
    assert res is None


@pytest.mark.skipif(strategy_instance="EML", reason="Property not in schema")
def test_get_url_returns_expected_type(strategy_instance, strategy_instance_no_meta):
    """Test that the get_url method returns the expected type."""
    # Positive case
    res = strategy_instance.get_url()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:URL"])
    # Negative case
    res = strategy_instance_no_meta.get_url()
    assert res is None


@pytest.mark.skipif(strategy_instance="EML", reason="Property not in schema")
def test_get_same_as_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_same_as method returns the expected type."""
    # Positive case
    res = strategy_instance.get_same_as()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:URL"])
    # Negative case
    res = strategy_instance_no_meta.get_same_as()
    assert res is None


@pytest.mark.skipif(strategy_instance="EML", reason="Property not in schema")
def test_get_version_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_version method returns the expected type."""
    # Positive case
    res = strategy_instance.get_version()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:Text", "schema:Number"])
    # Negative case
    res = strategy_instance_no_meta.get_version()
    assert res is None


@pytest.mark.skipif(strategy_instance="EML", reason="Property not in schema")
def test_get_is_accessible_for_free_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_is_accessible_for_free method returns the expected
    type."""
    # Positive case
    res = strategy_instance.get_is_accessible_for_free()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:Boolean"])
    # Negative case
    res = strategy_instance_no_meta.get_is_accessible_for_free()
    assert res is None


def test_get_keywords_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_keywords method returns the expected type."""
    # Positive case
    res = strategy_instance.get_keywords()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:Text", "schema:DefinedTerm"])
    # Negative case
    res = strategy_instance_no_meta.get_keywords()
    assert res is None


def test_get_identifier_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_identifier method returns the expected type."""
    # Positive case
    res = strategy_instance.get_identifier()
    assert is_not_null(res)
    assert is_property_type(
        results=res,
        expected_types=["schema:Text", "schema:URL", "schema:PropertyValue"],
    )
    # Negative case
    res = strategy_instance_no_meta.get_identifier()
    assert res is None


@pytest.mark.skipif(strategy_instance="EML", reason="Property not in schema")
def test_get_citation_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_citation method returns the expected type."""
    # Positive case
    res = strategy_instance.get_citation()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:Text", "schema:CreativeWork"])
    # Negative case
    res = strategy_instance_no_meta.get_citation()
    assert res is None


def test_get_variable_measured_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_variable_measured method returns the expected type."""
    # Positive case
    res = strategy_instance.get_variable_measured()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:PropertyValue"])
    # Negative case
    res = strategy_instance_no_meta.get_variable_measured()
    assert res is None


@pytest.mark.skipif(strategy_instance="EML", reason="Property not in schema")
def test_get_included_in_data_catalog_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_included_in_data_catalog method returns the expected
    type."""
    # Positive case
    res = strategy_instance.get_included_in_data_catalog()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:DataCatalog"])
    # Negative case
    res = strategy_instance_no_meta.get_included_in_data_catalog()
    assert res is None


@pytest.mark.skipif(strategy_instance="EML", reason="Property not in schema")
def test_get_subject_of_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_subject_of method returns the expected type."""
    # Positive case
    res = strategy_instance.get_subject_of()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:DataDownload"])
    # Negative case
    res = strategy_instance_no_meta.get_subject_of()
    assert res is None


def test_get_distribution_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_distribution method returns the expected type."""
    # Positive case
    res = strategy_instance.get_distribution()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:DataDownload"])
    # Negative case
    res = strategy_instance_no_meta.get_distribution()
    assert res is None


@pytest.mark.skipif(strategy_instance="EML", reason="Property not in schema")
def test_get_potential_action_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_potential_action method returns the expected type."""
    # Positive case
    res = strategy_instance.get_potential_action()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:SearchAction"])
    # Negative case
    res = strategy_instance_no_meta.get_potential_action()
    assert res is None


@pytest.mark.skipif(strategy_instance="EML", reason="Property not in schema")
def test_get_date_created_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_date_created method returns the expected type."""
    # Positive case
    res = strategy_instance.get_date_created()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:Date", "schema:DateTime"])
    # Negative case
    res = strategy_instance_no_meta.get_date_created()
    assert res is None


def test_get_date_modified_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_date_modified method returns the expected type."""
    # Positive case
    res = strategy_instance.get_date_modified()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:Date", "schema:DateTime"])
    # Negative case
    res = strategy_instance_no_meta.get_date_modified()
    assert res is None


def test_get_date_published_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_date_published method returns the expected type."""
    # Positive case
    res = strategy_instance.get_date_published()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:Date", "schema:DateTime"])
    # Negative case
    res = strategy_instance_no_meta.get_date_published()
    assert res is None


@pytest.mark.skipif(strategy_instance="EML", reason="Property not in schema")
def test_get_expires_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_expires method returns the expected type."""
    # Positive case
    res = strategy_instance.get_expires()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:Date", "schema:DateTime"])
    # Negative case
    res = strategy_instance_no_meta.get_expires()
    assert res is None


def test_get_temporal_coverage_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_temporal_coverage method returns the expected type."""
    # Positive case
    res = strategy_instance.get_temporal_coverage()
    assert is_not_null(res)
    assert is_property_type(
        results=res,
        expected_types=[
            "schema:Text",
            "schema:Date",
            "schema:DateTime",
            "time:ProperInterval",
            "time:Instant",
        ],
    )
    # Negative case
    res = strategy_instance_no_meta.get_temporal_coverage()
    assert res is None


def test_get_spatial_coverage_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_spatial_coverage method returns the expected type."""
    # Positive case
    res = strategy_instance.get_spatial_coverage()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:Place"])
    # Negative case
    res = strategy_instance_no_meta.get_spatial_coverage()
    assert res is None


def test_get_creator_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_creator method returns the expected type."""
    # Positive case
    res = strategy_instance.get_creator()
    assert is_not_null(res)
    assert is_property_type(
        results=res,
        expected_types=["schema:Person", "schema:Organization", "schema:Role"],
    )
    # Negative case
    res = strategy_instance_no_meta.get_creator()
    assert res is None


def test_get_contributor_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_contributor method returns the expected type."""
    # Positive case
    res = strategy_instance.get_contributor()
    assert is_not_null(res)
    assert is_property_type(
        results=res,
        expected_types=["schema:Person", "schema:Organization", "schema:Role"],
    )
    # Negative case
    res = strategy_instance_no_meta.get_contributor()
    assert res is None


@pytest.mark.skipif(strategy_instance="EML", reason="Property not in schema")
def test_get_provider_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_provider method returns the expected type."""
    # Positive case
    res = strategy_instance.get_provider()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:Organization", "@id"])
    # Negative case
    res = strategy_instance_no_meta.get_provider()
    assert res is None


@pytest.mark.skipif(strategy_instance="EML", reason="Property not in schema")
def test_get_publisher_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_publisher method returns the expected type."""
    # Positive case
    res = strategy_instance.get_publisher()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:Organization", "@id"])
    # Negative case
    res = strategy_instance_no_meta.get_publisher()
    assert res is None


def test_get_funding_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_funding method returns the expected type."""
    # Positive case
    res = strategy_instance.get_funding()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:MonetaryGrant"])
    # Negative case
    res = strategy_instance_no_meta.get_funding()
    assert res is None


def test_get_license_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_license method returns the expected type."""
    # Positive case
    res = strategy_instance.get_license()
    assert is_not_null(res)
    assert is_property_type(res, ["schema:URL"])
    # Negative case
    res = strategy_instance_no_meta.get_license()
    assert res is None


@pytest.mark.skipif(strategy_instance="EML", reason="Property not in schema")
def test_get_was_revision_of_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_was_revision_of method returns the expected type."""
    # Positive case
    res = strategy_instance.get_was_revision_of()
    assert is_not_null(res)
    assert is_property_type(res, ["@id"])
    # Negative case
    res = strategy_instance_no_meta.get_was_revision_of()
    assert res is None


def test_get_was_derived_from_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_was_derived_from method returns the expected type."""
    # Positive case
    res = strategy_instance.get_was_derived_from()
    assert is_not_null(res)
    assert is_property_type(res, ["@id"])
    # Negative case
    res = strategy_instance_no_meta.get_was_derived_from()
    assert res is None


def test_get_is_based_on_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_is_based_on method returns the expected type."""
    # Positive case
    res = strategy_instance.get_is_based_on()
    assert is_not_null(res)
    assert is_property_type(res, ["@id"])
    # Negative case
    res = strategy_instance_no_meta.get_is_based_on()
    assert res is None


@pytest.mark.skipif(strategy_instance="EML", reason="Property not in schema")
def test_get_was_generated_by_returns_expected_type(
    strategy_instance, strategy_instance_no_meta
):
    """Test that the get_was_generated_by method returns the expected type."""
    # Positive case
    res = strategy_instance.get_was_generated_by()
    assert is_not_null(res)
    assert is_property_type(res, ["provone:Execution"])
    # Negative case
    res = strategy_instance_no_meta.get_was_generated_by()
    assert res is None
