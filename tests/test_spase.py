"""Test additional SPASE module functions and methods."""

from lxml import etree
from soso.strategies.spase import *
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
    # backup contacts (names and roles) which are not considered authors, and any remaining contacts
    # with author roles not in PubInfo
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_authors(spase) == (['Fuselier, Stephen A.', 'Young, David T.', 'Gomez, Roman G.', 'Burch, James L.'],
                                    [['Author', 'CoInvestigator'], ['Author', 'CoInvestigator'],
                                        ['Author', 'CoInvestigator'], ['Author', 'PrincipalInvestigator']],
                                    '2022-01-01T00:00:00', 'Space Physics Data Facility', [], '',
                                    {'spase://SMWG/Person/Stephen.A.Fuselier': ['InstrumentLead'],
                                        'spase://SMWG/Person/David.T.Young': ['InstrumentLead'],
                                        'spase://SMWG/Person/Roman.G.Gomez': [], 'spase://SMWG/Person/James.L.Burch': [],
                                        'spase://SMWG/Person/Jolene.S.Pickett': [], 'spase://SMWG/Person/MMS_SDC_POC':
                                        ['HostContact'], 'spase://SMWG/Person/Robert.M.Candey': ['MetadataContact'],
                                        'spase://SMWG/Person/Lee.Frost.Bargatze': ['MetadataContact']},
                                    {'spase://SMWG/Person/Stephen.A.Fuselier': 'Fuselier, Stephen A.',
                                        'spase://SMWG/Person/David.T.Young': 'Young, David T.',
                                        'spase://SMWG/Person/Roman.G.Gomez': 'Gomez, Roman G.',
                                        'spase://SMWG/Person/James.L.Burch': 'Burch, James L.',
                                        'spase://SMWG/Person/Jolene.S.Pickett': ['PrincipalInvestigator']})

    # Negative case: If the authors, author roles, publication date, publisher, contributors, publication title,
    # and backup contacts are not present, the function will return null/empty values.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_authors(spase) == ([], [], "", "", [], "", {}, {})

def test_get_accessURLs_returns_expected_value():
    """Test that the get_accessURLs function returns the expected value."""

    # Positive case: The function will return AccessURLs found in the SPASE record, separated into two dictionaries,
    # with the keys as the url and the values to be a list containing their data format(s),
    # name, and product key (if applicable)
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_accessURLs(spase) == ({'https://spdf.gsfc.nasa.gov/pub/data/cassini/helio1day/' +
        'cassini_helio1day_position_19971016_v01.cdf': ['CDF', 'HTTPS from SPDF']}, 
        {'ftps://lasp.colorado.edu/mms/sdc/public/data/mms4/hpca/brst/l2/ion/':
            ['CDF', {'keys': [], 'name': 'FTPS from the MMS SDC (not with most browsers)'}],
        'https://lasp.colorado.edu/mms/sdc/public/data/mms4/hpca/brst/l2/ion/':
            ['CDF', {'keys': [], 'name': 'HTTPS from the MMS SDC'}],
        'ftps://spdf.gsfc.nasa.gov/pub/data/mms/mms4/hpca/brst/l2/ion/':
            ['CDF', {'keys': [], 'name': 'FTPS from SPDF (not with most browsers)'}],
        'https://cdaweb.gsfc.nasa.gov/cgi-bin/eval2.cgi?dataset=MMS4_HPCA_BRST_L2_ION&index=sp_phys':
            ['CDF', {'keys': ['MMS4_HPCA_BRST_L2_ION'], 'name': 'CDAWeb'}],
        'https://cdaweb.gsfc.nasa.gov/hapi': ['CSV', {'keys': ['MMS4_HPCA_BRST_L2_ION'],
            'name': 'CDAWeb HAPI Server'}]})

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

