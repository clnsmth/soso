"""The SPASE strategy module."""

from lxml import etree
from soso.interface import StrategyInterface
from soso.utilities import (
    delete_null_values
)
from typing import Union, List, Dict
import re
from datetime import datetime, timedelta
import json
import os
import requests
from pathlib import Path
import time

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
            - includedInDataCatalog
            - is_accessible_for_free
            - version
            - expires
            - provider
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
        # find element in tree to iterate over
        for elt in self.root.iter(tag=etree.Element):
            if (elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData")
                or elt.tag.endswith("Observatory") or elt.tag.endswith("Instrument")):
                self.desiredRoot = elt
        # if want to see entire xml file as a string
        #print(etree.tostring(self.desiredRoot, pretty_print = True).decode(), end=' ')

    def get_id(self) -> str:
        # Mapping: schema:identifier = hpde.io landing page for the SPASE record
        ResourceID = get_ResourceID(self.metadata, self.namespaces)
        hpdeURL = ResourceID.replace("spase://", "https://hpde.io/")

        return delete_null_values(hpdeURL)

    def get_name(self) -> str:
        # Mapping: schema:name = spase:ResourceHeader/spase:ResourceName
        desiredTag = self.desiredRoot.tag.split("}")
        SPASE_Location = ".//spase:" + f"{desiredTag[1]}/spase:ResourceHeader/spase:ResourceName"
        name = self.metadata.findtext(
            SPASE_Location,
            namespaces=self.namespaces,
        )
        return delete_null_values(name)

    def get_description(self) -> str:
        # Mapping: schema:description = spase:ResourceHeader/spase:Description
        desiredTag = self.desiredRoot.tag.split("}")
        SPASE_Location = ".//spase:" + f"{desiredTag[1]}/spase:ResourceHeader/spase:Description"
        description = self.metadata.findtext(
            SPASE_Location,
            namespaces=self.namespaces,
        )
        return delete_null_values(description)

    def get_url(self) -> str:
        # Mapping: schema:url = spase:ResourceHeader/spase:DOI (or https://hpde.io landing page, if no DOI)
        desiredTag = self.desiredRoot.tag.split("}")
        SPASE_Location = ".//spase:" + f"{desiredTag[1]}/spase:ResourceHeader/spase:DOI"
        url = self.metadata.findtext(
            SPASE_Location,
            namespaces=self.namespaces,
        )
        if delete_null_values(url) is None:
            url = self.get_id()
        return delete_null_values(url)

    def get_same_as(self) -> Union[List, None]:
        # Mapping: schema:sameAs = spase:ResourceHeader/spase:PriorID
        same_as = []

        # traverse xml to extract needed info
        for child in self.desiredRoot.iter(tag=etree.Element):
            if child.tag.endswith("PriorID"):
                same_as.append(child.text)
        if same_as == []:
            same_as = None
        elif len(same_as) == 1:
            same_as = same_as[0]
        return delete_null_values(same_as)

    def get_version(self) -> None:
        version = None
        return delete_null_values(version)

    # commented out partial code that was put on hold due to licenses being added to SPASE soon
    def get_is_accessible_for_free(self) -> None:
        free = None
        """schema:description: spase:AccessInformation/AccessRights"""
        is_accessible_for_free = None
        # local vars needed
        #access = ""

        # iterate thru to find AccessInfo
        #for child in self.desiredRoot:
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

    def get_keywords(self) -> Union[List, None]:
        # Mapping: schema:keywords = spase:Keyword
        keywords = []

        # traverse xml to extract needed info
        for child in self.desiredRoot.iter(tag=etree.Element):
            if child.tag.endswith("Keyword"):
                keywords.append(child.text)
        if keywords == []:
            keywords = None
        return delete_null_values(keywords)

    def get_identifier(self) -> Union[Dict, List[Dict], None]:
        # Mapping: schema:identifier = spase:ResourceHeader/spase:DOI (or https://hpde.io landing page, if no DOI)
        # Each item is: {@id: URL, @type: schema:PropertyValue, propertyID: URI for identifier scheme, value: identifier value, url: URL}
        # Uses identifier scheme URI, provided at: https://schema.org/identifier
        #  OR schema:PropertyValue, provided at: https://schema.org/PropertyValue
        url = self.get_url()
        ID = get_ResourceID(self.metadata, self.namespaces)
        hpdeURL = self.get_id()
        # if SPASE record has a DOI
        if "doi" in url:
            temp = url.split("/")
            value = "doi:" + "/".join(temp[3:])
            identifier = [{"@id": url,
                            "@type" : "PropertyValue",
                            "propertyID": "https://registry.identifiers.org/registry/doi",
                            "value": value,
                            "url": url},
                        {"@id": hpdeURL,
                            "@type": "PropertyValue",
                            "propertyID": "SPASE",
                            "value": ID,
                            "url": hpdeURL}
                        ]
        # if SPASE record only has landing page instead
        else:
            identifier = {"@id": url,
                            "@type": "PropertyValue",
                            "propertyID": "SPASE",
                            "url": url,
                            "value": ID}
        return delete_null_values(identifier)

    def get_citation(self) -> Union[List[Dict], None]:
        # Mapping: schema:citation = spase:ResourceHeader/spase:InformationURL
        citation = []
        information_url = get_information_url(self.metadata)
        if information_url:
            for each in information_url:
                # most basic citation item
                entry = {"@id": each["url"],
                        "@type": "CreativeWork",
                        "url": each["url"],
                        "identifier": each["url"]}
                if "name" in each.keys():
                    entry["name"] = each["name"]
                if "description" in each.keys():
                    entry["description"] = each["description"]
                citation.append(entry)
        else:
            citation = None
        return delete_null_values(citation)

    def get_variable_measured(self) -> Union[List[Dict], None]:
        # Mapping: schema:variable_measured = spase:Parameters/spase:Name, Description, Units, ParameterKey
        # Each object is:
        #   {"@type": schema:PropertyValue, "name": Name, "description": Description, "unitText": Units, "alternateName": ParameterKey}
        # Following schema:PropertyValue found at: https://schema.org/PropertyValue
        variable_measured = []
        #minVal = ""
        #maxVal = ""
        paramDesc = ""
        unitsFound = []
        key = ""
        i = 0

        # traverse xml to extract needed info
        for child in self.desiredRoot.iter(tag=etree.Element):
            if child.tag.endswith("Parameter"):
                targetChild = child
                for child in targetChild:
                    unitsFound.append("")
                    try:
                        if child.tag.endswith("Name"):
                            paramName = child.text
                        elif child.tag.endswith("Description"):
                            paramDesc, sep, after = child.text.partition("\n")
                        elif child.tag.endswith("Units"):
                            unit = child.text
                            unitsFound[i] = unit
                        elif child.tag.endswith("ParameterKey"):
                            key = child.text
                        #elif child.tag.endswith("ValidMin"):
                            #minVal = child.text
                        #elif child.tag.endswith("ValidMax"):
                            #maxVal = child.text
                    except AttributeError as err:
                        continue
                # most basic entry for variable measured
                entry = {"@type": "PropertyValue", 
                        "name": paramName}
                        #"minValue": f"{minVal}",
                        #"maxValue": f"{maxVal}"})
                if paramDesc:
                    entry["description"] = paramDesc
                if unitsFound[i]:
                    entry["unitText"] = unitsFound[i]
                if key:
                    entry["alternateName"] = key
                i += 1
                variable_measured.append(entry)
        if len(variable_measured) == 0:
            variable_measured = None
        return delete_null_values(variable_measured)

    def get_included_in_data_catalog(self) -> None:
        included_in_data_catalog = None
        return delete_null_values(included_in_data_catalog)

    def get_subject_of(self) -> Union[Dict, None]:
        # Mapping: schema:subjectOf = {http://www.w3.org/2001/XMLSchema-instance}MetadataRights
        #   AND spase:ResourceHeader/spase:ReleaseDate
        # Following type:DataDownload found at: https://schema.org/DataDownload
        date_modified = self.get_date_modified()
        metadata_license = get_metadata_license(self.metadata)
        contentURL = self.get_id()
        # small lookup table for commonly used licenses in SPASE (CC0 for NASA, CC-BY-NC-3.0 for ESA, etc)
        commonLicenses = [{"fullName":"Creative Commons Zero v1.0 Universal",
                            "identifier": "CC0-1.0",
                            "url": "https://spdx.org/licenses/CC0-1.0.html"},
                            {"fullName": "Creative Commons Attribution Non Commercial 3.0 Unported",
                                "identifier": "CC-BY-NC-3.0",
                                "url": "https://spdx.org/licenses/CC-BY-NC-3.0.html"},
                            {"fullName": "Creative Commons Attribution 1.0 Generic",
                                "identifier": "CC-BY-1.0",
                                "url": "https://spdx.org/licenses/CC-BY-1.0.html"}]
        if metadata_license:
            # find URL associated w license found in top-level SPASE line
            licenseURL = ""
            for entry in commonLicenses:
                if entry["fullName"] == metadata_license:
                    licenseURL = entry["url"]
            # if license is not in lookup table
            if not licenseURL:
                # find licenseURL from SPDX data file at https://github.com/spdx/license-list-data/tree/main
                #   and add to commonLicenses dictionary. Then rerun script for those that failed.
                pass

            # basic format for item
            entry = {"@id": contentURL,
                    "@type": "DataDownload",
                    "name": "SPASE metadata for dataset",
                    "description": "SPASE metadata describing the dataset",
                    "license": licenseURL,
                    "encodingFormat": "application/xml",
                    "contentUrl": contentURL,
                    "identifier": contentURL}
            # if date modified is available, add it
            if date_modified:
                entry["dateModified"] = date_modified
            subject_of = entry
        else:
            subject_of = None
        return delete_null_values(subject_of)

    def get_distribution(self) -> Union[List[Dict], None]:
        # Mapping: schema:distribution = /spase:AccessInformation/spase:AccessURL/spase:URL
        #   (if URL is a direct link to download data)
        # AND /spase:AccessInformation/spase:Format
        # Each object is:
        #   {"@type": schema:DataDownload, "contentURL": URL, "encodingFormat": Format}
        # Following schema:DataDownload found at: https://schema.org/DataDownload
        distribution = []
        dataDownloads, potentialActions = get_accessURLs(self.metadata)
        for k, v in dataDownloads.items():
            entry = ({"@type": "DataDownload",
                        "contentUrl": k,
                        "encodingFormat": v[0]})
            # if AccessURL has a name
            if v[1]:
                entry["name"] = v[1]
            distribution.append(entry)
        if len(distribution) != 0:
            if len(distribution) == 1:
                distribution = distribution[0]
        else:
            distribution = None
        return delete_null_values(distribution)

    def get_potential_action(self) -> Union[List[Dict], None]:
        # Mapping: schema:potentialAction = /spase:AccessInformation/spase:AccessURL/spase:URL
        #   (if URL is not a direct link to download data)
        # AND /spase:AccessInformation/spase:Format
        # Following schema:potentialAction found at: https://schema.org/potentialAction
        potential_actionList = []
        startSent = ""
        endSent = ""
        dataDownloads, potentialActions = get_accessURLs(self.metadata)
        temp_covg = self.get_temporal_coverage()
        if temp_covg is not None:
            if type(temp_covg) == str:
                start, sep, end = temp_covg.partition("/")
            else:
                start, sep, end = temp_covg["temporalCoverage"].partition("/")
            # create test end time
            date, sep, time = start.partition("T")
            time = time.replace("Z", "")
            if "." in time:
                time, sep, ms = time.partition(".")
            dt_string = date + " " + time
            dt_obj = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
            # make test stop time 1 minute after start time
            testEnd = dt_obj + timedelta(minutes=1)
            testEnd = str(testEnd).replace(" ", "T")
            # set testEnd as end time if no end time found in record
            if end == "" or end == "..":
                end = testEnd
            else:
                endSent = f"Data is available up to {end}. "
            endSent += f"Use {testEnd} as a test end value."
            startSent = f"Use {start} as default value."

        # potentialActions[url] = [encoding, {"keys": [], "name": ""}]

        # loop thru all AccessURLs
        for k, v in potentialActions.items():
            prodKeys = v[1]["keys"]
            name = v[1]["name"]
            encoding = v[0]
            # regex pattern for DateTime objects
            pattern = "(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(.[0-9]+)?(Z)?"

            # most basic format for a potentialAction item
            entry = {"@type": "SearchAction",
                            "target": {"@type": "EntryPoint",
                                        "contentType": encoding,
                                        "url": k,
                                        "description": f"Download dataset data as {encoding} file at this URL"}
                            }
            # if link has no prodKey
            if prodKeys == []:
                # if not an ftp link, include url as @id
                if "ftp" not in k: 
                    entry["target"]["@id"] = k
                    entry["target"]["identifier"] = k
                # if name available, add it
                if name:
                    entry["target"]["name"] = name
                potential_actionList.append(entry)
            else:
                # loop thru all product keys if there are multiple
                for prodKey in prodKeys:
                    prodKey = prodKey.replace("\"", "")
                    # if name available, add it
                    if name:
                        entry["target"]["name"] = name
                    # if link is a hapi link, provide the hapi interface web service to download data
                    if "/hapi" in k:
                        # additions needed for each hapi link
                        queryFormat = [{"@type": "PropertyValueSpecification",
                                                    "valueName": "start",
                                                    "description": f"A UTC ISO DateTime. {startSent}",
                                                    "valueRequired": False,
                                                    "valuePattern": f"{pattern}"},
                                                    {"@type": "PropertyValueSpecification",
                                                    "valueName": "end",
                                                    "description": f"A UTC ISO DateTime. {endSent}",
                                                    "valueRequired": False,
                                                    "valuePattern": f"{pattern}"}]
                        entry["target"].pop("url")
                        entry["target"]["urlTemplate"] = f"{k}/data?id={prodKey}&time.min={{start}}&time.max={{end}}"
                        entry["target"]["description"] = "Download dataset labeled by id in CSV format based on the requested start and end dates"
                        entry["target"]["httpMethod"] = "GET"
                        entry["query-input"] = queryFormat
                        # if not ftp link, include url as @id
                        if 'ftp' not in k:
                            entry["target"]["@id"] = k
                            entry["target"]["identifier"] = k
                    # use GSFC CDAWeb portal to download CDF
                    else:
                        entry["description"] = "Download dataset data as CDF or CSV file at this URL"
                        # if not ftp link, include url as @id
                        if 'ftp' not in k:
                            entry["target"]["@id"] = k
                            entry["target"]["identifier"] = k
                    potential_actionList.append(entry)
        if len(potential_actionList) != 0:
            potential_action = potential_actionList
        else:
            potential_action = None
        return delete_null_values(potential_action)

    def get_date_created(self) -> Union[str, None]:
        # Mapping: schema:dateCreated = spase:ResourceHeader/spase:PublicationInfo/spase:PublicationDate
        # OR spase:ResourceHeader/spase:RevisionHistory/spase:ReleaseDate
        # Using schema:DateTime as defined in: https://schema.org/DateTime
        date_created = self.get_date_published()

        #release, revisions = get_dates(self.metadata)
        #if revisions == []:
            #date_created = str(release).replace(" ", "T")
        # find earliest date in revision history
        #else:
            #print("RevisionHistory found!")
            #date_created = str(revisions[0])
            #if len(revisions) > 1:
                #for i in range(1, len(revisions)):
                    #if (revisions[i] < revisions[i-1]):
                        #date_created = str(revisions[i])
            #date_created = date_created.replace(" ", "T")
        return delete_null_values(date_created)

    def get_date_modified(self) -> Union[str, None]:
        # Mapping: schema:dateModified = spase:ResourceHeader/spase:ReleaseDate
        # Using schema:DateTime as defined in: https://schema.org/DateTime
        #trigger = False
        release, revisions = get_dates(self.metadata)
        date_modified = str(release).replace(" ", "T")
        #date_created = date_modified
        # confirm that ReleaseDate is the latest date in the record
        #if revisions != []:
            #print("RevisionHistory found!")
            # find latest date in revision history
            #date_created = str(revisions[0])
            #if len(revisions) > 1:
                #for i in range(1, len(revisions)):
                    #if (revisions[i] > revisions[i-1]):
                        #date_created = str(revisions[i])
            #print(date_created)
            #print(date_modified)
            # raise Error if releaseDate is not the latest in RevisionHistory
            #if datetime.strptime(date_created, "%Y-%m-%d %H:%M:%S") != release:
                #raise ValueError("ReleaseDate is not the latest date in the record!")
                #trigger = True
        return delete_null_values(date_modified)

    def get_date_published(self) -> Union[str, None]:
        # Mapping: schema:datePublished = spase:ResourceHeader/spase:PublicationInfo/spase:PublicationDate
        # OR spase:ResourceHeader/spase:RevisionHistory/spase:ReleaseDate
        # Using schema:DateTime as defined in: https://schema.org/DateTime        
        author, authorRole, pubDate, publisher, contributor, dataset, backups, contactsList = get_authors(self.metadata)
        date_published = None
        release, revisions = get_dates(self.metadata)
        if pubDate == "":
            if revisions:
                # find earliest date in revision history
                date_published = str(revisions[0])
                if len(revisions) > 1:
                    for i in range(1, len(revisions)):
                        if (revisions[i] < revisions[i-1]):
                            date_published = str(revisions[i])
                date_published = date_published.replace(" ", "T")
                date_published = date_published.replace("Z", "")
        else:
            date_published = pubDate.replace(" ", "T")
            date_published = date_published.replace("Z", "")
        return delete_null_values(date_published)

    def get_expires(self) -> None:
        expires = None
        return delete_null_values(expires)

    def get_temporal_coverage(self) -> Union[str, Dict, None]:
        # Mapping: schema:temporal_coverage = spase:TemporalDescription/spase:TimeSpan/*
        # Each object is:
        #   {temporalCoverage: StartDate and StopDate|RelativeStopDate}
        # Result is either schema:Text or schema:DateTime, found at https://schema.org/Text and https://schema.org/DateTime
        # Using format as defined in: https://github.com/ESIPFed/science-on-schema.org/blob/main/guides/Dataset.md#temporal-coverage
        desiredTag = self.desiredRoot.tag.split("}")
        SPASE_Location = ".//spase:" + f"{desiredTag[1]}/spase:TemporalDescription/spase:TimeSpan/spase:StartDate"
        start = self.metadata.findtext(
            SPASE_Location,
            namespaces=self.namespaces,
        )
        SPASE_Location = ".//spase:" + f"{desiredTag[1]}/spase:TemporalDescription/spase:TimeSpan/spase:StopDate"
        stop = self.metadata.findtext(
            SPASE_Location,
            namespaces=self.namespaces,
        )

        if start:
            if stop:
                temporal_coverage = {"@type": "DateTime",
                                    "temporalCoverage": f"{start.strip()}/{stop.strip()}"}
            # in case there is a RelativeStopDate
            else:
                temporal_coverage = f"{start}/.."
        else:
            temporal_coverage = None
        return delete_null_values(temporal_coverage)

    def get_spatial_coverage(self) -> Union[List[Dict], None]:
        # Mapping: schema:spatial_coverage = list of spase:NumericalData/spase:ObservedRegion
        spatial_coverage = []
        desiredTag = self.desiredRoot.tag.split("}")
        SPASE_Location = ".//spase:" + f"{desiredTag[1]}/spase:ObservedRegion"
        for item in self.metadata.findall(
            SPASE_Location,
            namespaces=self.namespaces,
        ):
            # Split string on '.'
            prettyName = item.text.replace(".", " ")

            spatial_coverage.append(
                {
                    "@type": "Place",
                    #"identifier": f"http://www.spase-group.org/data/schema/{item.text.replace('.', '_').upper()}",
                    "additionalProperty": {
                        "@type": "PropertyValue",
                        "valueReference": {
                            "@type": "DefinedTerm",
                            "inDefinedTermSet": {
                                "@type": "DefinedTermSet",
                                "name": "SPASE ObservedRegion"},
                        "termCode": item.text}
                    },
                    "name": prettyName
                }
            )
        if len(spatial_coverage) == 0:
            spatial_coverage = None
        return delete_null_values(spatial_coverage)

    def get_creator(self) -> Union[List[Dict], None]:
        # Mapping: schema:creator = spase:ResourceHeader/spase:PublicationInfo/spase:Authors 
        # OR schema:creator = spase:ResourceHeader/spase:Contact/spase:PersonID
        # Each item is:
        #   {@type: Role, roleName: Contact Role, creator: {@type: Person, name: Author Name, givenName: First Name, familyName: Last Name}}
        #   plus the additional properties if available: affiliation and identifier (ORCiD ID),
        #       which are pulled from SMWG Person SPASE records
        # Using schema:Creator as defined in: https://schema.org/creator
        author, authorRole, pubDate, pub, contributor, dataset, backups, contactsList = get_authors(self.metadata)
        authorStr = str(author).replace("[", "").replace("]","")
        creator = []
        multiple = False
        matchingContact = False
        if author:
            # if creators were found in Contact/PersonID
            if "Person/" in authorStr:
                # if multiple found, split them and iterate thru one by one
                if "'," in authorStr:
                    multiple = True
                for person in author:
                    if multiple:
                        # keep track of position so roles will match
                        index = author.index(person)
                    else:
                        index = 0
                    # split text from Contact into properly formatted name fields
                    authorStr, givenName, familyName = nameSplitter(person)
                    # get additional info if any
                    orcidID, affiliation, ror = get_ORCiD_and_Affiliation(person, self.file)
                    # create the dictionary entry for that person and append to list
                    creatorEntry = personFormat("creator", authorRole[index], authorStr, givenName, familyName, affiliation, orcidID, ror)
                    creator.append(creatorEntry)
            # if all creators were found in PublicationInfo/Authors
            else:
                # if there are multiple authors
                if len(author) > 1:
                    # get rid of extra quotations
                    for num, each in enumerate(author):
                        if "\'" in each:
                            author[num] = each.replace("\'","")
                    # iterate over each person in author string
                    for person in author:
                        index = author.index(person)
                        familyName, sep, givenName = person.partition(", ")
                        # find matching person in contacts, if any, to retrieve affiliation and ORCiD
                        for key, val in contactsList.items():
                            if person == val:
                                matchingContact = True
                                orcidID, affiliation, ror = get_ORCiD_and_Affiliation(key, self.file)
                                creatorEntry = personFormat("creator", authorRole[index], person, givenName, familyName, affiliation, orcidID, ror)
                        if not matchingContact:
                            creatorEntry = personFormat("creator", authorRole[index], person, givenName, familyName)
                        creator.append(creatorEntry)
                # if there is only one author listed
                else:
                    # get rid of extra quotations
                    person = authorStr.replace("\"","")
                    familyName, sep, givenName = person.partition(",")
                    # find matching person in contacts, if any, to retrieve affiliation and ORCiD
                    for key, val in contactsList.items():
                        if person == val:
                            matchingContact = True
                            orcidID, affiliation, ror = get_ORCiD_and_Affiliation(key, self.file)
                            creatorEntry = personFormat("creator", authorRole[0], person, givenName, familyName, affiliation, orcidID, ror)
                    if not matchingContact:
                        creatorEntry = personFormat("creator", authorRole[0], person, givenName, familyName)
                    creator.append(creatorEntry)
        # preserve order of elements
        if len(creator) != 0:
            if len(creator) > 1:
                creator = {"@list": creator}
        else:
            creator = None
        return delete_null_values(creator)

    def get_contributor(self) -> Union[List[Dict], None]:
        # Mapping: schema:contributor = spase:ResourceHeader/spase:Contact/spase:PersonID
        # Each item is:
        #   {@type: Role, roleName: Contributor or curator role, contributor: {@type: Person, name: Author Name, givenName: First Name, familyName: Last Name}}
        #   plus the additional properties if available: affiliation and identifier (ORCiD ID),
        #       which are pulled from SMWG Person SPASE records
        # Using schema:Person as defined in: https://schema.org/Person
        author, authorRole, pubDate, pub, contributors, dataset, backups, contactsList = get_authors(self.metadata)
        contributor = []
        # holds role values that are not initially considered for contributor var
        CuratorRoles = ["HostContact", "GeneralContact", "DataProducer", "MetadataContact", "TechnicalContact"]
        
        # Step 1: check for ppl w author roles that were not found in PubInfo
        for key, val in contactsList.items():
            if "." not in val:
                # split contact into name, first name, and last name
                contributorStr, givenName, familyName = nameSplitter(key)
                # attempt to get ORCiD and affiliation
                orcidID, affiliation, ror = get_ORCiD_and_Affiliation(key, self.file)
                # if contact has more than 1 role
                if len(contactsList[key]) > 1:
                    individual = personFormat("contributor", contactsList[key], contributorStr, givenName, familyName, affiliation, orcidID, ror)
                else:
                    individual = personFormat("contributor", contactsList[key][0], contributorStr, givenName, familyName, affiliation, orcidID, ror)
                contributor.append(individual)

        # Step 2: check for non-author role contributors found in Contacts
        if contributors:
            for person in contributors:
                # split contact into name, first name, and last name
                contributorStr, givenName, familyName = nameSplitter(person)
                # add call to get ORCiD and affiliation
                orcidID, affiliation, ror = get_ORCiD_and_Affiliation(person, self.file)
                individual = personFormat("contributor", contributorStr, givenName, familyName, affiliation, orcidID, ror)
                contributor.append(individual)
        # Step 3: if no non-author role contributor is found, use backups (editors/curators)
        else:
            found = False
            i = 0
            # while a curator is not found
            while not found and i < len(CuratorRoles):
                # search for roles in backups that match CuratorRoles (in order of priority)
                keys = [key for key, val in backups.items() if CuratorRoles[i] in val]
                if keys != []:
                    for key in keys:
                        # split contact into name, first name, and last name
                        editorStr, givenName, familyName = nameSplitter(key)
                        # add call to get ORCiD and affiliation
                        orcidID, affiliation, ror = get_ORCiD_and_Affiliation(key, self.file)
                        individual = personFormat("contributor", CuratorRoles[i], editorStr, givenName, familyName, affiliation, orcidID, ror)
                        contributor.append(individual)
                        found = True
                i += 1
        # preserve order of elements
        if len(contributor) != 0:
            if len(contributor) > 1:
                contributor = {"@list": contributor}
        else:
            contributor = None

        return delete_null_values(contributor)

    def get_provider(self) -> None:
        provider = None
        return delete_null_values(provider)

    def get_publisher(self) -> Union[Dict, None]:
        # Mapping: schema:publisher = spase:ResourceHeader/spase:Contacts
        # OR spase:ResourceHeader/spase:PublicationInfo/spase:PublishedBy
        # Each item is:
        #   {@type: Organization, name: PublishedBy OR Contact (if Role = Publisher)}
        # Using schema:Organization as defined in: https://schema.org/Organization
        
        author, authorRole, pubDate, publisher, contributor, dataset, backups, contactsList = get_authors(self.metadata)
        #ror = None

        # commented out ROR for now until capability added in SPASE
        #ror = get_ROR(publisher)
        """if ror:
            publisher = {"@id": ror,
                        "@type": "Organization",
                        "name": publisher,
                        "identifier": ror}
        else:"""
        if publisher == "":
            publisher = None
        else:
            publisher = {"@type": "Organization",
                        "name": publisher}
        return delete_null_values(publisher)

    def get_funding(self) -> Union[List[Dict], None]:
        # Mapping: schema:funding = spase:ResourceHeader/spase:Funding/spase:Agency 
        # AND spase:ResourceHeader/spase:Funding/spase:Project
        # AND spase:ResourceHeader/spase:Funding/spase:AwardNumber
        # Each item is:
        #   {@type: MonetaryGrant, funder: {@type: Organization, name: Agency}, name: Project}
        # Using schema:MonetaryGrant as defined in: https://schema.org/MonetaryGrant
        funding = []
        agency = []
        project = []
        award = []
        ror = None
        # iterate thru to find all info related to funding
        for child in self.desiredRoot.iter(tag=etree.Element):
            if child.tag.endswith("Funding"):
                targetChild = child
                for child in targetChild:
                    if child.tag.endswith("Agency"):
                        agency.append(child.text)
                    elif child.tag.endswith("Project"):
                        project.append(child.text)
                    elif child.tag.endswith("AwardNumber"):
                        award.append(child.text)
        # if funding info was found
        if agency:
            i = 0
            #ror = get_ROR(agency)
            for funder in agency:
                # basic format for funding item
                entry = {"@type": "MonetaryGrant",
                        "funder": {"@type": "Organization",
                                    "name": funder},
                        "name": project[i]}
                if award:
                    entry["identifier"] = award[i]
                    """if ror:
                    entry["funder"]["@id"] = ror
                    entry["funder"]["identifier"] = ror"""
                funding.append(entry)
                i += 1
        if len(funding) != 0:
            if len(funding) == 1:
                funding = funding[0]
        else:
            funding = None
        return delete_null_values(funding)

    def get_license(self) -> Union[List, None]:
        # Mapping: schema:license = spase:AccessInformation/spase:RightsList/spase:Rights
        # Using schema:license as defined in: https://schema.org/license
        license_url = []

        desiredTag = self.desiredRoot.tag.split("}")
        SPASE_Location = ".//spase:" + f"{desiredTag[1]}/spase:AccessInformation/spase:RightsList/spase:Rights"
        for item in self.metadata.findall(
            SPASE_Location,
            namespaces=self.namespaces,
        ):
            if [item.get("rightsURI")] not in license_url:
                license_url.append(item.get("rightsURI"))
        if license_url == []:
            license_url = None
        elif len(license_url) == 1:
            license_url = license_url[0]
        return delete_null_values(license_url)

    def get_was_revision_of(self) -> Union[List[Dict], Dict, None]:
        # Mapping: prov:wasRevisionOf = spase:Association/spase:AssociationID
        #   (if spase:AssociationType is "RevisionOf")
        # prov:wasRevisionOf found at https://www.w3.org/TR/prov-o/#wasRevisionOf
        was_revision_of = get_relation(self.desiredRoot, ["RevisionOf"], self.file)
        return delete_null_values(was_revision_of)

    def get_was_derived_from(self) -> Union[Dict, None]:
        # Mapping: schema:wasDerivedFrom = spase:Association/spase:AssociationID
        #   (if spase:AssociationType is "DerivedFrom" or "ChildEventOf")
        # schema:wasDerivedFrom found at https://www.w3.org/TR/prov-o/#wasDerivedFrom
        was_derived_from = None
        # same mapping as is_based_on
        was_derived_from = self.get_is_based_on()
        return delete_null_values(was_derived_from)

    def get_is_based_on(self) -> Union[List[Dict], Dict, None]:
        # Mapping: schema:isBasedOn = spase:Association/spase:AssociationID
        #   (if spase:AssociationType is "DerivedFrom" or "ChildEventOf")
        # schema:isBasedOn found at https://schema.org/isBasedOn
        is_based_on = get_relation(self.desiredRoot, ["ChildEventOf", "DerivedFrom"], self.file)
        return delete_null_values(is_based_on)

    def get_was_generated_by(self) -> Union[List[Dict], None]:
        # Mapping: prov:wasGeneratedBy = spase:InstrumentID/spase:ResourceID
        #   and spase:InstrumentID/spase:ResourceHeader/spase:ResourceName
        #   AND spase:InstrumentID/spase:ObservatoryID/spase:ResourceID
        #   and spase:InstrumentID/spase:ObservatoryID/spase:ResourceHeader/spase:ResourceName
        #   AND spase:InstrumentID/spase:ObservatoryID/spase:ObservatoryGroupID/spase:ResourceID
        #   and spase:InstrumentID/spase:ObservatoryID/spase:ObservatoryGroupID/spase:ResourceHeader/spase:ResourceName
        # prov:wasGeneratedBy found at https://www.w3.org/TR/prov-o/#wasGeneratedBy

        instruments = get_instrument(self.metadata, self.file)
        observatories = get_observatory(self.metadata, self.file)
        was_generated_by = []
        
        if observatories:
            for each in observatories:
                was_generated_by.append({"@type": ["ResearchProject", "prov:Activity"],
                                            "prov:used": each})
        if instruments:
            for each in instruments:
                was_generated_by.append({"@type": ["ResearchProject", "prov:Activity"],
                                            "prov:used": each})

        if was_generated_by == []:
            was_generated_by = None
        return delete_null_values(was_generated_by)


