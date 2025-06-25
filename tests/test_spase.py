"""Test additional SPASE module functions and methods."""

from datetime import datetime
from lxml import etree
from soso.strategies.spase import (
    get_schema_version,
    get_authors,
    get_access_urls,
    get_dates,
    person_format,
    name_splitter,
    get_measurement_method,
    get_information_url,
    get_instrument,
    get_observatory,
    get_alternate_name,
    get_cadence_context,
    get_mentions,
    get_is_part_of,
    get_orcid_and_affiliation,
    get_metadata_license,
    get_temporal,
    process_authors,
    verify_type,
    get_resource_id,
    get_relation,
    update_log,
    make_trial_start_and_stop,
    find_match,
)
from soso.utilities import get_empty_metadata_file_path, get_example_metadata_file_path

# pylint: disable=too-many-lines


def test_get_schema_version_returns_expected_value():
    """Test that the get_schema_version function returns the expected value."""

    # Positive case: The function will return the schema version of the SPASE
    # file.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_schema_version(spase) == "2.5.0"

    # Negative case: If the schema version is not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_schema_version(spase) is None


def test_get_authors_returns_expected_value():
    """Test that the get_authors function returns the expected value."""

    # Positive case: The function will return the highest priority authors found in the SPASE
    #   file, as well as their roles, the publication date, the publisher,
    #   contributors, publication title, backup contacts (names and roles)
    #   which are not considered authors, and any remaining contacts with
    #   author roles not in PubInfo
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_authors(spase) == (
        [
            "Fuselier, Stephen A.",
            "Young, David T.",
            "Gomez, Roman G.",
            "Burch, James L.",
        ],
        [
            ["Author", "CoInvestigator"],
            ["Author", "CoInvestigator"],
            ["Author", "CoInvestigator"],
            ["Author", "PrincipalInvestigator"],
        ],
        "2022-01-01T00:00:00",
        "Space Physics Data Facility",
        [],
        "",
        {
            "spase://SMWG/Person/Stephen.A.Fuselier": ["InstrumentLead"],
            "spase://SMWG/Person/David.T.Young": ["InstrumentLead"],
            "spase://SMWG/Person/Roman.G.Gomez": [],
            "spase://SMWG/Person/James.L.Burch": [],
            "spase://SMWG/Person/Jolene.S.Pickett": [],
            "spase://SMWG/Person/MMS_SDC_POC": ["HostContact"],
            "spase://SMWG/Person/Robert.M.Candey": ["MetadataContact"],
            "spase://SMWG/Person/Lee.Frost.Bargatze": ["MetadataContact"],
        },
        {
            "spase://SMWG/Person/Stephen.A.Fuselier": "Fuselier, Stephen A.",
            "spase://SMWG/Person/David.T.Young": "Young, David T.",
            "spase://SMWG/Person/Roman.G.Gomez": "Gomez, Roman G.",
            "spase://SMWG/Person/James.L.Burch": "Burch, James L.",
            "spase://SMWG/Person/Jolene.S.Pickett": ["PrincipalInvestigator"],
        },
    )

    # Negative case: If the authors, author roles, publication date, publisher,
    #   contributors, publication title, and backup contacts are not present,
    #   the function will return null/empty values.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_authors(spase) == ([], [], "", "", [], "", {}, {})


def test_get_access_urls_returns_expected_value():
    """Test that the get_access_urls function returns the expected value."""

    # Positive case: The function will return AccessURLs found in the
    #   SPASE record, separated into two dictionaries, with the keys as
    #   the url and the values to be a list containing their data format(s),
    #   name, and product key (if applicable)
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_access_urls(spase) == (
        {
            "https://spdf.gsfc.nasa.gov/pub/data/cassini/helio1day/"
            + "cassini_helio1day_position_19971016_v01.cdf": ["CDF", "HTTPS from SPDF"]
        },
        {
            "ftps://lasp.colorado.edu/mms/sdc/public/data/mms4/hpca/brst/l2/ion/": [
                "CDF",
                {"keys": [], "name": "FTPS from the MMS SDC (not with most browsers)"},
            ],
            "https://lasp.colorado.edu/mms/sdc/public/data/mms4/hpca/brst/l2/ion/": [
                "CDF",
                {"keys": [], "name": "HTTPS from the MMS SDC"},
            ],
            "ftps://spdf.gsfc.nasa.gov/pub/data/mms/mms4/hpca/brst/l2/ion/": [
                "CDF",
                {"keys": [], "name": "FTPS from SPDF (not with most browsers)"},
            ],
            "https://cdaweb.gsfc.nasa.gov/cgi-bin/eval2.cgi?dataset=MMS4_HPCA_BRST_L2_ION"
            + "&index=sp_phys": [
                "CDF",
                {"keys": ["MMS4_HPCA_BRST_L2_ION"], "name": "CDAWeb"},
            ],
            "https://cdaweb.gsfc.nasa.gov/hapi": [
                "CSV",
                {"keys": ["MMS4_HPCA_BRST_L2_ION"], "name": "CDAWeb HAPI Server"},
            ],
        },
    )

    # Negative case: If the access_URLs are not present, the function will
    # return empty/null values.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_access_urls(spase) == ({}, {})


