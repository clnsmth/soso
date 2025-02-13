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
            - subject_of
            - expires
            - provider
            - was_generated_by
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
        # Mapping: schema:identifier = spase:ResourceID
        desiredTag = self.desiredRoot.tag.split("}")
        SPASE_Location = ".//spase:" + f"{desiredTag[1]}/spase:ResourceID"
        dataset_id = self.metadata.findtext(
            SPASE_Location, namespaces=self.namespaces
        )
        return delete_null_values(dataset_id)

    def get_name(self) -> str:
        # Mapping: schema:description = spase:ResourceHeader/spase:ResourceName
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
            desiredTag = self.desiredRoot.tag.split("}")
            SPASE_Location = ".//spase:" + f"{desiredTag[1]}/spase:ResourceID"
            url = self.metadata.findtext(
                SPASE_Location, namespaces=self.namespaces
            ).replace("spase://", "https://hpde.io/")
        return delete_null_values(url)

    def get_same_as(self) -> Union[List, None]:
        same_as = []
        for child in self.desiredRoot.iter(tag=etree.Element):
            if child.tag.endswith("PriorID"):
                same_as.append(child.text)
        if same_as == []:
            same_as = None
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

    def get_keywords(self) -> Union[str, None]:
        # Mapping: schema:keywords = spase:ResourceHeader/spase:Keyword
        keywords = []
        for child in self.desiredRoot.iter(tag=etree.Element):
            if child.tag.endswith("Keyword"):
                keywords.append(child.text)
        if keywords == []:
            keywords = None
        return delete_null_values(keywords)

    def get_identifier(self) -> Union[str, Dict, None]:
        # Mapping: schema:identifier = spase:ResourceHeader/spase:DOI (or https://hpde.io landing page, if no DOI)
        # Each item is: {@id: URL, @type: schema:PropertyValue, propertyID: URI for identifier scheme, value: identifier value, url: URL}
        # Uses identifier scheme URI, provided at: https://schema.org/identifier
        #  OR schema:PropertyValue, provided at: https://schema.org/PropertyValue
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

    def get_citation(self) -> Union[str, Dict, None]:
        # Mapping: schema:citation = spase:ResourceHeader/spase:PublicationInfo/spase:Authors
        # AND spase:ResourceHeader/spase:PublicationInfo/spase:PublicationDate
        # AND spase:ResourceHeader/spase:PublicationInfo/spase:PublishedBy
        # AND spase:ResourceHeader/spase:PublicationInfo/spase:Title
        # AND spase:ResourceHeader/spase:DOI
        # AND spase:ResourceHeader/spase:InformationURL

        # local vars needed
        authorTemp = ""
        author = []
        pubDate = ""
        pub = ""
        contributor = []
        dataset = ""
        i = 0

        authorTemp, authorRole, pubDate, pub, contributor, dataset, backups, contactsList = get_authors(self.metadata)
        pubDate = pubDate[:4]
        authorStr = str(authorTemp)
        authorStr = authorStr.replace("[", "").replace("]","")
        authorStr = authorStr.replace("'","")
        authorStr = authorStr.replace(" and ", " ")
        # if author is not empty
        if authorTemp:
            # if author was pulled from ContactID
            if "Person/" in authorStr:
                # if multiple found, split them and iterate thru one by one
                if len(authorTemp) > 1:
                    for person in authorTemp:
                        path, sep, authorStr = person.partition("Person/")
                        givenName, sep, familyName = authorStr.partition(".")
                        #print(givenName)
                        #print(familyName)
                        #print(authorStr)
                        # if name has initial(s) already
                        if ("." in familyName):
                            initial, sep, familyName = familyName.partition(".")
                            givenName = givenName[0] + "." + initial + "."
                            givenName = givenName[0] + "." + initial + "."
                        else:
                            givenName = givenName[0] + "."
                        # add commas to separate each name until last name in list
                        if (i < (len(authorTemp) - 1)):
                            author += [familyName + ", " + givenName]
                        else:
                            author += ["& " + familyName + ", " + givenName]
                        i += 1
                    # reformat author string
                    # if only 2 authors, eliminate extra comma in bw them
                    if len(authorTemp) == 2:
                        authorStr = ""
                        for each in author:
                            authorStr += str(each).replace("'", "") + " "
                        author = authorStr[:-1]
                    # else convert the list into a string with proper format
                    else:
                        author = str(author).replace("[", "").replace("]","")
                        author = author.replace("'","")
                    # if only 2 authors, eliminate extra comma in bw them
                    if len(authorTemp) == 2:
                        authorStr = ""
                        for each in author:
                            authorStr += str(each).replace("'", "") + " "
                        author = authorStr[:-1]
                    # else convert the list into a string with proper format
                    else:
                        author = str(author).replace("[", "").replace("]","")
                        author = author.replace("'","")
                # if only one Contact found
                else:
                    path, sep, authorTemp = authorStr.partition("Person/")
                    #print(authorTemp)
                    givenName, sep, familyName = authorTemp.partition(".")
                    # if name has initial(s) already
                    if ("." in familyName):
                        initial, sep, familyName = familyName.partition(".")
                        givenName = givenName[0] + "." + initial + "."
                        givenName = givenName[0] + "." + initial + "."
                    else:
                        givenName = givenName[0] + "."
                    author = familyName + ", " + givenName
            # case when in PubInfo but only one author
            elif ";" not in authorStr:
                # if formatted for citation already
                if "et al" in authorStr:
                    author = authorStr
                # in case there are multiple w/o ;
                elif "., " in authorStr:
                    authorStr = authorStr.replace(".,", "..,")
                    authorTemp = authorStr.split("., ")
                    if ", " not in authorTemp[-1]:
                        givenName, sep, familyName = authorTemp[-1].partition(". ")
                        givenName = givenName.replace("and ", "") + "."
                        authorTemp[-1] = familyName + ", " + givenName
                    if ", " not in authorTemp[-1]:
                        givenName, sep, familyName = authorTemp[-1].partition(". ")
                        givenName = givenName.replace("and ", "") + "."
                        authorTemp[-1] = familyName + ", " + givenName
                    if "and " in authorTemp[-1]:
                        authorTemp[-1].replace("and ", "& ")
                    else:
                        authorTemp[-1] = "& " + authorTemp[-1]
                    # if only 2 authors, eliminate extra comma in bw them
                    if len(authorTemp) == 2:
                        authorStr = ""
                        for each in authorTemp:
                            authorStr += str(each).replace("'", "") + " "
                        author = authorStr[:-1]
                    else:
                        author = str(authorTemp).replace("[", "").replace("]","")
                        author = author.replace("'","")
                    # if only 2 authors, eliminate extra comma in bw them
                    if len(authorTemp) == 2:
                        authorStr = ""
                        for each in authorTemp:
                            authorStr += str(each).replace("'", "") + " "
                        author = authorStr[:-1]
                    else:
                        author = str(authorTemp).replace("[", "").replace("]","")
                        author = author.replace("'","")
                else:
                    familyName, sep, givenName = authorStr.partition(", ")
                    # if name has initial(s) already
                    if ("," in givenName):
                        givenName, sep, initial = givenName.partition(", ")
                        givenName = givenName[0] + "." + initial
                        givenName = givenName[0] + "." + initial
                    else:
                        # handle case when name is not formatted correctly
                        if givenName == "":
                            givenName, sep, familyName = familyName.partition(". ")
                            initial, sep, familyName = familyName.partition(" ")
                            givenName = givenName + "." + initial[0] + "."
                            givenName = givenName + "." + initial[0] + "."
                        else:
                            givenName = givenName[0] + "."
                    author = familyName + ", " + givenName
            # handle case when multiple authors pulled from PubInfo
            else:
                authorTemp = authorStr.split("; ")
                #print(authorTemp)
                authorStr = ""
                for each in authorTemp:
                    familyName = None
                    givenName = None
                    eachTemp = str(each).replace("[", "").replace("]","")
                    #print(eachTemp)
                    if (", " in eachTemp) or ("." in eachTemp):
                        if ", " in eachTemp:
                            familyName, sep, givenName = eachTemp.partition(", ")
                        else:
                            givenName, sep, familyName = eachTemp.partition(".")
                    #print(familyName)
                    #print(givenName)
                    if familyName is not None:
                        # if name has initial(s) already
                        if (". " in familyName):
                            initial, sep, familyName = familyName.partition(". ")
                            givenName = givenName[0] + "." + initial + "."                    
                        if (". " in familyName):
                            initial, sep, familyName = familyName.partition(". ")
                            givenName = givenName[0] + "." + initial + "."                    
                        elif ("," in givenName):
                            givenName, sep, initial = givenName.partition(", ")
                            givenName = givenName[0] + "." + initial
                            givenName = givenName[0] + "." + initial
                        else:
                            givenName = givenName[0] + "."
                            familyName = familyName.strip()
                            familyName = familyName.strip()
                        if authorTemp.index(each) == (len(authorTemp)-1):
                            familyName = "& " + familyName
                        else:
                            givenName += ", "
                        authorStr += familyName + ", " + givenName
                    else:
                        if authorTemp.index(each) == (len(authorTemp)-1):
                            authorStr += "& " + eachTemp
                        else:
                            authorStr += eachTemp + ", "
                author = authorStr
        # no author was found
        else:
            author = ""
        # assign backup values if not found in desired locations
        if pub == '':
            RepoID = get_repoID(self.metadata)
            (before, sep, pub) = RepoID.partition("Repository/")
        if pubDate == "":
            #pubDate, trigger, date_created = self.get_date_modified()
            pubDate = self.get_date_modified()
            pubDate = pubDate[:4]
        DOI = self.get_url()
        information_url = get_information_url(self.metadata)
        if information_url:
            if dataset:
                citation = {"@type": "CreativeWork",
                            "citation": f"{author} ({pubDate}). {dataset}. {pub}. {DOI}",
                            "about": information_url}
            else:
                citation = {"@type": "CreativeWork",
                            "citation": f"{author} ({pubDate}). {pub}. {DOI}",
                            "about": information_url}
        else:
            if dataset:
                citation = f"{author} ({pubDate}). {dataset}. {pub}. {DOI}"
            else:
                citation = f"{author} ({pubDate}). {pub}. {DOI}"
        return delete_null_values(citation)

    def get_variable_measured(self) -> Union[List[Dict], None]:
        # Mapping: schema:variable_measured = /spase:Parameters/spase:Name, Description, Units, ValidMin, ValidMax
        # Each object is:
        #   {"@type": schema:PropertyValue, "name": Name, "description": Description, "unitText": Units}
        # Following schema:PropertyValue found at: https://schema.org/PropertyValue
        variable_measured = []
        minVal = ""
        maxVal = ""
        paramDesc = ""
        unitsFound = []
        i = 0
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
                        #elif child.tag.endswith("ValidMin"):
                            #minVal = child.text
                        #elif child.tag.endswith("ValidMax"):
                            #maxVal = child.text
                    except AttributeError as err:
                        continue
                if paramDesc and unitsFound[i]:
                    variable_measured.append({"@type": "PropertyValue", 
                                            "name": f"{paramName}",
                                            "description": f"{paramDesc}",
                                            "unitText": f"{unitsFound[i]}"})
                elif paramDesc:
                    variable_measured.append({"@type": "PropertyValue", 
                                        "name": f"{paramName}",
                                        "description": f"{paramDesc}"})
                elif unitsFound[i]:
                    variable_measured.append({"@type": "PropertyValue", 
                                        "name": f"{paramName}",
                                        "unitText": f"{unitsFound[i]}"})
                else:
                    variable_measured.append({"@type": "PropertyValue", 
                                        "name": f"{paramName}"})
                                        #"minValue": f"{minVal}",
                                        #"maxValue": f"{maxVal}"})
                i += 1
        # preserve order of elements
        if len(variable_measured) != 0:
            variable_measured = {"@list": variable_measured}
        else:
            variable_measured = None
        return delete_null_values(variable_measured)

    def get_included_in_data_catalog(self) -> None:
        included_in_data_catalog = None
        return delete_null_values(included_in_data_catalog)

    def get_subject_of(self) -> None:
        encoding_format = None
        return delete_null_values(encoding_format)

    def get_distribution(self) -> Union[List[Dict], None]:
        # Mapping: schema:distribution = /spase:AccessInformation/spase:AccessURL/spase:URL
        # AND /spase:AccessInformation/spase:Format
        # Each object is:
        #   {"@type": schema:DataDownload, "contentURL": URL, "encodingFormat": Format}
        # Following schema:DataDownload found at: https://schema.org/DataDownload
        distribution = []
        dataDownloads, potentialActions = get_accessURLs(self.metadata)
        for k, v in dataDownloads.items():
            distribution.append({"@type": "DataDownload",
                                "contentUrl": f"{k}",
                                "encodingFormat": f"{v[0]}"})
        # preserve order of elements
        if len(distribution) != 0:
            if len(distribution) > 1:
                distribution = {"@list": distribution}
            else:
                distribution = distribution[0]
        else:
            distribution = None
        return delete_null_values(distribution)

    def get_potential_action(self) -> Union[List[Dict], None]:
        # Mapping: schema:potentialAction = /spase:AccessInformation/spase:AccessURL/spase:URL
        # AND /spase:AccessInformation/spase:Format
        # Following schema:potentialAction found at: https://schema.org/potentialAction
        potential_actionList = []
        dataDownloads, potentialActions = get_accessURLs(self.metadata)
        temp_covg = self.get_temporal_coverage()
        if temp_covg is not None:
            if type(temp_covg) == str:
                start, sep, end = temp_covg.partition("/")
            else:
                start, sep, end = temp_covg["temporalCoverage"].partition("/")
            if end == "" or end == "..":
                date, sep, time = start.partition("T")
                time = time.replace("Z", "")
                if "." in time:
                    time, sep, ms = time.partition(".")
                dt_string = date + " " + time
                dt_obj = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
                # make stop time 1 second after start time
                end = dt_obj + timedelta(seconds=1)
                end = str(end).replace(" ", "T")
            startSent = f"Use {start} as default value."
            endSent = f"Use {end} as default value."
        else:
            startSent = ""
            endSent = ""

        # loop thru all AccessURLs
        for k, v in potentialActions.items():
            prodKeys = v[1]
            encoding = v[0]
            pattern = "(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(.[0-9]+)?(Z)?"

            # if link has no prodKey
            #TODO: find out what should go here!!!
            if prodKeys == "None":
                potential_actionList.append({"@type": "SearchAction",
                                            "target": {"@type": "URL",
                                                        "encodingFormat": f"{encoding}",
                                                        "url": f"{k}",
                                                        "description": f"Download dataset data as {encoding} file at this URL"}
                                            })
            else:
                # loop thru all product keys if there are multiple
                for prodKey in prodKeys:
                    prodKey = prodKey.replace("\"", "")
                    # if link is a hapi link, provide the hapi interface web service to download data
                    if "/hapi" in k:
                        potential_actionList.append({"@type": "SearchAction",
                                            "target": {"@type": "EntryPoint",
                                                        "contentType": f"{encoding}",
                                                        "urlTemplate": f"{k}/data?id={prodKey}&time.min=(start)&time.max=(end)",
                                                        "description": "Download dataset labeled by id in CSV format based on the requested start and end dates",
                                                        "httpMethod": "GET"},
                                            "query-input": [
                                                {"@type": "PropertyValueSpecification",
                                                "valueName": "start",
                                                "description": f"A UTC ISO DateTime. {startSent}",
                                                "valueRequired": False,
                                                "valuePattern": f"{pattern}"},
                                                {"@type": "PropertyValueSpecification",
                                                "valueName": "end",
                                                "description": f"A UTC ISO DateTime. {endSent}",
                                                "valueRequired": False,
                                                "valuePattern": f"{pattern}"}
                                            ]
                        })
                    # use GSFC CDAWeb portal to download CDF
                    else:
                        potential_actionList.append({"@type": "SearchAction",
                                                "target": {"@type": "URL",
                                                            "encodingFormat": f"{encoding}",
                                                            "url": f"{k}",
                                                            "description": "Download dataset data as CDF or CSV file at this URL"}
                                                })
        # preserve order of elements
        if len(potential_actionList) != 0:
            potential_action = {"@list": potential_actionList}
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
                #print("Taken from RevisionHistory")
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
        #   {temporalCoverage: StartDate and StopDate|RelativeStopDate, temporal: Cadence}
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
        SPASE_Location = ".//spase:" + f"{desiredTag[1]}/spase:TemporalDescription/spase:Cadence"
        repeat_frequency = self.metadata.findtext(
            SPASE_Location,
            namespaces=self.namespaces,
        )

        explanation = ""

        if start:
            if stop:
                if repeat_frequency:
                    explanation = get_cadenceContext(repeat_frequency)
                    temporal_coverage = {"@type": "DateTime",
                                        "temporalCoverage": f"{start}/{stop}",
                                        "temporal": {"temporal": repeat_frequency,
                                                    "description": explanation}
                    }
                else:
                    temporal_coverage = f"{start}/{stop}"
            else:
                if repeat_frequency:
                    explanation = get_cadenceContext(repeat_frequency)
                    temporal_coverage = {"@type": "DateTime",
                                        "temporalCoverage": f"{start}/..",
                                        "temporal": {"temporal": repeat_frequency,
                                                    "description": explanation}
                    }
                else:
                    temporal_coverage = f"{start}/.."
        else:
            temporal_coverage = None
        return delete_null_values(temporal_coverage)

    def get_spatial_coverage(self) -> Union[List[Dict], None]:
        # Mapping: schema:spatial_coverage = list of spase:NumericalData/spase:ObservedRegion/*
        # Each object is:
        #   {"@type": schema:Place, "@id": URI}
        # Using URIs, as defined in: https://github.com/polyneme/topst-spase-rdf-tools/blob/main/data/spase.owl
        spatial_coverage = []
        desiredTag = self.desiredRoot.tag.split("}")
        SPASE_Location = ".//spase:" + f"{desiredTag[1]}/spase:ObservedRegion"
        for item in self.metadata.findall(
            SPASE_Location,
            namespaces=self.namespaces,
        ):
            spatial_coverage.append(
                {
                    "@type": "schema:Place",
                    "identifier": f"http://www.spase-group.org/data/schema/{item.text.replace('.', '_').upper()}",
                    "alternateName": item.text,
                }
            )
        # preserve order of elements
        if len(spatial_coverage) != 0:
            spatial_coverage = {"@list": spatial_coverage}
        else:
            spatial_coverage = None
        return delete_null_values(spatial_coverage)

    def get_creator(self) -> Union[List, None]:
        # Mapping: schema:creator = spase:ResourceHeader/spase:PublicationInfo/spase:Authors 
        # OR schema:creator = spase:ResourceHeader/spase:Contact/spase:PersonID
        # Each item is:
        #   {@type: Role, roleName: Contact Role, creator: {@type: Person, name: Author Name, givenName: First Name, familyName: Last Name}}
        # Using schema:Creator as defined in: https://schema.org/creator
        author, authorRole, pubDate, pub, contributor, dataset, backups, contactsList = get_authors(self.metadata)
        authorStr = str(author).replace("[", "").replace("]","")
        creator = []
        multiple = False
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
                # add call to get ORCiD and affiliation here
                authorStr, givenName, familyName = nameSplitter(person)
                orcidID, affiliation = get_ORCiD_and_Affiliation(person, self.file)
                creatorEntry = creatorFormat(authorRole[index], authorStr, givenName, familyName, affiliation, orcidID)
                creator.append(creatorEntry)
        # if all creators were found in PublicationInfo/Authors
        else:
            # if there are multiple authors
            if (";" in authorStr) or (".," in authorStr):
                if (";" in authorStr):
                    author = authorStr.split("; ")
                else:
                    author = authorStr.split("., ")
                # iterate over each person in author string
                for person in author:
                    # get rid of extra quotations
                    person = person.replace("'","")
                    # if first name doesnt have a period, check if it is an initial
                    if (not person.endswith(".")):
                        # if first name is an initial w/o a period, add one
                        grp = re.search(r'[\.\s]{1}[\w]{1}$', person)
                        if grp is not None:
                            person += "."
                    # remove 'and' from name
                    if "and " in person:
                        person = person.replace("and ", "")
                    if authorRole == ["Author"]:
                        if ", " in person:
                            familyName, sep, givenName = person.partition(", ")
                        else:
                            givenName, sep, familyName = person.partition(". ")
                            givenName += "."
                        # add call to ORCiD and affiliation
                        # iterate thru contacts to find one that matches the current person
                        for contact in contactsList:
                            firstName, sep, lastName = contact.rpartition(".")
                            firstName, sep, initial = firstName.partition(".")
                            path, sep, firstName = firstName.rpartition("/")
                            #print("First: " + firstName + "\nInitial: " + initial + "\nLast: " + lastName)
                            if (firstName in person) and (initial in person) and (lastName in person):
                                matchingContact = contact
                        orcidID, affiliation = get_ORCiD_and_Affiliation(matchingContact, self.file)
                        creatorEntry = creatorFormat(authorRole[0], person, givenName, familyName, affiliation, orcidID)
                        creator.append(creatorEntry)
            # if there is only one author listed
            else:
                # get rid of extra quotations
                person = authorStr.replace("\"","")
                if authorRole == ["Author"]:
                    familyName, sep, givenName = person.partition(",")
                    # handle case when name is not formatted correctly
                    if givenName == "":
                        givenName, sep, familyName = familyName.partition(". ")
                        initial, sep, familyName = familyName.partition(" ")
                        givenName = givenName + ". " + initial[0] + "."
                    # add call to get ORCiD and affiliation
                    # iterate thru contacts to find one that matches the current person
                    for contact in contactsList:
                        firstName, sep, lastName = contact.rpartition(".")
                        firstName, sep, initial = firstName.partition(".")
                        if (firstName in person) and (initial in person) and (lastName in person):
                            matchingContact = contact
                    orcidID, affiliation = get_ORCiD_and_Affiliation(matchingContact, self.file)
                    creatorEntry = creatorFormat(authorRole[0], person, givenName, familyName, affiliation, orcidID)
                    creator.append(creatorEntry)
        # preserve order of elements
        if len(creator) != 0:
            creator = {"@list": creator}
        else:
            creator = None
        return delete_null_values(creator)

    def get_contributor(self) -> Union[List, None]:
        # Mapping: schema:contributor = spase:ResourceHeader/spase:Contact/spase:PersonID
        # Each item is:
        #   {@type: Role, roleName: Contributor or curator role, contributor: {@type: Person, name: Author Name, givenName: First Name, familyName: Last Name}}
        # Using schema:Person as defined in: https://schema.org/Person
        author, authorRole, pubDate, pub, contributors, dataset, backups, contactsList = get_authors(self.metadata)
        contributor = []
        # holds role values that are not initially considered for contributor var
        CuratorRoles = ["HostContact", "GeneralContact", "DataProducer", "MetadataContact", "TechnicalContact"]
        
        for person in contributors:
            # add call to get ORCiD and affiliation
            contributorStr, givenName, familyName = nameSplitter(person)
            orcidID, affiliation = get_ORCiD_and_Affiliation(person, self.file)
            individual = contributorFormat("Contributor", contributorStr, givenName, familyName, affiliation, orcidID)
            contributor.append(individual)
        # if no contributor found use backups (editors)
        if contributor == []:
            found = False
            i = 0
            # while a curator is not found
            while not found and i < len(CuratorRoles):
                # search for roles in backups that match CuratorRoles (in order of priority)
                keys = [key for key, val in backups.items() if CuratorRoles[i] in val]
                if keys != []:
                    for key in keys:
                        # add call to get ORCiD and affiliation
                        editorStr, givenName, familyName = nameSplitter(key)
                        orcidID, affiliation = get_ORCiD_and_Affiliation(key, self.file)
                        individual = contributorFormat(CuratorRoles[i], editorStr, givenName, familyName, affiliation, orcidID)
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
        # OR spase:AccessInformation/spase:RepositoryID
        # Each item is:
        #   {@type: Organization, name: PublishedBy OR Contact (if Role = Publisher) OR RepositoryID}
        # Using schema:Organization as defined in: https://schema.org/Organization
        author, authorRole, pubDate, publisher, contributor, dataset, backups, contactsList = get_authors(self.metadata)
        if publisher == "":
            #publisher = None
            RepoID = get_repoID(self.metadata)
            (before, sep, publisher) = RepoID.partition("Repository/")
        #else:
        if ("SDAC" in publisher) or ("Solar Data Analysis Center" in publisher):
            publisher = {"@id": "https://ror.org/04rvfc379",
                            "@type": "Organization",
                            "name": f"{publisher}",
                            "url": "https://ror.org/04rvfc379"}
        elif ("SPDF" in publisher) or ("Solar Physics Data Facility" in publisher):
            publisher = {"@id": "https://ror.org/00ryjtt64",
                            "@type": "Organization",
                            "name": f"{publisher}",
                            "url": "https://ror.org/00ryjtt64"}
        else:
            publisher = {"@type": "Organization",
                            "name": f"{publisher}"}
        return delete_null_values(publisher)

    def get_funding(self) -> Union[List[Dict], None]:
        # Mapping: schema:funding = spase:ResourceHeader/spase:Funding/spase:Agency 
        # AND spase:ResourceHeader/spase:Funding/spase:Project
        # AND spase:ResourceHeader/spase:Funding/spase:AwardNumber
        # Each item is:
        #   {@type: MonetaryGrant, funder: {@type: Person or Organization, name: Agency}, identifier: AwardNumber, name: Project}
        # Using schema:MonetaryGrant as defined in: https://schema.org/MonetaryGrant
        funding = []
        agency = []
        project = []
        award = []
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
            for funder in agency:
                # if award number was found
                if award:
                    funding.append({"@type": "MonetaryGrant",
                                    "funder": {"@type": "Organization",
                                                "name": f"{funder}"
                                    },
                                    "identifier": f"{award[i]}",
                                    "name": f"{project[i]}"
                                    })
                # if award number was not found
                else:
                    # funded by an agency
                    if ";" not in funder:
                        funding.append({"@type": "MonetaryGrant",
                                        "funder": {"@type": "Organization",
                                                    "name": f"{funder}"
                                        },
                                        "name": f"{project[i]}"
                                    })
                    # funded by a person and/thru an agency
                    else:
                        org, sep, person = funder.partition("; ")
                        funding.append({"@type": "MonetaryGrant",
                                        "funder": [{"@type": "Organization",
                                                    "name": f"{org}"},
                                                    {"@type": "Person",
                                                    "name": f"{person}"}
                                        ],
                                        "name": f"{project[i]}"
                                    })
                i += 1
        # preserve order of elements
        if len(funding) != 0:
            funding = {"@list": funding}
        else:
            funding = None
        return delete_null_values(funding)

    def get_license(self) -> Union[List, None]:
        # Mapping: schema:license = spase:AccessInformation/spase:rightsList/spase:rights
        # Using schema:license as defined in: https://schema.org/license
        license_url = []
        # format in xml file is below
        """<rightsList>
            <rights xml:lang="en"
            schemeURI="https://spdx.org/licenses/"
            rightsIdentifierScheme="SPDX"
            rightsIdentifier="CC-BY-4.0"
            rightsURI="https://creativecommons.org/licenses/by/4.0/">
            Creative Commons Attribution 4.0 International</rights>
        </rightsList>"""

        desiredTag = self.desiredRoot.tag.split("}")
        SPASE_Location = ".//spase:" + f"{desiredTag[1]}/spase:AccessInformation/spase:rightsList/spase:rights"
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
        return license_url

    def get_was_revision_of(self) -> Union[Dict, None]:
        # Mapping: schema:wasRevisionOf = spase:Association/spase:AssociationID
        #   (if spase:AssociationType is "RevisionOf")
        #schema:wasRevisionOf found at https://www.w3.org/TR/prov-o/#wasRevisionOf
        relations = []
        for child in self.desiredRoot.iter(tag=etree.Element):
            if child.tag.endswith("Association"):
                targetChild = child
                for child in targetChild:
                    if child.tag.endswith("AssociationID"):
                        A_ID = child.text
                    elif child.tag.endswith("AssociationType"):
                        type = child.text
                if type == "RevisionOf":
                    relations.append(A_ID)
        if relations == []:
            was_revision_of = None
        else:
            was_revision_of = {"@id": f"{relations}"}
        return delete_null_values(was_revision_of)

    def get_was_derived_from(self) -> Union[Dict, None]:
        # Mapping: schema:wasDerivedFrom = spase:Association/spase:AssociationID
        #   (if spase:AssociationType is "DerivedFrom" or "ChildEventOf")
        # schema:wasDerivedFrom found at https://www.w3.org/TR/prov-o/#wasDerivedFrom
        was_derived_from = None
        was_derived_from = self.get_is_based_on()
        return delete_null_values(was_derived_from)

    def get_is_based_on(self) -> Union[Dict, None]:
        # Mapping: schema:isBasedOn = spase:Association/spase:AssociationID
        #   (if spase:AssociationType is "DerivedFrom" or "ChildEventOf")
        # schema:isBasedOn found at https://schema.org/isBasedOn
        is_based_on = []
        derivations = []
        for child in self.desiredRoot.iter(tag=etree.Element):
            if child.tag.endswith("Association"):
                targetChild = child
                for child in targetChild:
                    if child.tag.endswith("AssociationID"):
                        A_ID = child.text
                    elif child.tag.endswith("AssociationType"):
                        type = child.text
                if type == "DerivedFrom" or type == "ChildEventOf":
                    derivations.append(A_ID)
        if derivations == []:
            is_based_on = None
        else:
            is_based_on = {"@id": f"{derivations}"}
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
    Takes an XML tree and scrapes the desired authors (with their roles), publication date,
        publisher, contributors, and publication title. Also scraped are the names and roles of
        the backups, which are any Contacts found that are not considered authors. It then returns 
        these items, with the author, author roles, and contributors as lists and the rest as strings,
        except for the backups which is a dictionary.

    :param metadata:    The SPASE metadata object as an XML tree.
    :type entry: etree.ElementTree object
    :returns: The highest priority authors found within the SPASE record as a list
                as well as a list of their roles, the publication date, publisher,
                contributors, and the title of the publication. It also returns any contacts found,
                along with their role(s), that were not considered for the author role.
    :rtype: tuple
    """
    # local vars needed
    author = []
    contactsList = []
    authorRole = []
    pubDate = ""
    pub = ""
    contributor = []
    dataset = ""
    backups = {}
    PI_child = None
    priority = False
    root = metadata.getroot()
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desiredRoot = elt

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
                                    PersonID = child.text
                                    backups[PersonID] = []
                                    # add to ContactsList
                                    contactsList.append(PersonID)
                                # find Role
                                elif child.tag.endswith("Role"):
                                    # backup author
                                    if ("PrincipalInvestigator" or "PI" or "CoInvestigator") in child.text:
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
                                    elif child.text == "Contributor":
                                        contributor.append(PersonID)
                                    # backup publisher
                                    elif child.text == "Publisher":
                                        pub = child.text
                                    else:
                                        # use list for values in case one person has multiple roles
                                        backups[PersonID] += [child.text]
                            except AttributeError as err:
                                continue
                except AttributeError as err:
                    continue
    if PI_child is not None:
        for child in PI_child.iter(tag=etree.Element):
            # collect preferred author
            if child.tag.endswith("Authors"):
                author = [child.text]
                authorRole = ["Author"]
            elif child.tag.endswith("PublicationDate"):
                pubDate = child.text
            # collect preferred publisher
            elif child.tag.endswith("PublishedBy"):
                pub = child.text
            # collect preferred dataset
            elif child.tag.endswith("Title"):
                dataset = child.text
    return author, authorRole, pubDate, pub, contributor, dataset, backups, contactsList

def getPaths(entry, paths) -> list:
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

def get_accessURLs(metadata: etree.ElementTree) -> tuple:
    """
    :param metadata:    The SPASE metadata object as an XML tree.
    
    :returns: The AccessURLs found in the SPASE record, separated into two dictionaries,
                dataDownloads and potentialActions, depending on if they are a direct 
                link to data or not. These dictionaries are setup to have the keys as
                the url and the values to be a list containing their data format(s)
                (and product key if applicable).
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
        #print(f"Adding {item.text} to encoding list.")
        encoding.append(item.text)
    #print(len(encoding))

    # iterate thru children to locate Access Information
    for child in desiredRoot.iter(tag=etree.Element):
        if child.tag.endswith("AccessInformation"):
            targetChild = child
            # iterate thru children to locate AccessURL and Format
            for child in targetChild:
                if child.tag.endswith("AccessURL"):
                    targetChild = child
                    # iterate thru children to locate URL
                    for child in targetChild:
                        if child.tag.endswith("URL"):
                            url = child.text
                            # provide "NULL" value in case no keys are found
                            AccessURLs[url] = []
                            # append an encoder for each URL
                            encoder.append(encoding[j])
                            #print(f"Adding {encoding[j]} to encoder list")
                        # check if URL has a product key
                        elif child.tag.endswith("ProductKey"):
                            prodKey = child.text
                            # if only one prodKey exists
                            if AccessURLs[url] == []:
                                AccessURLs[url] = [prodKey]
                            # if multiple prodKeys exist
                            else:
                                AccessURLs[url] += [prodKey]
                    #print(f"leaving {url}")
            #print(f"exiting AccessInfo #{j}")
            j += 1
    for k, v in AccessURLs.items():
        # if URL has no access key
        if not v:
            #print(i)
            NonDataFileExt = ['html', 'com', 'gov', 'edu', 'org', 'eu', 'int']
            DataFileExt = ['csv', 'cdf', 'fits', 'txt', 'nc', 'json', 'jpeg',
                           'png', 'gif', 'tar', 'netcdf3', 'netcdf4', 'hdf5',
                           'zarr', 'asdf', 'zip']
            protocol, sep, domain = k.partition("://")
            domain, sep, path = domain.partition("/")
            domain, sep, ext = domain.rpartition(".")
            # see if file extension is one associated w data files
            #print(ext)
            if ext not in DataFileExt:
                downloadable = False
            else:
                downloadable = True
            # if URL is direct link to download data, add to the dataDownloads dictionary
            if downloadable:
                dataDownloads[k] = [encoder[i]]
            else:
                potentialActions[k] = [encoder[i], "None"]
        # if URL has access key, add to the potentialActions dictionary
        else:
            potentialActions[k] = [encoder[i], v]
        i += 1
    return dataDownloads, potentialActions