# Below are utility functions for the SPASE strategy.


def get_schema_version(metadata: etree.ElementTree) -> str:
    """
    :param metadata: The SPASE metadata object as an XML tree.

    :returns: The version of the SPASE schema used in the metadata record.
    """
    schema_version = metadata.findtext(
        "{http://www.spase-group.org/data/schema}Version"
    )
    return schema_version

def get_authors(metadata: etree.ElementTree) -> tuple[List, List, str, str, List, str, Dict, Dict]:
    """
    Takes an XML tree and scrapes the desired authors (with their roles), publication date,
    publisher, contributors, and publication title. Also scraped are the names and roles of
    the backups, which are any Contacts found that are not considered authors. It then returns 
    these items, with the author, author roles, and contributors as lists and the rest as strings,
    except for the backups which is a dictionary.

    :param metadata: The SPASE metadata object as an XML tree.
    :returns: The highest priority authors found within the SPASE record as a list
                as well as a list of their roles, the publication date, publisher,
                contributors, and the title of the publication. It also returns any contacts found,
                along with their role(s) in two separate dictionaries: ones that are not considered
                for the author role and ones that are.
    """
    # local vars needed
    author = []
    contactsList = {}
    authorRole = []
    pubDate = ""
    pub = ""
    contributor = []
    dataset = ""
    backups = {}
    PI_child = None
    root = metadata.getroot()
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desiredRoot = elt

    # traverse xml to extract needed info
    # iterate thru to find ResourceHeader
    for child in desiredRoot.iter(tag=etree.Element):
        if child.tag.endswith("ResourceHeader"):
            targetChild = child
            # iterate thru to find PublicationInfo
            for child in targetChild:
                try:
                    if child.tag.endswith("PublicationInfo"):
                        PI_child = child
                    elif child.tag.endswith("Contact"):
                        C_Child = child
                        # iterate thru Contact to find PersonID and Role
                        for child in C_Child:
                            try:
                                # find PersonID
                                if child.tag.endswith("PersonID"):
                                    # store PersonID
                                    PersonID = child.text.strip()
                                    backups[PersonID] = []
                                    contactsList[PersonID] = []
                                # find Role
                                elif child.tag.endswith("Role"):
                                    # backup author
                                    if ("PrincipalInvestigator" in child.text) or ("PI" in child.text) or ("CoInvestigator" in child.text):
                                        if PersonID not in author:
                                            author.append(PersonID)
                                            authorRole.append(child.text.strip())
                                        else:
                                            index = author.index(PersonID)
                                            authorRole[index] = [authorRole[index], child.text.strip()]
                                        # store author roles found here in case PubInfo present
                                        contactsList[PersonID] += [child.text.strip()]
                                    # preferred contributor
                                    elif child.text == "Contributor":
                                        contributor.append(PersonID)
                                    # backup publisher (none found in SPASE currently)
                                    elif child.text == "Publisher":
                                        pub = child.text.strip()
                                    else:
                                        # use list for values in case one person has multiple roles
                                        # store contacts w non-author roles for use in contributors
                                        backups[PersonID] += [child.text.strip()]
                            except AttributeError as err:
                                continue
                except AttributeError as err:
                    continue
    if PI_child is not None:
        for child in PI_child.iter(tag=etree.Element):
            # collect preferred author
            if child.tag.endswith("Authors"):
                author = [child.text.strip()]
                authorRole = ["Author"]
            # collect preferred publication date
            elif child.tag.endswith("PublicationDate"):
                pubDate = child.text.strip()
            # collect preferred publisher
            elif child.tag.endswith("PublishedBy"):
                pub = child.text.strip()
            # collect preferred dataset
            elif child.tag.endswith("Title"):
                dataset = child.text.strip()

    # remove contacts w/o role values
    contactsCopy = {}
    for contact, role in contactsList.items():
        if role:
            contactsCopy[contact] = role
    # compare author and contactsList to add author roles from contactsList for matching people found in PubInfo
    # also formats the author list correctly for use in get_creator
    author, authorRole, contactsList = process_authors(author, authorRole, contactsCopy)

    return author, authorRole, pubDate, pub, contributor, dataset, backups, contactsList