def test_get_dates_returns_expected_value():
    """Test that the get_dates function returns the expected value."""
    # Positive case: The function will return the release date and
    # the list of all dates in revision history of the SPASE file.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_dates(spase) == (
        datetime(2023, 3, 4, 12, 34, 56),
        [
            datetime(2021, 4, 27, 15, 38, 11),
            datetime(2022, 8, 4, 12, 34, 56),
            datetime(2023, 3, 4, 12, 34, 56),
        ],
    )

    # Negative case: If the schema version is not present, the function will
    # return null/empty values
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_dates(spase) == ("", [])


def test_person_format_returns_expected_value():
    """Test that the person_format function returns the expected value."""

    # Positive case: The function will return the correctly formatted entry to be added
    # to the contributors or creator list.
    # Case 1: A contributor is being formatted.
    person_type = "contributor"
    role_name = "GeneralContact"
    name = "John H. Smith"
    given_name = "John H."
    family_name = "Smith"
    assert person_format(
        person_type, role_name, name, given_name, family_name, first_entry=True
    ) == (
        {
            "@type": ["Role", "DefinedTerm"],
            "contributor": {
                "@type": "Person",
                "name": "John H. Smith",
                "givenName": "John H.",
                "familyName": "Smith",
            },
            "inDefinedTermSet": {
                "@id": "https://spase-group.org/data/model/spase-latest/spase-latest_xsd.htm#Role",
                "@type": "DefinedTermSet",
                "name": "SPASE Role",
                "url": "https://spase-group.org/data/model/spase-latest/spase-latest_xsd.htm#Role",
            },
            "roleName": "General Contact",
            "termCode": "GeneralContact",
        }
    )
    # Case 2: An author is being formatted
    person_type = "creator"
    role_name = "PI"
    name = "Mark L. Watney"
    given_name = "Mark L."
    family_name = "Watney"
    assert person_format(person_type, role_name, name, given_name, family_name) == (
        {
            "@type": "Person",
            "name": "Mark L. Watney",
            "givenName": "Mark L.",
            "familyName": "Watney",
        }
    )

    # Negative case: If no contact info is given, the function will
    # return None.
    assert person_format(None, None, None, None, None) is None


def test_name_splitter_returns_expected_value():
    """Test that the name_splitter function returns the expected value."""

    # Positive case: The function will return the full name, givenName,
    #   and familyName of the Contact provided.
    person = "spase://SMWG/Person/John.H.Smith"
    assert name_splitter(person) == ("John H. Smith", "John H.", "Smith")

    # Negative case: If no contact info is given, the function will
    # raise an error.
    try:
        name_splitter(None)
    except ValueError as error:
        assert "This function only takes a nonempty string as an argument" in str(error)
    try:
        name_splitter("")
    except ValueError as error:
        assert "This function only takes a nonempty string as an argument" in str(error)