def get_dates(metadata: etree.ElementTree) -> tuple:
    """
    :param metadata:    The SPASE metadata object as an XML tree.

    :returns:   The ReleaseDate and a list of all the dates found in RevisionHistory
    """
    root = metadata.getroot()
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desiredRoot = elt
    RevisionHistory = []
    ReleaseDate = ""

    for child in desiredRoot.iter(tag=etree.Element):
        if child.tag.endswith("ResourceHeader"):
            targetChild = child
            for child in targetChild:
                # find ReleaseDate
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
                                    dt_obj = datetime.strptime(dt_string,
                                                            "%Y-%m-%d %H:%M:%S")
                                    RevisionHistory.append(dt_obj)
                except AttributeError as err:
                    continue
    return ReleaseDate, RevisionHistory

def get_repoID(metadata: etree.ElementTree) -> str:
    """
    :param metadata:    The SPASE metadata object as an XML tree.

    :returns:   The RepositoryID found in the last AccessInformation section
    """
    root = metadata.getroot()
    repoID = None
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desiredRoot = elt
    for child in desiredRoot.iter(tag=etree.Element):
        if child.tag.endswith("AccessInformation"):
            targetChild = child
            # iterate thru children to locate RepositoryID
            for child in targetChild:
                if child.tag.endswith("RepositoryID"):
                    repoID = child.text
    return repoID

