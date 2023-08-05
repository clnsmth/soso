"""The ISO 19115-1 strategy module."""

from soso.interface import StrategyInterface


class ISO19115(StrategyInterface):
    """Define the strategy for ISO 19115."""

    def get_name(self):
        return "name from ISO19115"

    def get_description(self):
        return "description from ISO19115"

    def get_url(self):
        return "url from ISO19115"

    def get_same_as(self):
        return "same_as from ISO19115"

    def get_version(self):
        return "version from ISO19115"

    def get_is_accessible_for_free(self):
        return True

    def get_keywords(self):
        return "get_keywords from ISO19115"

    def get_identifier(self):
        return "get_identifier from ISO19115"

    def get_citation(self):
        return "get_citation from ISO19115"

    def get_variable_measured(self):
        return "get_variable_measured from ISO19115"

    def get_included_in_data_catalog(self):
        return "get_included_in_data_catalog from ISO19115"

    def get_subject_of(self):
        return "get_subject_of from ISO19115"

    def get_distribution(self):
        return "get_distribution from ISO19115"

    def get_date_created(self):
        return "get_date_created from ISO19115"

    def get_date_modified(self):
        return "get_date_modified from ISO19115"

    def get_date_published(self):
        return "get_date_published from ISO19115"

    def get_expires(self):
        return "get_expires from ISO19115"

    def get_temporal_coverage(self):
        return "get_temporal_coverage from ISO19115"

    def get_spatial_coverage(self):
        return "get_spatial_coverage from ISO19115"

    def get_creator(self):
        return "get_creator from ISO19115"

    def get_contributor(self):
        return "get_contributor from ISO19115"

    def get_provider(self):
        return "get_provider from ISO19115"

    def get_publisher(self):
        return "get_publisher from ISO19115"

    def get_funding(self):
        return "get_funding from ISO19115"

    def get_license(self):
        return "get_license from ISO19115"

    def get_was_revision_of(self):
        return "get_was_revision_of from ISO19115"

    def get_was_derived_from(self):
        return "get_was_derived_from from ISO19115"

    def get_is_based_on(self):
        return "get_is_based_on from ISO19115"

    def get_was_generated_by(self):
        return "get_was_generated_by from ISO19115"

    def get_checksum(self):
        return "get_checksum from ISO19115"
