"""Test additional SPASE module functions and methods."""

from lxml import etree
from soso.strategies.spase import (get_schema_version, get_authors, get_accessURLs,
                                   get_dates, get_repoID, get_alternate_name, contributorFormat,
                                   nameSplitter, get_measurement_type, get_information_url,
                                   get_instrument, get_observatory, get_cadenceContext)
from soso.utilities import get_empty_metadata_file_path, get_example_metadata_file_path


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
    # file, as well as their roles, the publication date, the publisher, contributors, publication title,
    # and backup contacts (names and roles) which are not considered authors
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_authors(spase) == (["Fuselier, Stephen, A.; Young, David, T.; Gomez, Roman, G.; Burch, James, L."], ["Author"],
                                  "2022-01-01 00:00:00", "NASA Space Physics Data Facility", [], "",
                                  {'spase://SMWG/Person/Stephen.A.Fuselier': ['InstrumentLead', 'CoInvestigator'],
                                   'spase://SMWG/Person/David.T.Young': ['InstrumentLead', 'CoInvestigator'],
                                   'spase://SMWG/Person/Roman.G.Gomez': ['CoInvestigator'],
                                   'spase://SMWG/Person/James.L.Burch': [],
                                   'spase://SMWG/Person/MMS_SDC_POC': ['HostContact'],
                                   'spase://SMWG/Person/Robert.M.Candey': ['MetadataContact'],
                                   'spase://SMWG/Person/Lee.Frost.Bargatze': ['MetadataContact']})

    # Negative case: If the authors, author roles, publication date, publisher, contributors, publication title,
    # and backup contacts are not present, the function will return null/empty values.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_authors(spase) == ([], [], "", "", [], "", {})

def test_get_accessURLs_returns_expected_value():
    """Test that the get_accessURLs function returns the expected value."""

    # Positive case: The function will return AccessURLs found in the SPASE record, separated into two dictionaries,
    # with the keys as the url and the values to be a list containing their data format(s) (and product key if applicable)
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_accessURLs(spase) == ({'ftps://lasp.colorado.edu/mms/sdc/public/data/mms4/hpca/brst/l2/ion/': ['CDF'],
                                      'https://lasp.colorado.edu/mms/sdc/public/data/mms4/hpca/brst/l2/ion/': ['CDF'],
                                      'ftps://spdf.gsfc.nasa.gov/pub/data/mms/mms4/hpca/brst/l2/ion/': ['CDF'],
                                      'https://spdf.gsfc.nasa.gov/pub/data/mms/mms4/hpca/brst/l2/ion/': ['CDF']},
                                      {'https://cdaweb.gsfc.nasa.gov/cgi-bin/eval2.cgi?dataset=MMS4_HPCA_BRST_L2_ION&index=sp_phys':
                                       ['CDF', ['MMS4_HPCA_BRST_L2_ION']],
                                       'https://cdaweb.gsfc.nasa.gov/hapi': ['CSV', ['MMS4_HPCA_BRST_L2_ION']]})

    # Negative case: If the access_URLs are not present, the function will
    # return empty/null values.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_accessURLs(spase) == ({}, {})

def test_get_dates_returns_expected_value():
    """Test that the get_dates function returns the expected value."""

    # Positive case: The function will return the release date and 
    # the list of all dates in revision history of the SPASE file.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_dates(spase) == ("2023-03-04 12:34:56", ["2021-04-27 15:38:11",
                                "2022-08-04 12:34:56", "2023-03-04 12:34:56"])

    # Negative case: If the schema version is not present, the function will
    # return null/empty values
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_dates(spase) == ("", [])

def test_get_repoID_returns_expected_value():
    """Test that the get_repoID function returns the expected value."""

    # Positive case: The function will return the repositoryID found in the 
    # last AccessInformation section of the SPASE file.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_repoID(spase) == "spase://SMWG/Repository/NASA/GSFC/SPDF/CDAWeb"

    # Negative case: If there are no repositoryIDs found, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_repoID(spase) is None

def test_contributorFormat_returns_expected_value():
    """Test that the contributorFormat function returns the expected value."""

    # Positive case: The function will return the correctly formatted entry to be added
    # to the contributors list.
    roleName = "GeneralContact"
    name = "John H. Smith"
    givenName = "John H."
    familyName = "Smith"
    assert contributorFormat(roleName, name, givenName, familyName) == {"@type": "Role",
                                                                        "roleName": "GeneralContact",
                                                                        "contributor": {
                                                                            "@type": "Person",
                                                                            "name": "John H. Smith",
                                                                            "givenName": "John H.",
                                                                            "familyName": "Smith"}
                                                                        }

    # Negative case: If no contact info is given, the function will
    # return None.
    assert contributorFormat(None, None, None, None) is None

