"""The SPASE strategy module."""

from lxml import etree
from soso.interface import StrategyInterface
from soso.utilities import (
    delete_null_values,
)
from typing import Union, List, Dict

# pylint: disable=duplicate-code


class SPASE(StrategyInterface):
    """Define the conversion strategy for SPASE (Space Physics Archive Search
    and Extract).

    Attributes:
        file: The path to the metadata file. This should be an XML file in
            SPASE format.
        schema_version: The version of the SPASE schema used in the metadata
            file.
        kwargs: Additional keyword arguments for handling unmappable
            properties. See the Notes section below for details.

    Notes:
        Some properties of this metadata standard don't directly map to SOSO.
        However, these properties can still be included by inputting the
        information as `kwargs`. Keys should match the property name, and
        values should be the desired value. For a deeper understanding of each
        SOSO property, refer to the `SOSO guidelines
        <https://github.com/ESIPFed/science-on-schema.org/blob/master/guides/Dataset.md>`_.

        Below are unmappable properties for this strategy:
            - [includedInDataCatalog]
            - [version]
    """

    def __init__(self, file: str, **kwargs: dict):
        """Initialize the strategy."""
        file = str(file)  # incase file is a Path object
        if not file.endswith(".xml"):  # file should be XML
            raise ValueError(file + " must be an XML file.")
        super().__init__(metadata=etree.parse(file))
        self.file = file
        self.schema_version = get_schema_version(self.metadata)
        self.namespaces = {"spase": "http://www.spase-group.org/data/schema"}
        self.kwargs = kwargs
        self.root = self.metadata.getroot()

    def get_id(self) -> str:
        # Mapping: schema:identifier = spase:ResourceID
        dataset_id = self.metadata.findtext(
            ".//spase:NumericalData/spase:ResourceID", namespaces=self.namespaces
        )
        return delete_null_values(dataset_id)

    def get_name(self) -> str:
        # Mapping: schema:description = spase:ResourceHeader/spase:ResourceName
        name = self.metadata.findtext(
            ".//spase:NumericalData/spase:ResourceHeader/spase:ResourceName",
            namespaces=self.namespaces,
        )
        return delete_null_values(name)

    def get_description(self) -> str:
        # Mapping: schema:description = spase:ResourceHeader/spase:Description
        description = self.metadata.findtext(
            ".//spase:NumericalData/spase:ResourceHeader/spase:Description",
            namespaces=self.namespaces,
        )
        return delete_null_values(description)

    # will need to make general for all SPASE record categories eventually
    def get_url(self) -> str:
        # Mapping: schema:url = spase:ResourceHeader/spase:DOI (or https://hpde.io landing page, if no DOI)
        url = self.metadata.findtext(
            ".//spase:NumericalData/spase:ResourceHeader/spase:DOI",
            namespaces=self.namespaces,
        )
        if delete_null_values(url) is None:
            url = self.metadata.findtext(
                ".//spase:NumericalData/spase:ResourceID", namespaces=self.namespaces
            ).replace("spase://", "https://hpde.io/")
        return delete_null_values(url)

    def get_same_as(self) -> None:
        same_as = None
        return delete_null_values(same_as)

    def get_version(self) -> None:
        version = None
        return delete_null_values(version)

    # commented out partial code that was put on hold due to licenses being added to SPASE soon
    def get_is_accessible_for_free(self) -> bool:
        """schema:description: spase:AccessInformation/AccessRights"""
        is_accessible_for_free = None
        # local vars needed
        #access = ""

        # iterate thru to find AccessInfo
        #for child in self.root[1]:
        #    if access == "Open":
        #        break
        #    if child.tag.endswith("AccessInformation"):
        #        targetChild = child
                # iterate thru to find AccessRights
        #        for child in targetChild:
        #            if child.tag.endswith("AccessRights"):
        #                access = child.text 
        #if access == "Open":
        #    is_accessible_for_free = True
        #else:
        #    is_accessible_for_free = False
        return delete_null_values(is_accessible_for_free)

    def get_keywords(self) -> Union[str, None]:
        keywords = None
        for child in self.root[1]:
            if child.tag.endswith("Keyword"):
                keywords = child.text
        return delete_null_values(keywords)

    def get_identifier(self) -> Union[tuple, None]:
        # Mapping: schema:identifier = spase:ResourceHeader/spase:DOI (or https://hpde.io landing page, if no DOI)
        url = self.get_url()
        # if SPASE record has a DOI
        if "doi" in url:
            temp = url.split("/")
            value = "doi:" + "/".join(temp[3:])
            identifier = {"@id": f"{url}",
                        "@type" : "PropertyValue",
                        "propertyID": "https://registry.identifiers.org/registry/doi",
                        "value": f"{value}",
                        "url": f"{url}"}
        # if SPASE record only has landing page instead
        else:
            identifier = url
        return identifier

    def get_citation(self) -> Union[str, None]:
        # Mapping: schema:citation = spase:ResourceHeader/spase:PublicationInfo/spase:Authors
        # AND spase:ResourceHeader/spase:PublicationInfo/spase:PublicationDate
        # AND spase:ResourceHeader/spase:PublicationInfo/spase:PublishedBy
        # AND spase:ResourceHeader/spase:PublicationInfo/spase:Title
        # AND spase:ResourceHeader/spase:DOI

        # local vars needed
        author = ""
        pubDate = ""
        pub = ""
        dataset = ""

        author, authorRole, pubDate, pub, dataset = get_authors(self.metadata)
        authorStr = str(author)
        authorStr = authorStr.replace("[", "").replace("]","")
        authorStr = authorStr.replace("'","")
        # if author was pulled from ContactID
        if ";" not in authorStr:
            if "Person/" in authorStr:
                path, sep, authorStr = authorStr.partition("Person/")
                givenName, sep, familyName = authorStr.partition(".")
                initial, sep, familyName = familyName.partition(".")
                givenName = givenName + ', ' + initial + '.'
                authorStr = familyName + ", " + givenName
        else:
            authorStr = authorStr.replace(";", ",")

        # assign backup values if not found in desired locations
        if pub == '':
            pub = "NASA Heliophysics Digital Resource Library"
        if pubDate == "":
            # iterate thru to find ResourceHeader
            for child in self.root[1]:
                if child.tag.endswith("ResourceHeader"):
                    targetChild = child
                    # iterate thru to find ReleaseDate (temp pubYr)
                    for child in targetChild:
                        if child.tag.endswith("ReleaseDate"):
                            pubDate = child.text[:4]
        DOI = self.get_url()
        if dataset:
            citation = f"{authorStr} ({pubDate}). {dataset}. {pub}. {DOI}"
        else:
            citation = f"{authorStr} ({pubDate}). {pub}. {DOI}"
        return delete_null_values(citation)

    def get_variable_measured(self) -> None:
        variable_measured = None
        return delete_null_values(variable_measured)

    def get_included_in_data_catalog(self) -> None:
        included_in_data_catalog = None
        return delete_null_values(included_in_data_catalog)

    def get_subject_of(self) -> None:
        encoding_format = None
        return delete_null_values(encoding_format)

    def get_distribution(self) -> None:
        distribution = None
        return delete_null_values(distribution)

    def get_potential_action(self) -> None:
        potential_action = None
        return delete_null_values(potential_action)

    def get_date_created(self) -> None:
        date_created = None
        return delete_null_values(date_created)

    def get_date_modified(self) -> None:
        date_modified = None
        return delete_null_values(date_modified)

    def get_date_published(self) -> None:
        date_published = None
        return delete_null_values(date_published)

    def get_expires(self) -> None:
        expires = None
        return delete_null_values(expires)

    def get_temporal_coverage(self) -> None:
        temporal_coverage = None
        return delete_null_values(temporal_coverage)

    def get_spatial_coverage(self) -> Union[List[Dict], None]:
        # Mapping: schema:spatial_coverage = list of spase:NumericalData/spase:ObservedRegion/*
        # Each object is:
        #   {"@type": schema:Place, "@id": URI}
        # Using URIs, as defined in: https://github.com/polyneme/topst-spase-rdf-tools/blob/main/data/spase.owl
        spatial_coverage = []
        for item in self.metadata.findall(
            ".//spase:NumericalData/spase:ObservedRegion",
            namespaces=self.namespaces,
        ):
            spatial_coverage.append(
                {
                    "@type": "schema:Place",
                    "identifier": f"http://www.spase-group.org/data/schema/{item.text.replace('.', '_').upper()}",
                    "alternateName": item.text,
                }
            )
        return delete_null_values(spatial_coverage)

    def get_creator(self) -> Union[list, None]:
        # Mapping: schema:creator = spase:ResourceHeader/spase:PublicationInfo/spase:Authors 
        # OR schema:creator = spase:ResourceHeader/spase:Contact/spase:PersonID
        
        author, authorRole, pubDate, pub, dataset = get_authors(self.metadata)
        authorStr = str(author)
        authorStr = authorStr.replace("[", "").replace("]","")
        creator = []
        #print(authorStr)
        # if creators were found in Contact/PersonID
        if "Person/" in authorStr:
            # if multiple found, split them and iterate thru one by one
            authorStr = authorStr.split("',")
            for person in authorStr:
                path, sep, author = person.partition("Person/")
                # get rid of extra quotations
                author = author.replace("'","")
                # keep track of position so roles will match
                index = author.index(person)
                givenName, sep, familyName = author.partition(".")
                initial, sep, familyName = familyName.partition(".")
                givenName = givenName + ' ' + initial + '.'
                creator.append({"@type": "Role", 
                                "roleName": f"{authorRole[index]}",
                                "creator": {"@type": "Person",
                                            "name": f"{author}",
                                            "givenName": f"{givenName}",
                                            "familyName": f"{familyName}"}
                                            })
        # if all creators were found in PublicationInfo/Authors
        else:
            # if there are multiple authors
            if (";" in authorStr) or (".," in authorStr):
                if (";" in authorStr):
                    author = authorStr.split(";")
                else:
                    author = authorStr.split("., ")
                # iterate over each person in author string
                for person in author:
                    # get rid of extra quotations
                    person = person.replace("'","")
                    # if first name is abbreviated
                    if (not person.endswith(".")):
                        person += "."
                    # remove 'and' from name
                    if "and " in person:
                        person = person.replace("and ", "")
                    if authorRole == ["Author"]:
                        familyName, sep, givenName = person.partition(", ")
                        creator.append({"@type": "Role", 
                                        "roleName": f"{authorRole[0]}",
                                        "creator": {"@type": "Person",
                                                    "name": f"{person}",
                                                    "givenName": f"{givenName}",
                                                    "familyName": f"{familyName}"}
                                                    })
            # if there is only one author listed
            else:
                # get rid of extra quotations
                person = authorStr.replace("'","")
                if authorRole == ["Author"]:
                    familyName, sep, givenName = person.partition(",")
                    creator.append({"@type": "Role", 
                                    "roleName": f"{authorRole[0]}",
                                    "creator": {"@type": "Person",
                                                "name": f"{person}",
                                                "givenName": f"{givenName}",
                                                "familyName": f"{familyName}"}
                                                })
        return delete_null_values(creator)

    def get_contributor(self) -> None:
        contributor = None
        return delete_null_values(contributor)

    def get_provider(self) -> None:
        provider = None
        return delete_null_values(provider)

    def get_publisher(self) -> None:
        publisher = None
        return delete_null_values(publisher)

    def get_funding(self) -> None:
        funding = None
        return delete_null_values(funding)

    def get_license(self) -> None:
        license_url = None
        return license_url

    def get_was_revision_of(self) -> None:
        was_revision_of = None
        return delete_null_values(was_revision_of)

    def get_was_derived_from(self) -> None:
        was_derived_from = None
        return delete_null_values(was_derived_from)

    def get_is_based_on(self) -> None:
        is_based_on = None
        return delete_null_values(is_based_on)

    def get_was_generated_by(self) -> None:
        was_generated_by = None
        return delete_null_values(was_generated_by)