def get_accessURLs(metadata: etree.ElementTree) -> tuple[Dict, Dict]:
    """
    Splits the SPASE AccessURLs present in the record into either the distribution
    or potentialAction schema.org properties.

    :param metadata: The SPASE metadata object as an XML tree.
    
    :returns: The AccessURLs found in the SPASE record, separated into two dictionaries,
                dataDownloads and potentialActions, depending on if they are a direct 
                link to data or not. These dictionaries are setup to have the keys as
                the url and the values to be a list containing their data format(s),
                name, and product key (if applicable).
    """
    # needed local vars
    dataDownloads = {}
    potentialActions = {}
    AccessURLs = {}
    encoding = []
    encoder = []
    i = 0
    j = 0
    root = metadata.getroot()
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desiredRoot = elt

    # get Formats before iteration due to order of elements in SPASE record
    desiredTag = desiredRoot.tag.split("}")
    SPASE_Location = ".//spase:" + f"{desiredTag[1]}/spase:AccessInformation/spase:Format"
    for item in metadata.findall(SPASE_Location, namespaces={"spase": "http://www.spase-group.org/data/schema"}):
        encoding.append(item.text)

    # traverse xml to extract needed info
    # iterate thru children to locate Access Information
    for child in desiredRoot.iter(tag=etree.Element):
        if child.tag.endswith("AccessInformation"):
            targetChild = child
            # iterate thru children to locate AccessURL and Format
            for child in targetChild:
                if child.tag.endswith("AccessURL"):
                    targetChild = child
                    name = ""
                    # iterate thru children to locate URL
                    for child in targetChild:
                        if child.tag.endswith("URL"):
                            url = child.text
                            # provide "NULL" value in case no keys are found
                            AccessURLs[url] = {"keys": [], "name": name}
                            # append an encoder for each URL
                            encoder.append(encoding[j])
                        # check if URL has a product key
                        elif child.tag.endswith("ProductKey"):
                            prodKey = child.text
                            # if only one prodKey exists
                            if AccessURLs[url]["keys"] == []:
                                AccessURLs[url]["keys"] = [prodKey]
                            # if multiple prodKeys exist
                            else:
                                AccessURLs[url]["keys"] += [prodKey]
                        elif child.tag.endswith("Name"):
                            name = child.text
            j += 1
    for k, v in AccessURLs.items():
        # if URL has no access key
        if not v["keys"]:
            NonDataFileExt = ['html', 'com', 'gov', 'edu', 'org', 'eu', 'int']
            DataFileExt = ['csv', 'cdf', 'fits', 'txt', 'nc', 'jpeg',
                            'png', 'gif', 'tar', 'netcdf3', 'netcdf4', 'hdf5',
                            'zarr', 'asdf', 'zip']
            protocol, sep, domain = k.partition("://")
            domain, sep, downloadFile = domain.rpartition("/")
            downloadFile, sep, ext = downloadFile.rpartition(".")
            # see if file extension is one associated w data files
            if ext not in DataFileExt:
                downloadable = False
            else:
                downloadable = True
            # if URL is direct link to download data, add to the dataDownloads dictionary
            if downloadable:
                if v["name"]:
                    dataDownloads[k] = [encoder[i], v["name"]]
                else:
                    dataDownloads[k] = [encoder[i]]
            else:
                potentialActions[k] = [encoder[i], v]
        # if URL has access key, add to the potentialActions dictionary
        else:
            potentialActions[k] = [encoder[i], v]
        i += 1
    return dataDownloads, potentialActions