def test_personFormat_returns_expected_value():
    """Test that the personFormat function returns the expected value."""

    # Positive case: The function will return the correctly formatted entry to be added
    # to the contributors list.
    type = "contributor"
    roleName = "GeneralContact"
    name = "John H. Smith"
    givenName = "John H."
    familyName = "Smith"
    assert personFormat(type, roleName, name, givenName, familyName) == {"@type": "Role",
                                                                        "roleName": "GeneralContact",
                                                                        "contributor": {
                                                                            "@type": "Person",
                                                                            "name": "John H. Smith",
                                                                            "givenName": "John H.",
                                                                            "familyName": "Smith"}
                                                                        }

    # Negative case: If no contact info is given, the function will
    # return None.
    assert personFormat(None, None, None, None, None) is None

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

def test_get_measurementMethod_returns_expected_value():
    """Test that the get_measurementMethod function returns the expected value."""

    # Positive case: The function will return the MeasurementType(s) found in the SPASE
    # file.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_measurementMethod(spase) == [
        {
            "@type": "DefinedTerm",
            "inDefinedTermSet": {
                "@type": "DefinedTermSet",
                "name": "SPASE MeasurementType"
            },
            "name": "Energetic Particles",
            "termCode": "EnergeticParticles"
        },
        {
            "@type": "DefinedTerm",
            "inDefinedTermSet": {
                "@type": "DefinedTermSet",
                "name": "SPASE MeasurementType"
            },
            "name": "Magnetic Field",
            "termCode": "MagneticField"
        }
    ]

    # Negative case: If the schema version is not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_measurementMethod(spase) is None

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
    kwargs = {"testing": "soso-spase/tests/data/"}
    assert get_instrument(spase, get_example_metadata_file_path("SPASE"), **kwargs) == (
        {'@id': 'https://hpde.io/SMWG/Instrument/MMS/4/FIELDS/FGM',
        '@type': ['IndividualProduct', 'prov:Entity', 'sosa:System'],
        'identifier':
            {'@id': 'https://hpde.io/SMWG/Instrument/MMS/4/FIELDS/FGM',
                '@type': 'PropertyValue',
                'propertyID': 'SPASE Resource ID',
                'value': 'spase://SMWG/Instrument/MMS/4/FIELDS/FGM'},
        'name': 'MMS 4 FIELDS Suite, Fluxgate Magnetometer (FGM) Instrument',
        'url': 'https://hpde.io/SMWG/Instrument/MMS/4/FIELDS/FGM'})
    """{'@id': 'https://hpde.io/SMWG/Instrument/MMS/4/HotPlasmaCompositionAnalyzer',
                                        '@type': ['IndividualProduct', 'prov:Entity', 'sosa:System'],
                                        'identifier':
                                            {'@id': 'https://hpde.io/SMWG/Instrument/MMS/4/HotPlasmaCompositionAnalyzer',
                                                '@type': 'PropertyValue', 'propertyID': 'SPASE Resource ID',
                                                'value': 'spase://SMWG/Instrument/MMS/4/HotPlasmaCompositionAnalyzer'},
                                        'name': 'MMS 4 Hot Plasma Composition Analyzer (HPCA) Instrument',
                                        'url': 'https://hpde.io/SMWG/Instrument/MMS/4/HotPlasmaCompositionAnalyzer'}]"""

    # Negative case: If the schema version is not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_instrument(spase) is None

def test_get_observatory_returns_expected_value():
    """Test that the get_observatory function returns the expected value."""

    # Positive case: The function will return the name, ResourceID, and InformationURL(s) for the
    # observatoryID(s) found in the SPASE file.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    kwargs = {"testing": "soso-spase/tests/data/"}
    assert get_observatory(spase, get_example_metadata_file_path("SPASE"), **kwargs) == ([
        {'@type': ['ResearchProject', 'prov:Entity', 'sosa:Platform'],
        '@id': 'https://hpde.io/SMWG/Observatory/MMS',
        'name': 'MMS',
        'identifier':
            {'@id': 'https://hpde.io/SMWG/Observatory/MMS',
            '@type': 'PropertyValue',
            'propertyID': 'SPASE Resource ID',
            'value': 'spase://SMWG/Observatory/MMS'},
        'url': 'https://hpde.io/SMWG/Observatory/MMS'},
        {'@type': ['ResearchProject', 'prov:Entity', 'sosa:Platform'],
        '@id': 'https://hpde.io/SMWG/Observatory/MMS/4',
        'name': 'MMS-4',
        'identifier':
            {'@id': 'https://hpde.io/SMWG/Observatory/MMS/4',
                '@type': 'PropertyValue',
                'propertyID': 'SPASE Resource ID',
                'value': 'spase://SMWG/Observatory/MMS/4'},
        'url': 'https://hpde.io/SMWG/Observatory/MMS/4'}])

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
    assert get_cadenceContext(spase) == "The time series is periodic with a 0.625 second cadence"

    # Negative case: If Cadence is not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_cadenceContext(spase) is None