def test_get_measurement_method_returns_expected_value():
    """Test that the get_measurement_method function returns the expected value."""

    # Positive case: The function will return the MeasurementType(s) found in the SPASE
    # file.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    namespaces = {"spase": "http://www.spase-group.org/data/schema"}
    assert get_measurement_method(spase, namespaces) == [
        {
            "@type": "DefinedTerm",
            "inDefinedTermSet": {
                "@id": "https://spase-group.org/data/model/spase-latest/spase-latest_xsd"
                + ".htm#MeasurementType",
                "@type": "DefinedTermSet",
                "name": "SPASE MeasurementType",
                "url": "https://spase-group.org/data/model/spase-latest/spase-latest_xsd"
                + ".htm#MeasurementType",
            },
            "name": "Energetic Particles",
            "termCode": "EnergeticParticles",
        },
        {
            "@type": "DefinedTerm",
            "inDefinedTermSet": {
                "@id": "https://spase-group.org/data/model/spase-latest/spase-latest_xsd"
                + ".htm#MeasurementType"
            },
            "name": "Magnetic Field",
            "termCode": "MagneticField",
        },
    ]

    # Negative case: If the schema version is not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_measurement_method(spase, namespaces) is None


def test_get_information_url_returns_expected_value():
    """Test that the get_information_url function returns the expected value."""

    # Positive case: The function will return the name, description, and url for the
    # InformationURL(s) found in the SPASE file.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_information_url(spase) == [
        {
            "name": "The Magnetospheric Multiscale (MMS) Mission home page at Goddard "
            "Space Flight Center (GSFC)",
            "url": "https://mms.gsfc.nasa.gov/",
            "description": "The Magnetospheric Multiscale (MMS) Mission Home Page hosted by "
            "the Goddard Space Flight Center (GSFC).",
        },
        {
            "name": "Data Caveats and Current Release Notes at LASP MMS SDC",
            "url": "https://lasp.colorado.edu/mms/sdc/public/datasets/hpca/",
            "description": "The Magnetospheric Multiscale (MMS) Mission home page hosted by the "
            "Laboratory of Atmospheric and Space Physics, Science Data Center (LASP, SDC) at the "
            "University of Colorado, Boulder.",
        },
    ]

    # Negative case: If the schema version is not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_information_url(spase) is None


def test_get_instrument_returns_expected_value():
    """Test that the get_instrument function returns the expected value."""

    # Positive case: The function will return the name, ResourceID, and InformationURL(s) for the
    # InstrumentID(s) found in the SPASE file.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    kwargs = {"testing": "soso-spase/tests/data/"}
    assert get_instrument(
        spase, str(get_example_metadata_file_path("SPASE")).replace("\\", "/"), **kwargs
    ) == (
        [
            {
                "@id": "https://hpde.io/SMWG/Instrument/MMS/4/FIELDS/FGM",
                "@type": ["IndividualProduct", "prov:Entity", "sosa:System"],
                "identifier": {
                    "@id": "https://hpde.io/SMWG/Instrument/MMS/4/FIELDS/FGM",
                    "@type": "PropertyValue",
                    "propertyID": "SPASE Resource ID",
                    "value": "spase://SMWG/Instrument/MMS/4/FIELDS/FGM",
                },
                "name": "MMS 4 FIELDS Suite, Fluxgate Magnetometer (FGM) Instrument",
                "url": "https://hpde.io/SMWG/Instrument/MMS/4/FIELDS/FGM",
            }
        ]
    )

    # Negative case: If the schema version is not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert (
        get_instrument(
            spase, str(get_example_metadata_file_path("SPASE")).replace("\\", "/")
        )
        is None
    )


def test_get_observatory_returns_expected_value():
    """Test that the get_observatory function returns the expected value."""

    # Positive case: The function will return the name, ResourceID, and InformationURL(s) for the
    # observatoryID(s) found in the SPASE file.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    kwargs = {"testing": "soso-spase/tests/data/"}
    assert get_observatory(
        spase, str(get_example_metadata_file_path("SPASE")).replace("\\", "/"), **kwargs
    ) == (
        [
            {
                "@type": ["ResearchProject", "prov:Entity", "sosa:Platform"],
                "@id": "https://hpde.io/SMWG/Observatory/MMS",
                "name": "MMS",
                "identifier": {
                    "@id": "https://hpde.io/SMWG/Observatory/MMS",
                    "@type": "PropertyValue",
                    "propertyID": "SPASE Resource ID",
                    "value": "spase://SMWG/Observatory/MMS",
                },
                "url": "https://hpde.io/SMWG/Observatory/MMS",
            },
            {
                "@type": ["ResearchProject", "prov:Entity", "sosa:Platform"],
                "@id": "https://hpde.io/SMWG/Observatory/MMS/4",
                "name": "MMS-4",
                "identifier": {
                    "@id": "https://hpde.io/SMWG/Observatory/MMS/4",
                    "@type": "PropertyValue",
                    "propertyID": "SPASE Resource ID",
                    "value": "spase://SMWG/Observatory/MMS/4",
                },
                "url": "https://hpde.io/SMWG/Observatory/MMS/4",
            },
        ]
    )

    # Negative case: If the schema version is not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert (
        get_observatory(
            spase, str(get_example_metadata_file_path("SPASE")).replace("\\", "/")
        )
        is None
    )