def get_dates(metadata: etree.ElementTree) -> tuple[str, List]:
    """
    Scrapes the ReleaseDate and RevisionHistory:ReleaseDate(s) SPASE properties for use 
    in the dateModified, dateCreated, and datePublished schema.org properties.

    :param metadata: The SPASE metadata object as an XML tree.

    :returns: The ReleaseDate and a list of all the dates found in RevisionHistory
    """
    root = metadata.getroot()
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desiredRoot = elt
    RevisionHistory = []
    ReleaseDate = ""

    # traverse xml to extract needed info
    for child in desiredRoot.iter(tag=etree.Element):
        if child.tag.endswith("ResourceHeader"):
            targetChild = child
            for child in targetChild:
                # find ReleaseDate and construct datetime object from the string
                try:
                    if child.tag.endswith("ReleaseDate"):
                        date, sep, time = child.text.partition("T")
                        if "Z" in child.text:
                            time = time.replace("Z", "")
                        if "." in child.text:
                            time, sep, after = time.partition(".")
                        dt_string = date + " " + time
                        dt_obj = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
                        ReleaseDate = dt_obj
                    elif child.tag.endswith("RevisionHistory"):
                        RHChild = child
                        for child in RHChild:
                            REChild = child
                            for child in REChild:
                                if child.tag.endswith("ReleaseDate"):
                                    date, sep, time = child.text.partition("T")
                                    if "Z" in child.text:
                                        time = time.replace("Z", "")
                                    if "." in child.text:
                                        time, sep, after = time.partition(".")
                                    dt_string = date + " " + time
                                    try:
                                        dt_obj = datetime.strptime(dt_string,
                                                                "%Y-%m-%d %H:%M:%S")
                                    # catch error when RevisionHistory is not formatted w time
                                    except ValueError as err:
                                        dt_obj = datetime.strptime(dt_string.strip(),
                                                                "%Y-%m-%d").date()
                                    finally:
                                        RevisionHistory.append(dt_obj)
                except AttributeError as err:
                    continue
    return ReleaseDate, RevisionHistory