def test_get_mentions_returns_expected_value():
    """Test that the get_mentions function returns the expected value."""

    # Positive case: The function will return info about the SPASE ResourceIDs with the
    # AssociationType = "Other" found within the Association section of the SPASE record.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    kwargs = {"testing": "soso-spase/tests/data/"}
    assert get_mentions(spase, **kwargs) == (
        {"@id": "https://doi.org/10.48322/xhe6-5a16",
            "@type": "Dataset",
            "identifier": "https://doi.org/10.48322/xhe6-5a16",
            "url": "https://doi.org/10.48322/xhe6-5a16"})
    """{
            "@id": "https://doi.org/10.48322/2ry9-3s59",
            "@type": "Dataset",
            "identifier": "https://doi.org/10.48322/2ry9-3s59"
        }
    ]"""

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
        "identifier": "https://doi.org/10.48322/s9mg-he04",
        "url": "https://doi.org/10.48322/s9mg-he04"
    }

    # Negative case: If PartOf AssociationIDs are not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_is_part_of(spase) is None

def test_get_ORCiD_and_Affiliation_returns_expected_value():
    """Test that the get_ORCiD_and_Affiliation function returns the expected value."""

    # Positive case: The function will return the ORCiD and organization (with its ror)
    #   associated with the given SPASE Person.
    person = "spase://SMWG/Person/David.T.Young"
    kwargs = {"testing": "soso-spase/tests/data/"}
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_ORCiD_and_Affiliation(person, spase, **kwargs) == ("0000-0001-9473-7000",
        "Southwest Research Institute", "03tghng59")

    # Negative case: If no person information is provided, the function will
    # return None.
    assert get_ORCiD_and_Affiliation(None, None, None) is None

def test_get_temporal_returns_expected_value():
    """Test that the get_temporal function returns the expected value."""

    # Positive case: The function will return the Cadence
    # found within the TemporalDescription section of the SPASE record,
    # as well as a human-readable description of it.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_temporal(spase) == [
        "The time series is periodic with a 0.625 second cadence",
        "PT0.625S"
    ]

    # Negative case: If Cadence is not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_temporal(spase) is None

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

    # Positive case: The function will return the correctly formatted entry to be added
    # to the creators and/or contributors list.
    author = ['Fuselier, Stephen, A.; Young, David, T.; Gomez, Roman, G.; Burch, James, L.']
    authorRole = ['Author']
    contactsList = {'spase://SMWG/Person/Stephen.A.Fuselier': ['CoInvestigator'],
                    'spase://SMWG/Person/David.T.Young': ['CoInvestigator'],
                    'spase://SMWG/Person/Roman.G.Gomez': ['CoInvestigator'],
                    'spase://SMWG/Person/James.L.Burch': ['PrincipalInvestigator'],
                    'spase://SMWG/Person/Jolene.S.Pickett': ['PrincipalInvestigator']}
    assert process_authors(author, authorRole, contactsList) == (
        ['Fuselier, Stephen A.', 'Young, David T.', 'Gomez, Roman G.', 'Burch, James L.'],
        [['Author', 'CoInvestigator'], ['Author', 'CoInvestigator'], ['Author', 'CoInvestigator'],
            ['Author', 'PrincipalInvestigator']],
        {'spase://SMWG/Person/Stephen.A.Fuselier': 'Fuselier, Stephen A.',
            'spase://SMWG/Person/David.T.Young': 'Young, David T.',
            'spase://SMWG/Person/Roman.G.Gomez': 'Gomez, Roman G.',
            'spase://SMWG/Person/James.L.Burch': 'Burch, James L.',
            'spase://SMWG/Person/Jolene.S.Pickett': ['PrincipalInvestigator']})

    # Negative case: If no contact info is given, the function will
    # return None.
    assert process_authors(None, None, None) is None