def contributorFormat(roleName:str, name:str, givenName:str, familyName:str, affiliation:str, orcidID:str) -> Dict:
    """
    :param roleName: The value found in the Role field associated with this Contact
    :param name: The full name of the Contact, as formatted in the SPASE record
    :param givenName: The first name/initial and middle name/initial of the Contact
    :param familyName: The last name of the Contact
    :param affiliation: The organization this Contact is affiliated with.
    :param orcidID: The ORCiD identifier for this Contact

    :returns:   The entry in the correct format to append to the contributor dictionary
    """
    
    domain, sep, orcidVal = orcidID.rpartition("/")

    if orcidID:
        contact = {"@type": "Role", 
                    "roleName": f"{roleName}",
                    "contributor": {"@type": "Person",
                                    "name": f"{name}",
                                    "givenName": f"{givenName}",
                                    "familyName": f"{familyName}",
                                    "affiliation": {"@type": "Organization",
                                                    "name": f"{affiliation}"},
                                    "identifier": {"@id": f"https://orcid.org/{orcidID}",
                                                    "@type": "PropertyValue",
                                                    "propertyID": "https://registry.identifiers.org/registry/orcid",
                                                    "url": f"https://orcid.org/{orcidID}",
                                                    "value": f"orcid:{orcidVal}"}}
                    }
    else:
        contact = {"@type": "Role", 
                "roleName": f"{roleName}",
                "contributor": {"@type": "Person",
                                "name": f"{name}",
                                "givenName": f"{givenName}",
                                "familyName": f"{familyName}",
                                "affiliation": {"@type": "Organization",
                                                "name": f"{affiliation}"}}
                }

    return contact