def personFormat(type:str, roleName:str, name:str, givenName:str, familyName:str, affiliation="", orcidID="", ror="") -> Dict:
    """
    Groups up all available metadata associated with a given contact
    into a dictionary following the SOSO guidelines.

    :param type: The type of person being formatted. Values can be either: Contributor or Creator.
    :param roleName: The value found in the Role field associated with this Contact
    :param name: The full name of the Contact, as formatted in the SPASE record
    :param givenName: The first name/initial and middle name/initial of the Contact
    :param familyName: The last name of the Contact
    :param affiliation: The organization this Contact is affiliated with.
    :param orcidID: The ORCiD identifier for this Contact
    :param ror: The ROR ID for the associated affiliation

    :returns: The entry in the correct format to append to the contributor or creator dictionary
    """
    
    domain, sep, orcidVal = orcidID.rpartition("/")
    # most basic format for contributor item
    entry = {"@type": "Role", 
            "roleName": roleName,
            f"{type}": {"@type": "Person",
                            "name": name,
                            "givenName": givenName,
                            "familyName": familyName}
            }
    if orcidID:
        entry[f"{type}"]["identifier"] = {"@id": f"https://orcid.org/{orcidID}",
                                                "@type": "PropertyValue",
                                                "propertyID": "https://registry.identifiers.org/registry/orcid",
                                                "url": f"https://orcid.org/{orcidID}",
                                                "value": f"orcid:{orcidVal}"}
        entry[f"{type}"]["@id"] = f"https://orcid.org/{orcidID}"
    if affiliation:
        if ror:
            entry[f"{type}"]["affiliation"] = {"@id": ror,
                                                "@type": "Organization",
                                                "name": affiliation,
                                                "identifier": ror}
        else:
            entry[f"{type}"]["affiliation"] = {"@type": "Organization",
                                                    "name": affiliation}
    contact = entry       

    return contact

def nameSplitter(person:str) -> tuple[str, str, str]:
    """
    Splits the given PersonID found in the SPASE Contacts container into
    three separate strings holding their full name, first name (and middle initial),
    and last name.

    :param person: The string found in the Contacts field as is formatted in the SPASE record.

    :returns: The string containing the full name of the Contact, the string containing the first name/initial of the Contact,
                and the string containing the last name of the Contact
    """
    if person:
        path, sep, nameStr = person.partition("Person/")
        # get rid of extra quotations
        nameStr = nameStr.replace("'","")
        givenName, sep, familyName = nameStr.partition(".")
        # if name has initial(s)
        if ("." in familyName):
            initial, sep, familyName = familyName.partition(".")
            givenName = givenName + ' ' + initial + '.'
        nameStr = givenName + " " + familyName
        nameStr = nameStr.replace("\"", "")
    else:
        raise ValueError("This function only takes a nonempty string as an argument. Try again.")
    return nameStr, givenName, familyName

def get_information_url(metadata: etree.ElementTree) -> Union[List[Dict], None]:
    """
    Returns all relevant information from the SPASE informationURL(s) property for use
    within the schema.org citation property.

    :param metadata: The SPASE metadata object as an XML tree.

    :returns: The name, description, and url(s) for all InformationURL sections found in the ResourceHeader,
                formatted as a list of dictionaries.
    """
    root = metadata.getroot()
    information_url = []
    name = ""
    description = ""
    for elt in root.iter(tag=etree.Element):
        if (elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData")
            or elt.tag.endswith("Observatory") or elt.tag.endswith("Instrument")):
            desiredRoot = elt
    # traverse xml to extract needed info
    for child in desiredRoot.iter(tag=etree.Element):
        if child.tag.endswith("ResourceHeader"):
            targetChild = child
            # iterate thru children to locate AccessURL and Format
            for child in targetChild:
                try:
                    if child.tag.endswith("InformationURL"):
                        targetChild = child
                        # iterate thru children to locate URL
                        for child in targetChild:
                            if child.tag.endswith("Name"):
                                name = child.text
                            elif child.tag.endswith("URL"):
                                url = child.text
                            elif child.tag.endswith("Description"):
                                description = child.text
                        if name:
                            if description:
                                information_url.append({"name": name,
                                                        "url": url,
                                                        "description": description})
                            else:
                                information_url.append({"name": name,
                                                        "url": url})
                        else:
                            information_url.append({"url": url})
                except AttributeError:
                    continue
    if information_url == []:
        information_url = None
    return information_url