def test_get_alternate_name_returns_expected_value():
    """Test that the get_alternate_name function returns the expected value."""

    # Positive case: The function will return the alternate name of the SPASE
    # dataset.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_alternate_name(spase) == "MMS4_HPCA_BRST_L2_ION"

    # Negative case: If the alternate name is not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_schema_version(spase) is None


def test_get_cadence_context_returns_expected_value():
    """Test that the get_cadence_context function returns the expected value."""

    # Positive case: The function will return a description of the Cadence
    # found within the TemporalDescription section of the SPASE record.
    cadence = "PT0.625S"
    assert (
        get_cadence_context(cadence)
        == "The time series is periodic with a 0.625 second cadence"
    )

    # Negative case: If Cadence is not present, the function will
    # return None.
    assert get_cadence_context(None) is None


def test_get_mentions_returns_expected_value():
    """Test that the get_mentions function returns the expected value."""

    # Positive case: The function will return info about the SPASE ResourceIDs with the
    # AssociationType = "Other" found within the Association section of the SPASE record.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    kwargs = {"testing": "soso-spase/tests/data/"}
    assert get_mentions(spase, **kwargs) == (
        [
            {
                "@id": "https://doi.org/10.48322/xhe6-5a16",
                "@type": "Dataset",
                "creator": {
                    "@list": [
                        {
                            "@type": "Person",
                            "familyName": "Gold",
                            "givenName": "R.E.",
                            "name": "Gold, R.E.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Roelof",
                            "givenName": "E.C.",
                            "name": "Roelof, E.C.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Krimigis",
                            "givenName": "S.",
                            "name": "Krimigis, S.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Haggerty",
                            "givenName": "D.",
                            "name": "Haggerty, D.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Armstrong",
                            "givenName": "T.P.",
                            "name": "Armstrong, T.P.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Manweiler",
                            "givenName": "J.W.",
                            "name": "Manweiler, J.W.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Patterson",
                            "givenName": "J.D.",
                            "name": "Patterson, J.D.",
                        },
                    ]
                },
                "description": "17-min-averaged sectored proton fluxes from the MF Spectrum "
                + "Analyzer of the ACE/EPAM LEFS150 instrument. All energies thresholds take "
                + "into account the incident particle type, shielding, and inactive "
                + "dead-layer of the solid state detector. All fluxes are background corrected "
                + "and are in the solar wind rest frame.",
                "identifier": "https://doi.org/10.48322/xhe6-5a16",
                "name": "ACE Electron Proton Alpha Monitor (EPAM) LEFS150 MFSA, Solar Wind "
                + "Frame, Sectored Proton Fluxes, 17 min Averages",
                "url": "https://doi.org/10.48322/xhe6-5a16",
            },
            {
                "@id": "https://doi.org/10.48322/2ry9-3s59",
                "@type": "Dataset",
                "creator": {
                    "@list": [
                        {
                            "@type": "Person",
                            "familyName": "Gold",
                            "givenName": "R.E.",
                            "name": "Gold, R.E.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Roelof",
                            "givenName": "E.C.",
                            "name": "Roelof, E.C.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Krimigis",
                            "givenName": "S.",
                            "name": "Krimigis, S.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Haggerty",
                            "givenName": "D.",
                            "name": "Haggerty, D.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Armstrong",
                            "givenName": "T.P.",
                            "name": "Armstrong, T.P.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Manweiler",
                            "givenName": "J.W.",
                            "name": "Manweiler, J.W.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Patterson",
                            "givenName": "J.D.",
                            "name": "Patterson, J.D.",
                        },
                    ]
                },
                "description": "Daily-averaged sectored proton fluxes from the MF Spectrum "
                + "Analyzer of the ACE/EPAM LEFS150 instrument. All energies thresholds take "
                + "into account the incident particle type, shielding, and inactive "
                + "dead-layer of the solid state detector. All fluxes are background corrected "
                + "and are in the solar wind rest frame.",
                "identifier": "https://doi.org/10.48322/2ry9-3s59",
                "name": "ACE Electron Proton Alpha Monitor (EPAM) LEFS150 MFSA, Solar Wind "
                + "Frame, Sectored Proton Fluxes, Daily Averages",
                "url": "https://doi.org/10.48322/2ry9-3s59",
            },
        ]
    )

    # Negative case: If Other AssociationIDs are not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_mentions(spase) is None