# Below are utility functions for the SPASE strategy.


def get_schema_version(metadata: etree.ElementTree) -> str:
    """
    :param metadata:    The SPASE metadata object as an XML tree.

    :returns:   The version of the SPASE schema used in the metadata record.
    """
    schema_version = metadata.findtext(
        "{http://www.spase-group.org/data/schema}Version"
    )
    return schema_version

def get_authors(metadata: etree.ElementTree) -> tuple:
    """
    :param metadata:    The SPASE metadata object as an XML tree.
    
    :returns: The highest priority authors found within the SPASE record as a list
                as well as a list of their roles, respectively.
    """
    # local vars needed
    author = []
    authorRole = []
    pubDate = ""
    pub = ""
    dataset = ""
    PI_child = None
    priority = False
    root = metadata.getroot()
    # holds role values that are not considered for author var
    UnapprovedAuthors = ["MetadataContact", "ArchiveSpecialist",
                        "HostContact", "Publisher", "User"]

    # iterate thru to find ResourceHeader
    for child in root[1]:
        if child.tag.endswith("ResourceHeader"):
            targetChild = child
            # iterate thru to find PublicationInfo
            for child in targetChild:
                if child.tag.endswith("PublicationInfo"):
                    PI_child = child
                elif child.tag.endswith("Contact"):
                    C_Child = child
                    # iterate thru Contact to find PersonID and Role
                    for child in C_Child:
                        # find PersonID
                        if child.tag.endswith("PersonID"):
                            # store PersonID
                            PersonID = child.text
                        # find Role
                        elif child.tag.endswith("Role"):
                            # backup author
                            if ("PrincipalInvestigator" or "PI") in child.text:
                                # if a lesser priority author found
                                #     first, overwrite author lists
                                if not priority and author:
                                    author = [PersonID]
                                    authorRole = [child.text]
                                else:
                                    author.append(PersonID)
                                    authorRole.append(child.text)
                                # mark that highest priority backup author was found
                                priority = True
                            # backup publisher
                            elif child.text == "Publisher":
                                pub = child.text
    if PI_child is not None:
        for child in PI_child:
            # collect preferred author
            if child.tag.endswith("Authors"):
                author = [child.text]
                authorRole = ["Author"]
            elif child.tag.endswith("PublicationDate"):
                pubDate = child.text
                pubDate = pubDate[:4]
            # collect preferred publisher
            elif child.tag.endswith("PublishedBy"):
                pub = child.text
            # collect preferred dataset
            elif child.tag.endswith("Title"):
                dataset = child.text
    return author, authorRole, pubDate, pub, dataset