def get_instrument(metadata: etree.ElementTree, path: str) -> Union[List[Dict], None]:
    """
    Attempts to retrieve all relevant information associated with all InstrumentID fields
    found in the SPASE record in order to be used in the prov-o wasGeneratedBy property.

    :param metadata: The SPASE metadata object as an XML tree.
    :param path: The absolute file path of the XML file the user wishes to pull info from.

    :returns: The name, url, and ResourceID for each instrument found in the InstrumentID section,
                formatted as a list of dictionaries.
    """
    # Mapping: schema:IndividualProduct, prov:Entity, and sosa:System = spase:InstrumentID
    # schema:IndividualProduct found at https://schema.org/IndividualProduct
    # prov:Entity found at https://www.w3.org/TR/prov-o/#Entity
    # sosa:System found at https://w3c.github.io/sdw-sosa-ssn/ssn/#SOSASystem

    root = metadata.getroot()
    instrument = []
    instrumentIDs = {}
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desiredRoot = elt
    for child in desiredRoot.iter(tag=etree.Element):
        if child.tag.endswith("InstrumentID"):
            instrumentIDs[child.text] = {}
    if instrumentIDs == {}:
        instrument = None
    else:
        # follow link provided by instrumentID to instrument page
        # from there grab name and url
        for item in instrumentIDs.keys():
            retrying = True
            tries = 1
            instrumentIDs[item]["name"] = ""
            instrumentIDs[item]["URL"] = ""

            # get home directory
            homeDir = str(Path.home())
            homeDir = homeDir.replace("\\","/")
            # get current working directory
            cwd = str(Path.cwd()).replace("\\","/")
            # split path into needed substrings
            before, absPath, after = path.partition(f"{homeDir}/")
            repoName, sep, after = after.partition("/")
            # add original SPASE repo to log file that holds name of repos needed
            updateLog(cwd, repoName)
            # add SPASE repo that contains instruments also
            repoName, sep, after = item.replace("spase://", "").partition("/")
            updateLog(cwd, repoName)
            # format record
            record = absPath + item.replace("spase://","") + ".xml"
            record = record.replace("'","")
            # try to access record at most twice
            while retrying:
                if os.path.isfile(record):
                    retrying = False
                    testSpase = SPASE(record)
                    root = testSpase.metadata.getroot()
                    instrumentIDs[item]["name"] = testSpase.get_name()
                    instrumentIDs[item]["URL"] = testSpase.get_url()
                else:
                    # if retry attempt fails as well, skip the record and let user know
                    if tries == 2:
                        print("Retry attempt failed, skipping this record/link. The metadata quality will be negatively affected.")
                        time.sleep(2)
                        retrying = False
                    else:
                        retrying, tries = retryLinks(item, tries)
        for k in instrumentIDs.keys():
            if instrumentIDs[k]["URL"]:
                instrument.append({"@id": instrumentIDs[k]["URL"],
                                                "@type": ["IndividualProduct", "prov:Entity", "sosa:System"],
                                                "identifier": {"@id": instrumentIDs[k]["URL"],
                                                                "@type": "PropertyValue",
                                                                "propertyID": "SPASE Resource ID",
                                                                "value": k},
                                                "name": instrumentIDs[k]["name"],
                                                "url": instrumentIDs[k]["URL"]})
    return instrument

def get_observatory(metadata: etree.ElementTree, path: str) -> Union[List[Dict], None]:
    """
    Uses the get_instrument function to attempt to retrieve all relevant information 
    associated with any ObservatoryID (and ObservatoryGroupID) fields
    found in their related SPASE records in order to be used in the prov-o
    wasGeneratedBy property.

    :param metadata: The SPASE metadata object as an XML tree.
    :param path: The absolute file path of the XML file the user wishes to pull info from.

    :returns:   The name, url, and ResourceID for each observatory related to this dataset,
                formatted as a list of dictionaries.
    """
    # Mapping: schema:ResearchProject, prov:Entity, and sosa:Platform = spase:InstrumentID/spase:ObservatoryID
    #   AND spase:InstrumentID/spase:ObservatoryID/spase:ObservatoryGroupID if available
    # schema:ResearchProject found at https://schema.org/ResearchProject
    # prov:Entity found at https://www.w3.org/TR/prov-o/#Entity
    # sosa:Platform found at https://w3c.github.io/sdw-sosa-ssn/ssn/#SOSAPlatform

    instrument = get_instrument(metadata, path)
    if instrument is not None:
        observatory = []
        observatoryGroupID = ""
        observatoryID = ""
        recordedIDs = []
        instrumentIDs = []

        for each in instrument:
            instrumentIDs.append(each["identifier"]["value"])
        for item in instrumentIDs:
            # get home directory
            homeDir = str(Path.home())
            homeDir = homeDir.replace("\\","/")
            # get current working directory
            cwd = str(Path.cwd()).replace("\\","/")
            # split path into needed substrings
            before, absPath, after = path.partition(f"{homeDir}/")
            repoName, sep, after = after.partition("/")
            # add original SPASE repo to log file that holds name of repos needed
            updateLog(cwd, repoName)
            record = absPath + item.replace("spase://","") + ".xml"
            record = record.replace("'","")
            # follow link provided by instrument to instrument page, from there grab ObservatoryID
            if os.path.isfile(record):
                testSpase = SPASE(record)
                root = testSpase.metadata.getroot()
                for elt in root.iter(tag=etree.Element):
                    if elt.tag.endswith("Instrument"):
                        desiredRoot = elt
                for child in desiredRoot.iter(tag=etree.Element):
                    if child.tag.endswith("ObservatoryID"):
                        observatoryID = child.text
                # add SPASE repo that contains observatories to log file also
                repoName, sep, after = observatoryID.replace("spase://", "").partition("/")
                updateLog(cwd, repoName)
                # use observatoryID as record to get observatoryGroupID and other info              
                record = absPath + observatoryID.replace("spase://","") + ".xml"
                record = record.replace("'","")
                # try to access record at most twice
                retryingObs = True
                triesObs = 1
                while retryingObs:               
                    if os.path.isfile(record):
                        retryingObs = False
                        url = ""
                        testSpase = SPASE(record)
                        root = testSpase.metadata.getroot()
                        for elt in root.iter(tag=etree.Element):
                            if elt.tag.endswith("Observatory"):
                                desiredRoot = elt
                        for child in desiredRoot.iter(tag=etree.Element):
                            if child.tag.endswith("ObservatoryGroupID"):
                                observatoryGroupID = child.text
                        name = testSpase.get_name()
                        url = testSpase.get_url()
                        # finally, follow that link to grab name and url from there
                        if observatoryGroupID:
                            retryingObsGrp = True
                            triesObsGrp = 1
                            # add SPASE repo that contains observatory group to log file also
                            repoName, sep, after = observatoryGroupID.replace("spase://", "").partition("/")
                            updateLog(cwd, repoName)
                            # format record
                            record = absPath + observatoryGroupID.replace("spase://","") + ".xml"
                            record = record.replace("'","")
                            # try to access record at most twice
                            while retryingObsGrp:
                                if os.path.isfile(record):
                                    retryingObsGrp = False
                                    groupURL = ""
                                    testSpase = SPASE(record)
                                    groupName = testSpase.get_name()
                                    groupURL = testSpase.get_url()
                                    if groupURL:
                                        if observatoryGroupID not in recordedIDs:
                                            observatory.append({"@type": ["ResearchProject", "prov:Entity", "sosa:Platform"],
                                                                "@id": groupURL,
                                                                "name": groupName,
                                                                "identifier": {"@id": groupURL,
                                                                                "@type": "PropertyValue",
                                                                                "propertyID": "SPASE Resource ID",
                                                                                "value": observatoryGroupID},
                                                                "url": groupURL})
                                            recordedIDs.append(observatoryGroupID)
                                else:
                                    # if retry attempt fails as well, skip the record and let user know
                                    if triesObsGrp == 2:
                                        print("Retry attempt failed, skipping this record/link. The metadata quality will be negatively affected.")
                                        time.sleep(2)
                                        retryingObsGrp = False
                                    else:
                                        retryingObsGrp, triesObsGrp = retryLinks(observatoryGroupID, triesObsGrp)
                        if url and (observatoryID not in recordedIDs):
                            observatory.append({"@type": ["ResearchProject", "prov:Entity", "sosa:Platform"],
                                                "@id": url,
                                                "name": name,
                                                "identifier": {"@id": url,
                                                                "@type": "PropertyValue",
                                                                "propertyID": "SPASE Resource ID",
                                                                "value": observatoryID},
                                                "url": url})
                            recordedIDs.append(observatoryID)
                    else:
                        # if retry attempt fails as well, skip the record and let user know
                        if triesObs == 2:
                            print("Retry attempt failed, skipping this record/link. The metadata quality will be negatively affected.")
                            time.sleep(2)
                            retryingObs = False
                        else:
                            retryingObs, triesObs = retryLinks(observatoryID, triesObs)
    else:
        observatory = None
    return observatory

def get_alternate_name(metadata: etree.ElementTree) -> Union[str, None]:
    """
    :param metadata: The SPASE metadata object as an XML tree.

    :returns: The alternate name of the dataset as a string.
    """
    root = metadata.getroot()
    alternate_name = None
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desiredRoot = elt
    for child in desiredRoot.iter(tag=etree.Element):
        if child.tag.endswith("ResourceHeader"):
            targetChild = child
            # iterate thru children to locate AlternateName for dataset
            for child in targetChild:
                try:
                    if child.tag.endswith("AlternateName"):
                        alternate_name = child.text
                except AttributeError:
                    continue
    return alternate_name

def get_cadenceContext(cadence:str) -> str:
    """
    Returns a more human friendly explanation of the ISO 8601 formatted value
    found in the TemporalDescription:Cadence field in SPASE.

    :param cadence: The value found in the Cadence field of the TemporalDescription section

    :returns: A string description of what this value represents/means.
    """
    # takes cadence/repeatFreq and returns an explanation for what it means
    # ISO 8601 Format = PTHH:MM:SS.sss
    # P1D, P1M, and P1Y represent time cadences of one day, one month, and one year, respectively
    context = "The time series is periodic with a "
    start, sep, end = cadence.partition("P")
    # cadence is in hrs, min, or sec
    if "T" in end:
        start, sep, time = end.partition("T")
        if "H" in time:
            # hrs
            start, sep, end = time.partition("H")
            context += start + " hour cadence"
        elif "M" in time:
            # min
            start, sep, end = time.partition("M")
            context += start + " minute cadence"
        elif "S" in time:
            # sec
            start, sep, end = time.partition("S")
            context += start + " second cadence"
    # one of the 3 base cadences
    else:
        if "D" in end:
            # days
            start, sep, end = end.partition("D")
            context += start + " day cadence"
        elif "M" in end:
            # months
            start, sep, end = end.partition("M")
            context += start + " month cadence"
        elif "Y" in end:
            # yrs
            start, sep, end = end.partition("Y")
            context += start + " year cadence"
    if context == "This means that the time series is periodic with a ":
        context = None
    return context