def test_get_is_part_of_returns_expected_value():
    """Test that the get_is_part_of function returns the expected value."""

    # Positive case: The function will return info about the SPASE ResourceIDs with the
    # AssociationType = "PartOf" found within the Association section of the SPASE record.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    kwargs = {"testing": "soso-spase/tests/data/"}
    assert get_is_part_of(spase, **kwargs) == {
        "@id": "https://doi.org/10.48322/s9mg-he04",
        "@type": "Dataset",
        "creator": {
            "@list": [
                {
                    "@type": "Person",
                    "affiliation": {
                        "@type": "Organization",
                        "identifier": {
                            "@id": "https://ror.org/01rmh9n78",
                            "@type": "PropertyValue",
                            "propertyID": "https://registry.identifiers.org/registry/ror",
                            "url": "https://ror.org/01rmh9n78",
                            "value": "ror:01rmh9n78",
                        },
                        "name": "University of New Hampshire",
                    },
                    "familyName": "McKibben",
                    "givenName": "R. Bruce",
                    "name": "McKibben, R. Bruce",
                },
                {
                    "@type": "Person",
                    "affiliation": {
                        "@type": "Organization",
                        "identifier": {
                            "@id": "https://ror.org/01rmh9n78",
                            "@type": "PropertyValue",
                            "propertyID": "https://registry.identifiers.org/registry/ror",
                            "url": "https://ror.org/01rmh9n78",
                            "value": "ror:01rmh9n78",
                        },
                        "name": "Physics Department, University of New Hampshire",
                    },
                    "familyName": "Connell",
                    "givenName": "James",
                    "name": "Connell, James",
                },
                {
                    "@type": "Person",
                    "affiliation": {
                        "@type": "Organization",
                        "identifier": {
                            "@id": "https://ror.org/04atsbb87",
                            "@type": "PropertyValue",
                            "propertyID": "https://registry.identifiers.org/registry/ror",
                            "url": "https://ror.org/04atsbb87",
                            "value": "ror:04atsbb87",
                        },
                        "name": "Department of Physics and Space Sciences, Florida Institute "
                        + "of Technology",
                    },
                    "familyName": "Zhang",
                    "givenName": "Ming",
                    "name": "Zhang, Ming",
                },
                {
                    "@type": "Person",
                    "familyName": "Tranquille",
                    "givenName": "Cecil",
                    "name": "Tranquille, Cecil",
                },
            ]
        },
        "description": "This Data Set contains 10 min Average Ion and Electron Spin-Averaged "
        + "Coincidence Counting Rates from the COSPIN High Energy Telescope (HET). The "
        + "Parameter Keys in the Parameter Level Segments below are specifically relevant "
        + "to the UFA accessible Versions of the Data.",
        "identifier": "https://doi.org/10.48322/s9mg-he04",
        "name": "Ulysses Cosmic Ray and Solar Particle Investigation (COSPIN) High Energy "
        + "Telescope (HET) Ion and Electron Spin-Averaged Coincidence Counting Rates, "
        + "10 min Data",
        "url": "https://doi.org/10.48322/s9mg-he04",
    }

    # Negative case: If PartOf AssociationIDs are not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_is_part_of(spase) is None


def test_get_orcid_and_affiliation_returns_expected_value():
    """Test that the get_orcid_and_affiliation function returns the expected value."""

    # Positive case: The function will return the ORCiD and organization (with its ror)
    #   associated with the given SPASE Person.
    person = "spase://SMWG/Person/David.T.Young"
    kwargs = {"testing": "soso-spase/tests/data/"}
    spase = str(get_example_metadata_file_path("SPASE")).replace("\\", "/")
    assert get_orcid_and_affiliation(person, spase, **kwargs) == (
        "0000-0001-9473-7000",
        "Southwest Research Institute",
        "03tghng59",
    )

    # Negative case: If no person information is provided, the function will
    # return None value.
    assert get_orcid_and_affiliation(None, None) == ("", "", "")