def test_nameSplitter_returns_expected_value():
    """Test that the nameSplitter function returns the expected value."""

    # Positive case: The function will return the full name, givenName, and familyName of the Contact provided.
    person = "spase://SMWG/Person/John.H.Smith"
    assert nameSplitter(person) == ("John H. Smith", "John H.", "Smith")

    # Negative case: If no contact info is given, the function will
    # raise an error.
    try:
        nameSplitter(None, None, None, None)
    except ValueError as error:
        assert "This function only takes a nonempty string as an argument" in str(error)
    try:
        nameSplitter("", "", "", "")
    except ValueError as error:
        assert "This function only takes a nonempty string as an argument" in str(error)

def test_get_measurement_type_returns_expected_value():
    """Test that the get_measurement_type function returns the expected value."""

    # Positive case: The function will return the MeasurementType(s) found in the SPASE
    # file.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_measurement_type(spase) == {'@type': 'DefinedTerm', 'keywords': ['EnergeticParticles', 'MagneticField']}

    # Negative case: If the schema version is not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_measurement_type(spase) is None

def test_get_information_url_returns_expected_value():
    """Test that the get_information_url function returns the expected value."""

    # Positive case: The function will return the name, description, and url for the
    # InformationURL(s) found in the SPASE file.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_information_url(spase) == [{'name': '''The Magnetospheric Multiscale (MMS) Mission home page at
                                           Goddard Space Flight Center (GSFC)''', 'url': 'https://mms.gsfc.nasa.gov/',
                                           'description': '''The Magnetospheric Multiscale (MMS) Mission Home Page 
                                           hosted by the Goddard Space Flight Center (GSFC).'''},
                                           {'name': 'Data Caveats and Current Release Notes at LASP MMS SDC',
                                            'url': 'https://lasp.colorado.edu/mms/sdc/public/datasets/hpca/',
                                            'description': '''The Magnetospheric Multiscale (MMS) Mission home page
                                            hosted by the Laboratory of Atmospheric and Space Physics, Science Data
                                            Center (LASP, SDC) at the University of Colorado, Boulder.'''}]

    # Negative case: If the schema version is not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_information_url(spase) is None

def test_get_instrument_returns_expected_value():
    """Test that the get_instrument function returns the expected value."""

    # Positive case: The function will return the name, ResourceID, and InformationURL(s) for the
    # InstrumentID(s) found in the SPASE file.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_instrument(spase) == [{"@type": "IndividualProduct",
                                    "identifier": "spase://SMWG/Instrument/MMS/4/FIELDS/FGM",
                                    "name": "MMS 4 FIELDS Suite, Fluxgate Magnetometer (FGM) Instrument",
                                    "url": [
                                    "https://www.nasa.gov/mission_pages/mms/spacecraft/mms-instruments.html"]},
                                    {"@type": "IndividualProduct",
                                    "identifier": "spase://SMWG/Instrument/MMS/4/HotPlasmaCompositionAnalyzer",
                                    "name": "MMS 4 Hot Plasma Composition Analyzer (HPCA) Instrument",
                                    "url": [
                                    "https://www.nasa.gov/mission_pages/mms/spacecraft/mms-instruments.html"]}
                                    ]

    # Negative case: If the schema version is not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_instrument(spase) is None

def test_get_observatory_returns_expected_value():
    """Test that the get_observatory function returns the expected value."""

    # Positive case: The function will return the name, ResourceID, and InformationURL(s) for the
    # observatoryID(s) found in the SPASE file.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_observatory(spase) == [{"@type": "ResearchProject",
                                    "@id": "spase://SMWG/Observatory/MMS",
                                    "name": "MMS",
                                    "url": ["https://mms.gsfc.nasa.gov/"]},
                                    {"@type": "ResearchProject",
                                    "@id": "spase://SMWG/Observatory/MMS/4",
                                    "name": "MMS-4",
                                    "url": ["https://mms.gsfc.nasa.gov/"]},
                                    {"@type": "ResearchProject",
                                    "@id": "spase://SMWG/Observatory/MMS",
                                    "name": "MMS",
                                    "url": ["https://mms.gsfc.nasa.gov/"]},
                                    {"@type": "ResearchProject",
                                    "@id": "spase://SMWG/Observatory/MMS/4",
                                    "name": "MMS-4",
                                    "url": ["https://mms.gsfc.nasa.gov/"]}
                                    ]

    # Negative case: If the schema version is not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_observatory(spase) is None

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

def test_get_cadenceContext_returns_expected_value():
    """Test that the get_cadenceContext function returns the expected value."""

    # Positive case: The function will return a description of the Cadence
    # found within the TemporalDescription section of the SPASE record.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_cadenceContext(spase) == "This means that the time series is periodic with a 0.625 second cadence"

    # Negative case: If Cadence is not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_cadenceContext(spase) is None