def get_mentions(metadata: etree.ElementTree, path:str) -> Union[List[Dict], Dict, None]:
    """
    Scrapes any AssociationIDs with the AssociationType "Other" and formats them
    as dictionaries using the get_relation function.

    :param metadata: The SPASE metadata object as an XML tree.
    :param path: The absolute path of the xml file being scraped.

    :returns: The ID's of other SPASE records related to this one in some way.
    """
    # Mapping: schema:mentions = spase:Association/spase:AssociationID
    #   (if spase:AssociationType is "Other")
    # schema:mentions found at https://schema.org/mentions
    root = metadata.getroot()
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desiredRoot = elt
    mentions = get_relation(desiredRoot, ["Other"], path)
    return mentions

def get_is_part_of(metadata: etree.ElementTree, path:str) -> Union[List[Dict], Dict, None]:
    """
    Scrapes any AssociationIDs with the AssociationType "PartOf" and formats them
    as dictionaries using the get_relation function.

    :param metadata: The SPASE metadata object as an XML tree.
    :param path: The absolute path of the xml file being scraped.

    :returns: The ID(s) of the larger resource this SPASE record is a portion of, as a dictionary.
    """
    # Mapping: schema:isBasedOn = spase:Association/spase:AssociationID
    #   (if spase:AssociationType is "PartOf")
    # schema:isPartOf found at https://schema.org/isPartOf
    root = metadata.getroot()
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desiredRoot = elt
    is_part_of = get_relation(desiredRoot, ["PartOf"], path)
    return is_part_of

def get_ORCiD_and_Affiliation(PersonID: str, file: str) -> tuple[str, str, str]:
    """
    Uses the given PersonID to scrape the ORCiD and affiliation (and its ROR ID if provided)
    associated with this contact.

    :param PersonID: The SPASE ID linking the page with the Person's info.
    :param file: The absolute path of the original xml file scraped.

    :returns: The ORCiD ID and organization name (with its ROR ID, if found) this Contact is affiliated with, as strings.
    """
    # takes PersonID and follows its link to get ORCIdentifier and OrganizationName
    orcidID = ""
    affiliation = ""
    ror = ""
    # get home directory
    homeDir = str(Path.home())
    homeDir = homeDir.replace("\\","/")
    # get current working directory
    cwd = str(Path.cwd()).replace("\\","/")
    # split record into needed substrings
    before, absPath, after = file.partition(f"{homeDir}/")
    repoName, sep, after = after.partition("/")
    # add original SPASE repo to log file that holds name of repos needed
    updateLog(cwd, repoName)
    # add SPASE repo that contains Person descriptions to log file also
    repoName, sep, after = PersonID.replace("spase://", "").partition("/")
    updateLog(cwd, repoName)
    # format record name
    record = absPath + PersonID.replace("spase://", "") + ".xml"
    record = record.replace("'","")
    # try to access record at most twice
    retrying = True
    tries = 1
    while retrying:
        if os.path.isfile(record):
            retrying = False
            testSpase = SPASE(record)
            root = testSpase.metadata.getroot()
            # iterate thru xml to get desired info
            for elt in root.iter(tag=etree.Element):
                if elt.tag.endswith("Person"):
                    desiredRoot = elt
            for child in desiredRoot.iter(tag=etree.Element):
                if child.tag.endswith("ORCIdentifier"):
                    orcidID = child.text
                elif child.tag.endswith("OrganizationName"):
                    affiliation = child.text
                elif child.tag.endswith("RORIdentifier"):
                    ror = child.text
        else:
            # if retry attempt fails as well, skip the record and let user know
            if tries == 2:
                print("Retry attempt failed, skipping this record/link. The metadata quality will be negatively affected.")
                time.sleep(2)
                retrying = False
            else:
                retrying, tries = retryLinks(PersonID, tries)
    return orcidID, affiliation, ror

def get_temporal(metadata: etree.ElementTree, namespaces: Dict) -> Union[List, None]:
    """
    Scrapes the TemporalDescription:Cadence field in SPASE for use in the
    schema.org temporal property.

    :param metadata: The SPASE metadata object as an XML tree.
    :param namespaces: The SPASE namespaces used in the form of a dictionary.

    :returns: The cadence or common time interval between the start of successive measurements,
                given in its ISO 8601 formatting as well as a explanation sentence.
    """
    # Mapping: schema:temporal = spase:TemporalDescription/spase:Cadence
    # Each object is:
    #   [ explanation (string explaining meaning of cadence), Cadence]
    # Schema found at https://schema.org/temporal
    root = metadata.getroot()
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desiredRoot = elt
    
    desiredTag = desiredRoot.tag.split("}")
    SPASE_Location = ".//spase:" + f"{desiredTag[1]}/spase:TemporalDescription/spase:Cadence"
    repeat_frequency =  metadata.findtext(
        SPASE_Location,
        namespaces= namespaces,
    )

    explanation = ""

    if repeat_frequency:
        explanation = get_cadenceContext(repeat_frequency)
        temporal = [explanation, repeat_frequency]
    else:
        temporal = None
    return delete_null_values(temporal)

def get_metadata_license(metadata: etree.ElementTree) -> str:
    """
    :param metadata: The metadata object as an XML tree.

    :returns: The metadata license of the SPASE record.
    """
    metadata_license = None
    root = metadata.getroot()
    attributes = root.attrib
    # key looks like this: {http://www.w3.org/2001/XMLSchema-instance}rights
    for key, val in attributes.items():
        if "rights" in key:
            metadata_license = val
    return metadata_license

def process_authors(author:List, authorRole:List, contactsList:Dict) -> tuple[List, List, Dict]:
    """
    Groups any contact names from the SPASE Contacts container with their matching names, if
    found, in PubInfo:Authors, and adds any additional author roles (such as PI) to their
    corresponding entry in the authorRoles list. Any contact with an author role not
    listed in PubInfo:Authors is added to the contactsList with the rest of the
    non-matching contacts for use in get_contributors.

    :param author: The list of names found in SPASE record to be used in get_creator
    :param authorRole: The list of roles associated with each person found in author list
    :param contactsList: The dictionary containing the names of people considered to 
                            be authors as formatted in the Contacts container in the 
                            SPASE record, as well as their roles

    :returns: The updated author, authorRoles, and contactsList items after merging any author
                roles from Contacts with the roles associated with them if found in PubInfo.  
    """
    # loop thru all contacts to find any that match authors, unless no PubInfo was found
    # if matches found, add roles to authorRoles and remove them from contactsList
    # if no match found for person(s), leave in contactsList for use in get_contributors

    authorStr = str(author).replace("[", "").replace("]","")
    # if creators were found in Contact/PersonID (no PubInfo)
    # remove author roles from contactsList so not duplicated in contributors (since already in author list)
    if "Person/" in authorStr:
        contactsCopy = {}
        for person, val in contactsList.items():
            contactsCopy[person] = []
            for role in val:
                # if role is not considered for author, add to acceptable roles list for use in contributors
                if ("PrincipalInvestigator" not in role) and ("PI" not in role) and ("CoInvestigator" not in role):
                    contactsCopy[person].append(role)
            # if no acceptable roles were found, remove that author from contributor consideration
            if contactsCopy[person] == []:
                contactsCopy.pop(person)
        return author, authorRole, contactsCopy
    # if all creators were found in PublicationInfo/Authors
    else:
        # if there are multiple authors
        if (";" in authorStr) or (".," in authorStr):
            if (";" in authorStr):
                author = authorStr.split("; ")
            else:
                author = authorStr.split("., ")
            # fix num of roles
            while (len(authorRole) < len(author)):
                authorRole += ["Author"]
            # get rid of extra quotations
            for num, each in enumerate(author):
                if "\'" in each:
                    author[num] = each.replace("\'","")
            # iterate over each person in author string
            for person in author:
                matchingContact = None
                index = author.index(person)
                # if first name doesnt have a period, check if it is an initial
                if (not person.endswith(".")):
                    # if first name is an initial w/o a period, add one
                    grp = re.search(r'[\.\s]{1}[\w]{1}$', person)
                    if grp is not None:
                        person += "."
                # remove 'and' from name
                if "and " in person:
                    person = person.replace("and ", "")
                # continued formatting fixes
                if ", " in person:
                    familyName, sep, givenName = person.partition(", ")
                else:
                    givenName, sep, familyName = person.partition(". ")
                    givenName += "."
                if "," in givenName:
                    givenName = givenName.replace(",","")
                # iterate thru contacts to find one that matches the current person
                for contact in contactsList.keys():
                    if matchingContact is None:
                        firstName, sep, lastName = contact.rpartition(".")
                        firstName, sep, initial = firstName.partition(".")
                        path, sep, firstName = firstName.rpartition("/")
                        # Assumption: if first name initial, middle initial, and last name match = same person
                        # remove <f"{firstName[0]}."> in the line below if this assumption is no longer accurate
                        if ((f"{firstName[0]}." in person) or (firstName in person)) and (f"{initial}." in person) and (lastName in person):
                            matchingContact = contact
                # if match is found, add role to authorRole and replace role with formatted person name in contactsList
                if matchingContact is not None:
                    authorRole[index] = [authorRole[index]] + contactsList[matchingContact]
                    contactsList[matchingContact] = f"{lastName}, {firstName} {initial}."
                author[index] = (f'{familyName}, {givenName}').strip()
        # if there is only one author listed
        else:
            matchingContact = None
            # get rid of extra quotations
            person = authorStr.replace("\"","")
            if authorRole == ["Author"]:
                familyName, sep, givenName = person.partition(",")
                # handle case when name is not formatted correctly
                if givenName == "":
                    givenName, sep, familyName = familyName.partition(". ")
                    initial, sep, familyName = familyName.partition(" ")
                    givenName = givenName + ". " + initial[0] + "."
                if "," in givenName:
                    givenName = givenName.replace(",","")
                # iterate thru contacts to find one that matches the current person
                for contact in contactsList.keys():
                    if matchingContact is None:
                        firstName, sep, lastName = contact.rpartition(".")
                        firstName, sep, initial = firstName.partition(".")
                        path, sep, firstName = firstName.rpartition("/")
                        # Assumption: if first name initial, middle initial, and last name match = same person
                        # remove <f"{firstName[0]}."> in the line below if this assumption is no longer accurate
                        if ((f"{firstName[0]}." in person) or (firstName in person)) and (f"{initial}." in person) and (lastName in person):
                            matchingContact = contact
                # if match is found, add role to authorRole and replace role with formatted person name in contactsList
                if matchingContact is not None:
                    authorRole[0] = [authorRole[0]] + contactsList[matchingContact]
                    contactsList[matchingContact] = f"{lastName}, {firstName} {initial}."
                author[0] = (f'{familyName}, {givenName}').strip()
    return author, authorRole, contactsList