def creatorFormat(roleName:str, name:str, givenName:str, familyName:str, affiliation:str, orcidID:str) -> Dict:
    """
    :param roleName: The value found in the Role field associated with this Contact
    :param name: The full name of the Contact, as formatted in the SPASE record
    :param givenName: The first name/initial and middle name/initial of the Contact
    :param familyName: The last name of the Contact
    :param affiliation: The organization this Contact is affiliated with.
    :param orcidID: The ORCiD identifier for this Contact

    :returns:   The entry in the correct format to append to the creator dictionary
    """

    domain, sep, orcidVal = orcidID.rpartition("/")
    if orcidID:
        creator = {"@type": "Role", 
                    "roleName": f"{roleName}",
                    "creator": {"@type": "Person",
                                "name": f"{name}",
                                "givenName": f"{givenName}",
                                "familyName": f"{familyName}",
                                "affiliation": {"@type": "Organization",
                                                "name": f"{affiliation}"},
                                "identifier": {"@id": orcidID,
                                                "@type": "PropertyValue",
                                                "propertyID": "https://registry.identifiers.org/registry/orcid",
                                                "url": f"{orcidID}",
                                                "value": f"orcid:{orcidVal}"}}
                        }
    else:
        creator = {"@type": "Role", 
                    "roleName": f"{roleName}",
                    "creator": {"@type": "Person",
                                "name": f"{name}",
                                "givenName": f"{givenName}",
                                "familyName": f"{familyName}",
                                "affiliation": {"@type": "Organization",
                                                "name": f"{affiliation}"}}
                    }
    return creator

