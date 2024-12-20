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

    def get_keywords(self) -> None:
        keywords = None
        return delete_null_values(keywords)

    def get_identifier(self) -> tuple:
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

    def get_citation(self) -> str:
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

        # iterate thru to find ResourceHeader
        for child in self.root[1]:
            if child.tag.endswith("ResourceHeader"):
                targetChild = child
                # iterate thru to find PublicationInfo
                for child in targetChild:
                    if child.tag.endswith("PublicationInfo"):
                        PI_child = child
                        for child in PI_child:
                            # collect preferred author
                            if child.tag.endswith("Authors"):
                                author = child.text
                                author = author.replace(";", ",")
                            elif child.tag.endswith("PublicationDate"):
                                pubDate = child.text
                                pubDate = pubDate[:4]
                            # collect preferred publisher
                            elif child.tag.endswith("PublishedBy"):
                                pub = child.text
                            # collect preferred dataset
                            elif child.tag.endswith("Title"):
                                dataset = child.text
        DOI = self.get_url()
        if dataset:
            citation = f"{author} ({pubDate}). {dataset}. {pub}. {DOI}"
        else:
            citation = f"{author} ({pubDate}). {pub}. {DOI}"
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

    def get_creator(self) -> list:
        # Mapping: schema:creator = spase:ResourceHeader/spase:PublicationInfo/spase:Authors 
        # OR schema:creator = spase:ResourceHeader/spase:Contact/spase:PersonID
        
        author, authorRole = get_authors(self.metadata)
        authorStr = str(author)
        authorStr = authorStr.replace("[", "").replace("]","")
        creator = []
        print(authorStr)
        if ";" in authorStr:
            author = authorStr.split(";")
        else:
            # unfinished: need to fix number of times loop runs since this runs up to num of chars in string
            path, sep, author = authorStr.partition("Person/")
        # iterate over each person in author string
        for person in author:
            # keep track of position so roles will match
            print(len(author))
            index = author.index(person)
            print(index)
            # get rid of extra quotations
            person = person.replace("'","")
            # if all creators were found in PublicationInfo/Authors
            if authorRole == ["Author"]:
                familyName, sep, givenName = person.partition(",")
                creator.append({"@type": "Role", 
                                "roleName": f"{authorRole[0]}",
                                "creator": {"@type": "Person",
                                            "name": f"{person}",
                                            "givenName": f"{givenName}",
                                            "familyName": f"{familyName}"}
                                            })
            else:
                givenName, sep, familyName = person.partition(".")
                initial, sep, familyName = familyName.partition(".")
                givenName = givenName + "." + initial
                creator.append({"@type": "Role", 
                                "roleName": f"{authorRole[index]}",
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
    if PI_child is not None:
        for child in PI_child:
            # collect preferred author
            if child.tag.endswith("Authors"):
                author = [child.text]
                authorRole = ["Author"]
    return author, authorRole

#testSpase = SPASE("C:/Users/zboqu/NASA Internship/soso-spase/src/soso/data/spase.xml")
testSpase = SPASE("C:/Users/zboqu/NASA Internship/NASA/NumericalData/Cassini/MAG/PT60S.xml")
#print(testSpase.get_is_accessible_for_free())
#print(testSpase.get_citation())
#print(testSpase.get_identifier())
result = testSpase.get_creator()
for each in result:
    print(each)