def getPaths(entry, paths):
    """Takes the absolute path of a SPASE record directory to be walked
    to extract all SPASE records present. Returns these paths using the
    list parameter paths, which holds the absolute paths generated by
    the function.

    :param entry: A string of the absolute path of the SPASE record directory
                    to be searched/walked to find all SPASE records within.
    :type entry: String
    :param paths: A list to hold absolute paths of all SPASE records found
                    within the given directory
    :type paths: list
    :return: A list containing the absolute paths of all SPASE records found
                within the given directory.
    :rtype: list
    """
    import os
    if os.path.exists(entry):
        for root, dirs, files in os.walk(entry):
            if files:
                for file in files:
                    paths.append(root + "/" + file)
    else:
        print(entry + " does not exist")
    return paths

# list that holds SPASE records already checked
searched = []
SPASE_paths = []
folder = "C:/Users/zboqu/NASA Internship/NASA/NumericalData/ACE/EPAM"
SPASE_paths = getPaths(folder, SPASE_paths)
print("You entered " + folder)
if len(SPASE_paths) == 0:
    print("No records found. Returning.")
else:
    print("The number of records is " + str(len(SPASE_paths)))
#testSpase = SPASE("C:/Users/zboqu/NASA Internship/soso-spase/src/soso/data/spase.xml")
#testSpase = SPASE("C:/Users/zboqu/NASA Internship/NASA/NumericalData/Cassini/MAG/PT60S.xml")
    #iterate through all SPASE records returned by PathGrabber
    # TODO: figure out why an error occurs at this filePath
    for r, record in enumerate(SPASE_paths[24:30]):
        if record not in searched:
            # scrape metadata for each record
            statusMessage = f"Extracting metadata from record {r+1}"
            statusMessage += f" of {len(SPASE_paths)}"
            print(statusMessage)
            print(record)
            testSpase = SPASE(record)
            #print(testSpase.get_is_accessible_for_free())
            print(testSpase.get_citation())
            print(testSpase.get_identifier())
            result = testSpase.get_creator()
            for each in result:
                print(each)

            # add record to searched
            searched.append(record)