def nameSplitter(person:str) -> tuple:
    """
    :param person:    The string found in the Contacts field as is formatted in the SPASE record.

    :returns:   The string containing only the full name of the Contact, the string containing the first name/initial of the Contact,
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

def get_measurement_type(metadata: etree.ElementTree) -> Union[Dict, None]:
    """
    :param metadata:    The SPASE metadata object as an XML tree.

    :returns:   The values found in the MeasurementType field(s) formatted as a dictionary
    """
    root = metadata.getroot()
    measurement_type = None
    measurementTypes = []
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desiredRoot = elt
    for child in desiredRoot.iter(tag=etree.Element):
        if child.tag.endswith("MeasurementType"):
            measurementTypes.append(child.text)
    if measurementTypes:
        measurement_type = {"@type": "DefinedTerm",
                            "keywords": measurementTypes}
    return measurement_type

def get_information_url(metadata: etree.ElementTree) -> Union[List[Dict], None]:
    """
    :param metadata:    The SPASE metadata object as an XML tree.

    :returns:   The name, description, and url(s) for all InformationURL sections found in the ResourceHeader,
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
    :param metadata:    The SPASE metadata object as an XML tree.
    :param path:    The absolute file path of the XML file the user wishes to pull info from.

    :returns:   The name, url(s), and ResourceID for each instrument found in the InstrumentID section,
                formatted as a list of dictionaries.
    """
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
        # from there grab name and infoURLs
        for item in instrumentIDs:
            instrumentIDs[item]["name"] = ""
            instrumentIDs[item]["URL"] = []
            absPath, sep, after = path.partition("NASA/")
            record = absPath + item.replace("spase://","") + ".xml"
            record = record.replace("'","")
            if os.path.isfile(record):
                testSpase = SPASE(record)
                root = testSpase.metadata.getroot()
                instrumentIDs[item]["name"] = testSpase.get_name()
                allURL_Info = get_information_url(testSpase.metadata)
                if allURL_Info:
                    for each in allURL_Info:
                        instrumentIDs[item]["URL"].append(each["url"])
        for k in instrumentIDs.keys():
            if instrumentIDs[k]["URL"]:
                instrument.append({"@type": "IndividualProduct",
                                    "identifier": k,
                                    "name": instrumentIDs[k]["name"],
                                    "url": instrumentIDs[k]["URL"]})
            else:
                instrument.append({"@type": "IndividualProduct",
                                "identifier": k,
                                "name": instrumentIDs[k]["name"]})
    return instrument

def get_observatory(metadata: etree.ElementTree, path: str) -> Union[List[Dict], None]:
    """
    :param metadata:    The SPASE metadata object as an XML tree.
    :param path:    The absolute file path of the XML file the user wishes to pull info from.

    :returns:   The name, url(s), and ResourceID for each observatory related to this dataset,
                formatted as a list of dictionaries.
    """
    instrument = get_instrument(metadata, path)
    if instrument is not None:
        observatory = []
        observatoryGroupID = ""
        observatoryID = ""
        recordedIDs = []
        instrumentIDs = []
        # follow link provided by instrument to instrument page, from there grab ObservatoryID
        # then follow link provided by ObservatoryID to grab name, infoURL, and ObservatoryGrpID
        # finally, follow that link to grab name and infoURL from there
        for each in instrument:
            instrumentIDs.append(each["identifier"])
        for item in instrumentIDs:
            absPath, sep, after = path.partition("NASA/")
            record = absPath + item.replace("spase://","") + ".xml"
            record = record.replace("'","")
            if os.path.isfile(record):
                testSpase = SPASE(record)
                root = testSpase.metadata.getroot()
                for elt in root.iter(tag=etree.Element):
                    if elt.tag.endswith("Instrument"):
                        desiredRoot = elt
                for child in desiredRoot.iter(tag=etree.Element):
                    if child.tag.endswith("ObservatoryID"):
                        observatoryID = child.text
                # use observatoryID as record to get observatoryGroupID and other info              
                record = absPath + observatoryID.replace("spase://","") + ".xml"
                record = record.replace("'","")                
                if os.path.isfile(record):
                    url = []
                    testSpase = SPASE(record)
                    root = testSpase.metadata.getroot()
                    for elt in root.iter(tag=etree.Element):
                        if elt.tag.endswith("Observatory"):
                            desiredRoot = elt
                    for child in desiredRoot.iter(tag=etree.Element):
                        if child.tag.endswith("ObservatoryGroupID"):
                            observatoryGroupID = child.text
                    name = testSpase.get_name()
                    infoURL = get_information_url(testSpase.metadata)
                    if infoURL:
                        for each in infoURL:
                            url.append(each["url"])
                    # if there is a groupID, use that link to provide info on it as well
                    if observatoryGroupID:
                        record = absPath + observatoryGroupID.replace("spase://","") + ".xml"
                        record = record.replace("'","")                
                        if os.path.isfile(record):
                            groupURL = []
                            testSpase = SPASE(record)
                            groupName = testSpase.get_name()
                            groupInfoURL = get_information_url(testSpase.metadata)
                            if groupInfoURL:
                                for each in groupInfoURL:
                                    groupURL.append(each["url"])
                                if observatoryGroupID not in recordedIDs:
                                    observatory.append({"@type": "ResearchProject",
                                                        "@id": observatoryGroupID,
                                                        "name": groupName,
                                                        "url": groupURL})
                                    recordedIDs.append(observatoryGroupID)
                            elif observatoryGroupID not in recordedIDs:
                                observatory.append({"@type": "ResearchProject",
                                                    "@id": observatoryGroupID,
                                                    "name": groupName})
                                recordedIDs.append(observatoryGroupID)
                    if url and (observatoryID not in recordedIDs):
                        observatory.append({"@type": "ResearchProject",
                                            "@id": observatoryID,
                                            "name": name,
                                            "url": url})
                        recordedIDs.append(observatoryID)
                    elif observatoryID not in recordedIDs:
                        observatory.append({"@type": "ResearchProject",
                                        "@id": observatoryID,
                                        "name": name})
                        recordedIDs.append(observatoryGroupID)
    else:
        observatory = None
    return observatory

def get_alternate_name(metadata: etree.ElementTree) -> Union[str, None]:
    """
    :param metadata:    The SPASE metadata object as an XML tree.

    :returns:   The alternate name of the dataset as a string.
    """
    root = metadata.getroot()
    alternate_name = None
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desiredRoot = elt
    for child in desiredRoot.iter(tag=etree.Element):
        if child.tag.endswith("ResourceHeader"):
            targetChild = child
            # iterate thru children to locate AccessURL and Format
            for child in targetChild:
                try:
                    if child.tag.endswith("AlternateName"):
                        alternate_name = child.text
                except AttributeError:
                    continue
    return alternate_name

def get_cadenceContext(cadence:str) -> str:
    """
    :param cadence:    The value found in the Cadence field of the TemporalDescription section

    :returns:   A string description of what this value represents/means.
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