def verifyType(url:str) -> tuple[bool, bool]:
    """
    Verifies that the link found in AssociationID is to a dataset or journal article.

    :param url: The link provided as an Associated work/reference for the SPASE record

    :returns: Boolean values signifying if the link is a Dataset or a ScholarlyArticle
    """
    # tests SPASE records to make sure they are datasets or a journal article
    isDataset = False
    isArticle = False

    if "hpde.io" in url:
        if "Data" in url:
            isDataset = True
    # case where url provided is a DOI
    else:
        link = requests.head(url)
        # check to make sure doi resolved to an hpde.io page
        if "hpde.io" in link.headers['location']:
            if "Data" in link.headers['location']:
                isDataset = True
        # if not, call DataCite API to check resourceTypeGeneral property associated w the record
        else:
            protocol, sep, doi = link.partition("doi.org/")
            dataciteLink = f"https://api.datacite.org/dois/{doi}"
            headers = {"accept": "application/vnd.api+json"}
            response = requests.get(dataciteLink, headers=headers)
            dict = json.loads(response.text)
            for item in dict["data"]["types"]:
                if (item["resourceTypeGeneral"] == "Dataset"):
                    isDataset = True
                elif (item["resourceTypeGeneral"] == "JournalArticle"):
                    isArticle = True
                # if wish to add more checks, simply add more "elif" stmts like above
                # and adjust provenance/relationship functions to include new type check

    return isDataset, isArticle

def get_ResourceID(metadata: etree.ElementTree, namespaces: Dict):
    """
    :param metadata: The SPASE metadata object as an XML tree.
    :param namespaces: The SPASE namespaces used in the form of a dictionary.

    :returns: The ResourceID for the SPASE record.
    """
    root = metadata.getroot()
    for elt in root.iter(tag=etree.Element):
        if (elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData")
                or elt.tag.endswith("Observatory") or elt.tag.endswith("Instrument")
                or elt.tag.endswith("Person")):
            desiredRoot = elt

    desiredTag = desiredRoot.tag.split("}")
    SPASE_Location = ".//spase:" + f"{desiredTag[1]}/spase:ResourceID"
    dataset_id = metadata.findtext(
        SPASE_Location, namespaces=namespaces
    )
    return dataset_id

def get_measurementMethod(metadata: etree.ElementTree, namespaces: Dict) -> Union[List, None]:
    """
    Scrapes all measurementType fields found in the SPASE record and maps them to
    the schema.org property measurementMethod.

    :param metadata: The SPASE metadata object as an XML tree.
    :param namespaces: The SPASE namespaces used in the form of a dictionary.

    :returns: The MeasurementType(s) for the SPASE record.
    """
    # Mapping: schema:measurementMethod = spase:MeasurementType
    # schema:measurementMethod found at https://schema.org/measurementMethod
    measurementMethod = []
    root = metadata.getroot()
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desiredRoot = elt
    desiredTag = desiredRoot.tag.split("}")
    SPASE_Location = ".//spase:" + f"{desiredTag[1]}/spase:MeasurementType"
    for item in metadata.findall(
        SPASE_Location,
        namespaces=namespaces,
    ):
        # Split string on uppercase characters
        res = re.split(r'(?=[A-Z])', item.text)
        # Remove empty strings and join with space
        prettyName = ' '.join(filter(None, res))

        measurementMethod.append(
            {"@type": "DefinedTerm",
            "inDefinedTermSet": {
                "@type": "DefinedTermSet",
                "name": "SPASE MeasurementType"},
            "name": prettyName,
            "termCode": item.text
            }
        )
    if len(measurementMethod) == 0:
        measurementMethod = None
    elif len(measurementMethod) == 1:
        measurementMethod = measurementMethod[0]
    return measurementMethod

def get_relation(desiredRoot: etree.Element, association: list[str], path: str) -> Union[List[Dict], Dict, None]:
    """
    Scrapes through the SPASE record and returns the AssociationIDs which have the
    given AssociationType. These are formatted as dictionaries and use the verifyType
    function to add the correct type to each entry.

    :param desiredRoot: The element in the SPASE metadata tree object we are searching from.
    :param association: The AssociationType(s) we are searching for in the SPASE record.
    :param path: The absolute path of the xml file being scraped.

    :returns: The ID's of other SPASE records related to this one in some way.
    """
    relations = []
    # iterate thru xml to find desired info
    for child in desiredRoot.iter(tag=etree.Element):
        if child.tag.endswith("Association"):
            targetChild = child
            for child in targetChild:
                if child.tag.endswith("AssociationID"):
                    A_ID = child.text
                elif child.tag.endswith("AssociationType"):
                    type = child.text
            for each in association:
                if type == each:
                    relations.append(A_ID)
    if relations == []:
        relation = None
    else:
        i = 0
        # try and get DOI instead of SPASE ID
        for record in relations:
            # try to access record at most twice
            retrying = True
            tries = 1
            # get home directory
            homeDir = str(Path.home())
            homeDir = homeDir.replace("\\","/")
            # get current working directory
            cwd = str(Path.cwd()).replace("\\","/")
            # add SPASE repo that contains related SPASE record to log file
            repoName, sep, after = record.replace("spase://", "").partition("/")
            updateLog(cwd, repoName)
            record = homeDir + '/' + record.replace("spase://", "") + ".xml"
            record = record.replace("'","")
            while retrying:
                if os.path.isfile(record):
                    retrying = False
                    testSpase = SPASE(record)
                    relations[i] = testSpase.get_url()
                else:
                    # if retry attempt fails as well, skip the record and let user know
                    if tries == 2:
                        print("Retry attempt failed, skipping this record/link. The metadata quality will be negatively affected.")
                        time.sleep(2)
                        retrying = False
                    else:
                        retrying, tries = retryLinks(record, tries)
                i += 1
        # add correct type
        if len(relations) > 1:
            relation = []
            for each in relations:
                # most basic entry into relation
                entry = {"@id": each,
                            "identifier": each}
                isDataset, isArticle = verifyType(each)
                if isDataset:
                    entry["@type"] = "Dataset"
                elif isArticle:
                    entry["@type"] = "ScholarlyArticle"
                relation.append(entry)
        else:
            # most basic entry into relation
            entry = {"@id": relations[0],
                        "identifier": relations[0]}
            isDataset, isArticle = verifyType(relations[0])
            if isDataset:
                entry["@type"] = "Dataset"
            elif isArticle:
                entry["@type"] = "ScholarlyArticle"
            relation = entry
    return relation

def updateLog(cwd:str, repoName:str) -> None:
    """
    Creates a log file containing the SPASE repositories needed for the
    metadata conversion to work as intended.

    :param cwd: The current working directory of your workstation.
    :param repoName: The name of the repository needed to access the SPASE record.
    """

    with open(f"{cwd}/requiredRepos.txt", "r") as f:
        text = f.read()
    if repoName not in text:
        with open(f"{cwd}/requiredRepos.txt", "a") as f:
            f.write(f"\n{repoName}")

def retryLinks(item:str, tries:int) -> tuple[bool, int]:
    """
    Attempts to access the given file. The user
    may answer 'skip' if a known broken link/record appears or
    answer 'done' to retry accessing the file after confirming all necessary
    SPASE repositories are cloned in their local home directory.

    :param item: The SPASE record you are trying to access.
    :param tries: The number of times the script has tried to access the file.
    """
    
    incorrectInput = True
    while incorrectInput:
        answer = input(f"'{item}' not found, likely because the SPASE repository " \
        "was not downloaded. If this error repeats, please run findRequirements to " \
        "determine what SPASE repositories need to be downloaded, download those " \
        "repositories to the same home directory, and continue this script by " \
        "responding 'done' or respond 'skip' to skip to the next. ")
        if (answer.lower() == 'done'):
            incorrectInput = False
            tries += 1
            retrying = True
        elif (answer.lower() == 'skip'):
            incorrectInput = False
            retrying = False
            print("Skipping this record/link. The metadata quality will be negatively affected.")
            time.sleep(2)
        else:
            print("Please enter 'done' or 'skip'.")
    return retrying, tries