def test_get_temporal_returns_expected_value():
    """Test that the get_temporal function returns the expected value."""

    # Positive case: The function will return the Cadence
    # found within the TemporalDescription section of the SPASE record,
    # as well as a human-readable description of it.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    namespaces = {"spase": "http://www.spase-group.org/data/schema"}
    assert get_temporal(spase, namespaces) == [
        "The time series is periodic with a 0.625 second cadence",
        "PT0.625S",
    ]

    # Negative case: If Cadence is not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_temporal(spase, namespaces) is None


def test_get_metadata_license_returns_expected_value():
    """Test that the get_metadata_license function returns the expected value."""

    # Positive case: The function will return the metadata license found
    # in the top-level SPASE line as an attribute.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_metadata_license(spase) == "Creative Commons Zero v1.0 Universal"

    # Negative case: If the metadata license is not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_metadata_license(spase) is None


def test_process_authors_returns_expected_value():
    """Test that the process_authors function returns the expected value."""

    # Positive case: The function will return the correctly formatted info for an entry
    # to be added to the creators and/or contributors list.
    # Case 1: Authors were found in PublicationInfo
    author = [
        "Fuselier, Stephen, A.; Young, David, T.; Gomez, Roman, G.; Burch, James, L."
    ]
    author_role = ["Author"]
    contacts_list = {
        "spase://SMWG/Person/Stephen.A.Fuselier": ["CoInvestigator"],
        "spase://SMWG/Person/David.T.Young": ["CoInvestigator"],
        "spase://SMWG/Person/Roman.G.Gomez": ["CoInvestigator"],
        "spase://SMWG/Person/James.L.Burch": ["PrincipalInvestigator"],
        "spase://SMWG/Person/Jolene.S.Pickett": ["PrincipalInvestigator"],
    }
    assert process_authors(author, author_role, contacts_list) == (
        [
            "Fuselier, Stephen A.",
            "Young, David T.",
            "Gomez, Roman G.",
            "Burch, James L.",
        ],
        [
            ["Author", "CoInvestigator"],
            ["Author", "CoInvestigator"],
            ["Author", "CoInvestigator"],
            ["Author", "PrincipalInvestigator"],
        ],
        {
            "spase://SMWG/Person/Stephen.A.Fuselier": "Fuselier, Stephen A.",
            "spase://SMWG/Person/David.T.Young": "Young, David T.",
            "spase://SMWG/Person/Roman.G.Gomez": "Gomez, Roman G.",
            "spase://SMWG/Person/James.L.Burch": "Burch, James L.",
            "spase://SMWG/Person/Jolene.S.Pickett": ["PrincipalInvestigator"],
        },
    )

    # Case 2: Authors are found in Contacts (no PublicationInfo container found)
    author = ["spase://SMWG/Person/Mark.Linton", "spase://SMWG/Person/Russell.A.Howard"]
    author_role = ["PrincipalInvestigator", "FormerPI"]
    contacts_list = {
        "spase://SMWG/Person/Mark.Linton": ["PrincipalInvestigator"],
        "spase://SMWG/Person/Russell.A.Howard": ["FormerPI"],
    }
    assert process_authors(author, author_role, contacts_list) == (
        ["spase://SMWG/Person/Mark.Linton", "spase://SMWG/Person/Russell.A.Howard"],
        ["PrincipalInvestigator", "FormerPI"],
        {},
    )

    # Negative case: If no contact info is given, the function will
    # return None.
    assert process_authors(None, None, None) == (None, None, None)