def test_verifyType_returns_expected_value():
    """Test that the verifyType function returns the expected value."""

    # Positive cases: The function will return True or False for the first value 
    # depending on if the URL is a link to a Dataset.
    # Case 1: hpde.io landing page URL to a Dataset is provided
    url = "https://hpde.io/NASA/NumericalData/MMS/4/HotPlasmaCompositionAnalyzer/Burst/Level2/Ion/PT0.625S.html"
    assert verifyType(url) == (True, False, True, {})

    # Case 2: DOI that resolves to an hpde.io landing page is provided
    url = "https://doi.org/10.48322/6cfb-rq65"
    assert verifyType(url) == (True, False, True, {})

    # Case 3: DOI that does not resolve to an hpde.io landing page (nor is a Dataset) is provided
    url = "https://doi.org/10.5281/zenodo.13287868"
    assert verifyType(url) == (False, False, False, {})

    # Case 4: hpde.io landing page URL to a non-Dataset is provided
    url = "https://hpde.io/SMWG/Instrument/ACE/MAG.html"
    assert verifyType(url) == (False, False, True, {})

    # Case 5: DOI that does not resolve to an hpde.io landing page (but still to a Dataset) is provided
    url = "https://doi.org/10.5067/SeaBASS/TURBID9/DATA001"
    assert verifyType(url) == (True, False, False,
        {"name": "Turbid9",
        "description": "No description currently available for https://doi.org/10.5067/SeaBASS/TURBID9/DATA001"})

    # Case 6: DOI that does not resolve to an hpde.io landing page (but still to a JournalArticle) is provided
    url = "https://doi.org/10.1007/s11214-014-0119-6"
    assert verifyType(url) == (False, True, False, {})

    # Negative case: If no related info is given, the function will
    # return None.
    assert verifyType(None) is None

def test_get_ResourceID_returns_expected_value():
    """Test that the get_ResourceID function returns the expected value."""

    # Positive case: The function will return the Resource ID of the SPASE
    # dataset.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    assert get_ResourceID(spase) == "spase://NASA/NumericalData/MMS/4/HotPlasmaCompositionAnalyzer/Burst/Level2/Ion/PT0.625S"

    # Negative case: If the Resource ID is not present, the function will
    # return None.
    spase = etree.parse(get_empty_metadata_file_path("SPASE"))
    assert get_ResourceID(spase) is None

def test_get_relation_returns_expected_value():
    """Test that the get_relation function returns the expected value."""

    # Positive case: The function will return info about the SPASE ResourceIDs with the
    # given AssociationType found within the Association section of the SPASE record.
    spase = etree.parse(get_example_metadata_file_path("SPASE"))
    kwargs = {"testing": "soso-spase/tests/data/"}
    root = spase.getroot()
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desiredRoot = elt
    
    assert get_relation(desiredRoot, ["PartOf"], **kwargs) == {
        "@id": "https://doi.org/10.48322/s9mg-he04",
        "@type": "Dataset",
        "identifier": "https://doi.org/10.48322/s9mg-he04",
        "url": "https://doi.org/10.48322/s9mg-he04"
    }

    # Negative case: If no relation is given, the function will
    # return None.
    assert get_relation(None, None) is None

def test_updateLog_returns_expected_value():
    """Test that the updateLog function returns the expected value."""

    # Positive case: The function will update the log file by adding the
    #   repository name given.
    from pathlib import Path

    # get current working directory
    cwd = str(Path.cwd())
    # create log file that holds name of repos needed
    with open(f"{cwd}/requiredRepos.txt", "w") as f:
        f.write("Please git clone the following SPASE repositories in your home directory "
        "for the script to run as intended:")
    updateLog(cwd, "testRepo")
    with open(f"{cwd}/requiredRepos.txt", "r") as f:
        text = f.read()
    assert "testRepo" in text

    # Negative case: If there is no file nor attempt number present, the function will
    # return None.
    assert updateLog(None, None) is None