def get_is_related_to(metadata: etree.ElementTree) -> Union[Dict, None]:
    """
    :param metadata:    The SPASE metadata object as an XML tree.

    :returns:   The ID's of other SPASE records related to this one in some way, as a dictionary.
    """
    # schema:isRelatedTo found at https://schema.org/isRelatedTo
    root = metadata.getroot()
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desiredRoot = elt
    relations = []
    for child in desiredRoot.iter(tag=etree.Element):
        if child.tag.endswith("Association"):
            targetChild = child
            for child in targetChild:
                if child.tag.endswith("AssociationID"):
                    A_ID = child.text
                elif child.tag.endswith("AssociationType"):
                    type = child.text
            if type == "Other":
                relations.append(A_ID)
    if relations == []:
        is_related_to = None
    else:
        is_related_to = {"@id": f"{relations}"}
    return is_related_to

def get_is_part_of(metadata: etree.ElementTree) -> Union[Dict, None]:
    """
    :param metadata:    The SPASE metadata object as an XML tree.

    :returns:   The ID(s) of the larger resource this SPASE record is a portion of, as a dictionary.
    """
    # schema:isPartOf found at https://schema.org/isPartOf
    root = metadata.getroot()
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desiredRoot = elt
    relations = []
    for child in desiredRoot.iter(tag=etree.Element):
        if child.tag.endswith("Association"):
            targetChild = child
            for child in targetChild:
                if child.tag.endswith("AssociationID"):
                    A_ID = child.text
                elif child.tag.endswith("AssociationType"):
                    type = child.text
            if type == "PartOf":
                relations.append(A_ID)
    if relations == []:
        is_part_of = None
    else:
        is_part_of = {"@id": f"{relations}"}
    return is_part_of