def test_verify_type_returns_expected_value():
    """Test that the verify_type function returns the expected value."""

    # Positive cases: The function will return True or False for the first and
    #   second values, depending on if the URL is a link to a Dataset or JournalArticle.
    #   It will also return a dictionary containing additional info pulled from the
    #   DataCite API if the link is to a non-NASA Dataset
    # Case 1: hpde.io landing page URL to a Dataset is provided
    url = (
        "https://hpde.io/NASA/NumericalData/MMS/4/HotPlasmaCompositionAnalyzer/Burst"
        "/Level2/Ion/PT0.625S.html"
    )
    assert verify_type(url) == (True, False, {})

    # Case 2: DOI that resolves to an hpde.io landing page is provided
    url = "https://doi.org/10.48322/6cfb-rq65"
    assert verify_type(url) == (True, False, {})

    # Case 3: DOI that does not resolve to an hpde.io landing page (nor is a
    #   Dataset) is provided
    url = "https://doi.org/10.5281/zenodo.13287868"
    assert verify_type(url) == (False, False, {})

    # Case 4: hpde.io landing page URL to a non-Dataset is provided
    url = "https://hpde.io/SMWG/Instrument/ACE/MAG.html"
    assert verify_type(url) == (False, False, {})

    # Case 5: DOI that does not resolve to an hpde.io landing page (but still to
    #   a Dataset) is provided
    url = "https://doi.org/10.5067/SeaBASS/TURBID9/DATA001"
    assert verify_type(url) == (
        True,
        False,
        {
            "name": "Turbid9",
            "creators": {
                "@type": "Person",
                "name": "SeaBASS",
            },
            "description": "No description currently available for "
            + "https://doi.org/10.5067/SeaBASS/TURBID9/DATA001.",
        },
    )

    # Case 6: DOI that does not resolve to an hpde.io landing page (but still
    #   to a JournalArticle) is provided
    url = "https://doi.org/10.1007/s11214-014-0119-6"
    assert verify_type(url) == (False, True, {})

    # Negative case: If no related info is given, the function will
    # return None value.
    assert verify_type(None) == (False, False, {})


def test_get_resource_id_returns_expected_value():
    """Test that the get_resource_id function returns the expected value."""

    # Positive case: The function will return the Resource ID of the SPASE
    # dataset.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    namespaces = {"spase": "http://www.spase-group.org/data/schema"}
    assert (
        get_resource_id(spase, namespaces)
        == "spase://NASA/NumericalData/MMS/4/HotPlasmaCompositionAnalyzer/Burst/Level2/Ion/PT0.625S"
    )

    # Negative case: If the Resource ID is not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_resource_id(spase, namespaces) is None


def test_get_relation_returns_expected_value():
    """Test that the get_relation function returns the expected value."""

    # Positive case: The function will return info about the SPASE ResourceIDs with the
    # given AssociationType found within the Association section of the SPASE record.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    kwargs = {"testing": "soso-spase/tests/data/"}
    root = spase.getroot()
    desired_root = None
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desired_root = elt

    assert get_relation(desired_root, ["Other"], **kwargs) == (
        [
            {
                "@id": "https://doi.org/10.48322/xhe6-5a16",
                "@type": "Dataset",
                "creator": {
                    "@list": [
                        {
                            "@type": "Person",
                            "familyName": "Gold",
                            "givenName": "R.E.",
                            "name": "Gold, R.E.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Roelof",
                            "givenName": "E.C.",
                            "name": "Roelof, E.C.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Krimigis",
                            "givenName": "S.",
                            "name": "Krimigis, S.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Haggerty",
                            "givenName": "D.",
                            "name": "Haggerty, D.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Armstrong",
                            "givenName": "T.P.",
                            "name": "Armstrong, T.P.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Manweiler",
                            "givenName": "J.W.",
                            "name": "Manweiler, J.W.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Patterson",
                            "givenName": "J.D.",
                            "name": "Patterson, J.D.",
                        },
                    ]
                },
                "description": "17-min-averaged sectored proton fluxes from the MF Spectrum "
                + "Analyzer of the ACE/EPAM LEFS150 instrument. All energies thresholds "
                + "take into account the incident particle type, shielding, and inactive "
                + "dead-layer of the solid state detector. All fluxes are background "
                + "corrected and are in the solar wind rest frame.",
                "identifier": "https://doi.org/10.48322/xhe6-5a16",
                "name": "ACE Electron Proton Alpha Monitor (EPAM) LEFS150 MFSA, Solar Wind "
                + "Frame, Sectored Proton Fluxes, 17 min Averages",
                "url": "https://doi.org/10.48322/xhe6-5a16",
            },
            {
                "@id": "https://doi.org/10.48322/2ry9-3s59",
                "@type": "Dataset",
                "creator": {
                    "@list": [
                        {
                            "@type": "Person",
                            "familyName": "Gold",
                            "givenName": "R.E.",
                            "name": "Gold, R.E.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Roelof",
                            "givenName": "E.C.",
                            "name": "Roelof, E.C.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Krimigis",
                            "givenName": "S.",
                            "name": "Krimigis, S.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Haggerty",
                            "givenName": "D.",
                            "name": "Haggerty, D.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Armstrong",
                            "givenName": "T.P.",
                            "name": "Armstrong, T.P.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Manweiler",
                            "givenName": "J.W.",
                            "name": "Manweiler, J.W.",
                        },
                        {
                            "@type": "Person",
                            "familyName": "Patterson",
                            "givenName": "J.D.",
                            "name": "Patterson, J.D.",
                        },
                    ]
                },
                "description": "Daily-averaged sectored proton fluxes from the MF Spectrum "
                + "Analyzer of the ACE/EPAM LEFS150 instrument. All energies thresholds "
                + "take into account the incident particle type, shielding, and inactive "
                + "dead-layer of the solid state detector. All fluxes are background "
                + "corrected and are in the solar wind rest frame.",
                "identifier": "https://doi.org/10.48322/2ry9-3s59",
                "name": "ACE Electron Proton Alpha Monitor (EPAM) LEFS150 MFSA, Solar Wind "
                + "Frame, Sectored Proton Fluxes, Daily Averages",
                "url": "https://doi.org/10.48322/2ry9-3s59",
            },
        ]
    )

    # Negative case: If no relation is given, the function will
    # return None.
    assert get_relation(None, None, None) is None


def test_update_log_returns_expected_value():
    """Test that the update_log function returns the expected value."""

    # Positive case: The function will update the log file by adding the
    #   repository name given.

    # create log file that holds the name(s) of the repos needed
    with open("./test_update_log.txt", "w", encoding="utf-8") as f:
        f.write("This is placeholder text for use in test_spase.py.")
    update_log(".", "testRepo", "test_update_log")
    with open("./test_update_log.txt", "r", encoding="utf-8") as f:
        text = f.read()
    assert "testRepo" in text


    # Negative case: If there is no file nor attempt number present, the function will
    # return None.
    assert update_log(None, None, None) is None


def test_make_trial_start_and_stop_returns_expected_value():
    """Test that the make_trial_start_and_stop function returns the expected value."""

    # Positive cases: The function will create sentences describing the sugggested start
    #   and end times derived from the TemporalDescription found in the SPASE record.
    #   If an end is not found, it will create a test one, set 1 min after start.

    # Case 1: No stop date is found
    temp_covg = "2015-09-01T12:11:00/.."
    assert make_trial_start_and_stop(temp_covg) == (
        "Use 2015-09-01T12:11:00 as default value.",
        "Use 2015-09-01T12:12:00 as a test end value.",
    )

    # Case 2: A stop date is found
    temp_covg = "2015-09-01T12:11:00/2025-05-01T12:00:00"
    assert make_trial_start_and_stop(temp_covg) == (
        "Use 2015-09-01T12:11:00 as default value.",
        "Data is available up to 2025-05-01T12:00:00. Use 2015-09-01T12:12:00 as a test end value.",
    )

    # Negative case: If there is no temporalCoverage provided/found, the function will
    # return None.
    assert make_trial_start_and_stop(None) == (None, None)


def test_find_match_returns_expected_value():
    """Test that the find_match function returns the expected value."""

    # Positive case: A matching contact is found, so its role is added to the
    # corresponding entry in the given list of author roles, and, in the
    # dictionary of contacts, the role value is replaced with the formatted person name.

    person = "Gurnett, Donald, A."
    author_role = ["Author"]
    contacts_list = {
        "spase://SMWG/Person/Donald.A.Gurnett": ["PrincipalInvestigator"],
        "spase://SMWG/Person/Jolene.S.Pickett": ["FormerPI"],
    }
    assert find_match(contacts_list, person, author_role) == (
        {
            "spase://SMWG/Person/Donald.A.Gurnett": "Gurnett, Donald A.",
            "spase://SMWG/Person/Jolene.S.Pickett": ["FormerPI"],
        },
        [["Author", "PrincipalInvestigator"]],
    )

    # Negative case: If no contact info is given, the function will
    # return None.
    assert find_match(None, None, None) == (None, None)