def get_ORCiD_and_Affiliation(PersonID: str, file: str) -> tuple:
    # takes PersonID and follows its link to get ORCIdentifier and OrganizationName
    orcidID = ""
    affiliation = ""
    absPath, sep, after = file.partition("NASA/")
    record = absPath + PersonID.replace("spase://","") + ".xml"
    record = record.replace("'","")
    if os.path.isfile(record):
        testSpase = SPASE(record)
        root = testSpase.metadata.getroot()
        for elt in root.iter(tag=etree.Element):
            if elt.tag.endswith("Person"):
                desiredRoot = elt
        for child in desiredRoot.iter(tag=etree.Element):
            if child.tag.endswith("ORCIdentifier"):
                orcidID = child.text
            elif child.tag.endswith("OrganizationName"):
                affiliation = child.text
    return orcidID, affiliation

def main(folder, printFlag = True, desiredProperties = ["id", "identifier", "sameAs", "url", "name", "description", "date_published",
                                                        "keywords", "creator", "citation", "temporal_coverage", "spatial_coverage",
                                                        "publisher", "distribution", "potential_action", "variable_measured", 
                                                        "funding", "license", "was_revision_of", "was_derived_from", "is_based_on", 
                                                        "is_related_to", "is_part_of", "date_created", "date_modified", "contributor",
                                                        "measurement_type", "instrument", "observatory", "alternate_name", "inLanguage"]) -> None:
    # list that holds SPASE records already checked
    searched = []
    SPASE_paths = []

    # obtains all filepaths to all SPASE records found in given directory
    SPASE_paths = getPaths(folder, SPASE_paths)
    #print("You entered " + folder)
    if len(SPASE_paths) == 0:
        print("No records found. Returning.")
    else:
        #print("The number of records is " + str(len(SPASE_paths)))
        # iterate through all SPASE records
        # Note: starting at record 24 in ACE/EPAM folder, end of author string is formatted wrong with "and first last" instead of "and last, first" (SPASE issue)
        # Successfully passed for all 129 records in NumericalData/ACE/EPAM folder and all 187 in DisplayData
        # In DisplayData, records 130, 167-70 has authors formatted wrong
        # DisplayData: record 70 is ex w multiple contacts, ACE has ex's w multiple authors
        # ReleaseDate is not most recent at this dataset (causes dateModified to be incorrect): C:/Users/zboquet/NASA/DisplayData\SDO\AIA\SSC
        #   And some here too: C:/Users/zboquet/NASA/DisplayData\STEREO-A\SECCHI\, C:/Users/zboquet/NASA/DisplayData\STEREO-B\SECCHI
        #                       C:/Users/zboquet/NASA/NumericalData\Cluster-Rumba\WBD\BM2
        # DD: #134 is ex w a LOT of observatory entries thanks to multiple instruments
        # record NASA/DisplayData\OBSPM/H-ALPHA.xml has broken instrumentID link
        # record NASA/DisplayData/UCLA/Global-MHD-code/mS1-Vx/PT10S.xml has extra spacing in PubInfo/Authors
        for r, record in enumerate(SPASE_paths):
            if record not in searched:
                # scrape metadata for each record
                statusMessage = f"Extracting metadata from record {r+1}"
                statusMessage += f" of {len(SPASE_paths)}"
                print(statusMessage)
                print(record)
                print()
                testSpase = SPASE(record)

                #print(testSpase.get_is_accessible_for_free())
                id = testSpase.get_id()
                url = testSpase.get_url()
                name = testSpase.get_name()
                sameAs = testSpase.get_same_as()
                keywords = testSpase.get_keywords()
                citation = testSpase.get_citation()
                identifier = testSpase.get_identifier()
                creator = testSpase.get_creator()
                publisher = testSpase.get_publisher()
                contributor = testSpase.get_contributor()
                variable_measured = testSpase.get_variable_measured()
                temporal_coverage = testSpase.get_temporal_coverage()
                spatial_coverage = testSpase.get_spatial_coverage()
                distribution = testSpase.get_distribution()
                potential_action = testSpase.get_potential_action()
                funding = testSpase.get_funding()
                license = testSpase.get_license()
                date_created = testSpase.get_date_created()
                #date_modified, trigger, mostRecentDate = testSpase.get_date_modified()
                date_modified = testSpase.get_date_modified()
                date_published = testSpase.get_date_published()
                was_revision_of = testSpase.get_was_revision_of()
                was_derived_from = testSpase.get_was_derived_from()
                is_based_on = testSpase.get_is_based_on()
                #is_related_to, ObsBy, Part = get_is_related_to(testSpase.metadata)
                is_related_to = get_is_related_to(testSpase.metadata)
                is_part_of = get_is_part_of(testSpase.metadata)
                measurement_type = get_measurement_type(testSpase.metadata)
                instrument = get_instrument(testSpase.metadata, record)
                observatory = get_observatory(testSpase.metadata, record)
                alternate_name = get_alternate_name(testSpase.metadata)
                inLanguage = 'en'

                if printFlag:
                    for property in desiredProperties:
                        if property == "id":
                            print(" @id:", end=" ")
                            print(json.dumps(id, indent=4))
                        elif property == "sameAs":
                            if sameAs is not None:
                                print(" sameAs:", end=" ")
                                print(json.dumps(sameAs, indent=4))
                            else:
                                print("No PriorID(s) were found.")
                        elif property == "url":
                            print(" url:", end=" ")
                            print(json.dumps(url, indent=4))
                        elif property == "name":
                            print(" name:", end=" ")
                            print(json.dumps(name, indent=4))
                        elif property == "keywords":
                            if keywords is None:
                                print("No keywords found")
                            else:
                                print(" keywords:", end=" ")
                                print(json.dumps(keywords, indent=4))
                        elif property == "citation":
                            print(" citation:", end=" ")
                            print(json.dumps(citation, indent=4))
                        elif property == "identifier":
                            print(" identifier:", end=" ")
                            print(json.dumps(identifier, indent=4))
                        elif property == "creator":
                            if creator is not None:
                                print(" creator:", end=" ")
                                print(json.dumps(creator, indent=4))
                            else:
                                print("No creators were found according to the priority rules.")
                        elif property == "date_created":
                            if date_created is not None:
                                print(" date_created:", end=" ")
                                print(json.dumps(date_created, indent=4))
                            else:
                                print("No creation date was found.")
                        elif property == "date_modified":
                            #if trigger:
                                #print("This record has incorrect dates.")
                            #else:
                            print(" date_modified:", end=" ")
                            print(json.dumps(date_modified, indent=4))
                                #print("")
                        elif property == "date_published":
                            if date_published is not None:
                                print(" date_published:", end=" ")
                                print(json.dumps(date_published, indent=4))
                            else:
                                print("No publication date was found.")
                        elif property == "publisher":
                            if publisher is not None:
                                print(" publisher:", end=" ")
                                print(json.dumps(publisher, indent=4))
                            else:
                                print("No publisher was found.")
                        elif property == "contributor":
                            # pos 1161-2 in NumericalData
                            if contributor is not None:
                                print(" contributor:", end=" ")
                                print(json.dumps(contributor, indent=4))
                            else:
                                print("No contributors found.")
                        elif property == "distribution" or property == "potential_action":
                            if property == "distribution":
                                if distribution is not None:
                                    print(" distribution:", end=" ")
                                    print(json.dumps(distribution, indent=4))
                                    #raise ValueError("A dataDownload was found!")
                                else:
                                    print("No dataDownloads were found")
                            else:
                                if potential_action is not None:
                                    print(" potential_action:", end=" ")
                                    print(json.dumps(potential_action, indent=4))
                        elif property == "temporal_coverage":
                            if temporal_coverage is not None:
                                print(" temporal_coverage:", end=" ")
                                print(json.dumps(temporal_coverage, indent=4))
                            else:
                                print("No start/stop times were found.")
                        elif property == "spatial_coverage":
                            if spatial_coverage is not None:
                                print(" spatial_coverage:", end=" ")
                                print(json.dumps(spatial_coverage, indent=4))
                            else:
                                print("No observed regions were found.")
                        elif property == "funding":
                            if funding is not None:
                                print(" funding:", end=" ")
                                print(json.dumps(funding, indent=4))
                            else:
                                print("No funding info was found.")
                        elif property == "license":
                            if license is not None:
                                print(" license:", end=" ")
                                print(json.dumps(license, indent=4))
                            else:
                                print("No license for the dataset was found.")
                        elif property == "was_revision_of":
                            if was_revision_of is not None:
                                print(" prov:was_revision_of:", end=" ")
                                print(json.dumps(was_revision_of, indent=4))
                            else:
                                print("No was_revision_of was found.")
                        elif property == "was_derived_from":
                            if was_derived_from is not None:
                                print(" prov:was_derived_from:", end=" ")
                                print(json.dumps(was_derived_from, indent=4))
                            else:
                                print("No was_derived_from was found.")
                        elif property == "is_based_on":
                            # only 16 in DisplayData have this, none in ACE/EPAM, 6 in NumericalData
                            if is_based_on is not None:
                                print(" schema:is_based_on:", end=" ")
                                print(json.dumps(is_based_on, indent=4))
                            else:
                                print("No is_based_on was found.")
                        # only 25 in NumericalData have "ObservedBy" or "PartOf" associationIDs
                        elif property == "is_related_to":
                            if is_related_to is not None:
                                print(" schema:is_related_to:", end=" ")
                                print(json.dumps(is_related_to, indent=4))
                            else:
                                print("No is_related_to was found.")
                        elif property == "is_part_of":
                            if is_part_of is not None:
                                print(" schema:isPartOf:", end=" ")
                                print(json.dumps(is_part_of, indent=4))
                            else:
                                print("No is_part_of was found.")
                        elif property == "variable_measured":
                            if variable_measured is not None:
                                print(" variable_measured:", end=" ")
                                print(json.dumps(variable_measured, indent=4))
                            else:
                                print("No parameters found.")
                        elif property == "measurement_type":
                            if measurement_type is not None:
                                print(" measurement_type:", end=" ")
                                print(json.dumps(measurement_type, indent=4))
                            else:
                                print("No measurementType found.")
                        elif property == "instrument":
                            if instrument is not None:
                                print(" instrument:", end=" ")
                                print(json.dumps(instrument, indent=4))
                            else:
                                print("No InstrumentIDs found.")
                        elif property == "observatory":
                            if observatory is not None:
                                print(" observatory:", end=" ")
                                print(json.dumps(observatory, indent=4))
                            else:
                                print("No ObservatoryIDs found.")
                        elif property == "alternate_name":
                            if alternate_name is not None:
                                print(" alternate_name:", end=" ")
                                print(json.dumps(alternate_name, indent=4))
                            else:
                                print("No alternateName found.")
                        elif property == "inLanguage":
                            print(" inLanguage:", end=" ")
                            print(json.dumps(inLanguage, indent=4))
                print("Metadata extraction completed")
                print()

                # add record to searched
                searched.append(record)

# test directories
folder = "C:/Users/zboquet/NASA/DisplayData"
#folder = "C:/Users/zboquet/NASA/DisplayData/ACE/MAG"
#folder = "C:/Users/zboquet/NASA/NumericalData/ACE/EPAM"
folder = "C:/Users/zboquet/NASA/NumericalData/MMS/4/HotPlasmaCompositionAnalyzer/Burst/Level2/Ion"
#Other1, AssocIDs1 = 
main(folder, True, ["creator", "contributor"])

#folder = "C:/Users/zboquet/NASA/NumericalData/ACE/EPAM"
#folder = "C:/Users/zboquet/NASA/NumericalData/Cassini/MAG"
# start at list item 132 if want to skip EPAM folder
#folder = "C:/Users/zboquet/NASA/NumericalData/ACE"
# start at list item 163 if want to skip ACE folder
folder = "C:/Users/zboquet/NASA/NumericalData"
#main(folder, True, ["distribution"])


