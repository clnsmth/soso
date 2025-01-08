"""The SPASE strategy module."""

from lxml import etree
from soso.interface import StrategyInterface
from soso.utilities import (
    delete_null_values,
)
from typing import Union, List, Dict
import re
from datetime import datetime, timedelta
import pandas as pd

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
            - [subject_of]
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
            if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
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
        # Uses identifier scheme URI, provided at: https://github.com/ESIPFed/science-on-schema.org/blob/main/guides/Dataset.md#identifier
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
        authorTemp = ""
        author = []
        pubDate = ""
        pub = ""
        contributor = []
        dataset = ""
        i = 0

        authorTemp, authorRole, pubDate, pub, contributor, dataset, backups = get_authors(self.metadata)
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
                            givenName = givenName[0] + ". " + initial + "."
                        else:
                            givenName = givenName[0] + "."
                        # add commas to separate each name until last name in list
                        if (i < (len(authorTemp) - 1)):
                            author += [familyName + ", " + givenName]
                        else:
                            author += ["& " + familyName + ", " + givenName]
                        i += 1
                    # reformat author string
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
                        givenName = givenName[0] + ". " + initial + "."
                    else:
                        givenName = givenName[0] + "."
                    author = familyName + ", " + givenName
            # case when in PubInfo but only one author
            elif ";" not in authorStr:
                # in case there are multiple w/o ;
                if "., " in authorStr:
                    authorStr = authorStr.replace(".,", "..,")
                    authorTemp = authorStr.split("., ")
                    if "and " in authorTemp[-1]:
                        authorTemp[-1].replace("and ", "& ")
                    else:
                        authorTemp[-1] = "& " + authorTemp[-1]
                    author = str(authorTemp).replace("[", "").replace("]","")
                    author = author.replace("'","")
                else:
                    familyName, sep, givenName = authorStr.partition(", ")
                    # if name has initial(s) already
                    if ("," in givenName):
                        givenName, sep, initial = givenName.partition(", ")
                        givenName = givenName[0] + ". " + initial
                    else:
                        # handle case when name is not formatted correctly
                        if givenName == "":
                            givenName, sep, familyName = familyName.partition(". ")
                            initial, sep, familyName = familyName.partition(" ")
                            givenName = givenName + ". " + initial[0] + "."
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
                        if ("." in familyName):
                            initial, sep, familyName = familyName.partition(".")
                            givenName = givenName[0] + ". " + initial + "."                    
                        elif ("," in givenName):
                            givenName, sep, initial = givenName.partition(", ")
                            givenName = givenName[0] + ". " + initial
                        else:
                            givenName = givenName[0] + "."
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
            # TODO: ask if this process should be used to find backup pub
            #for child in self.desiredRoot.iter(tag=etree.Element):
                #if child.tag.endswith("AccessInformation"):
                    #targetChild = child
                    # iterate thru children to locate RepositoryID
                    #for child in targetChild:
                        #if child.tag.endswith("RepositoryID"):
                            # use partition to split text by Repository/
                            #    and assign only the text after it to pub
                            #(before, sep, pub) = child.text.partition("Repository/")
            if pub == '':
                pub = "NASA Heliophysics Digital Resource Library"
        if pubDate == "":
            pubDate, trigger, date_created = self.get_date_modified()
            pubDate = pubDate[:4]
        DOI = self.get_url()
        if dataset:
            citation = f"{author} ({pubDate}). {dataset}. {pub}. {DOI}"
        else:
            citation = f"{author} ({pubDate}). {pub}. {DOI}"
        return delete_null_values(citation)

    def get_variable_measured(self) -> Union[List[Dict], None]:
        # Mapping: schema:variable_measured = /spase:Parameters/spase:Name, Description, Units, ValidMin, ValidMax
        # Each object is:
        #   {"@type": schema:PropertyValue, "name": Name, "description": Description, "unitText": Units,
        #       "minValue": ValidMin, "maxValue": ValidMax}
        # Following schema:PropertyValue found at: https://github.com/ESIPFed/science-on-schema.org/blob/main/guides/Dataset.md#variables
        variable_measured = []
        paramDesc = ""
        unit = ""
        minVal = ""
        maxVal = ""
        for child in self.desiredRoot.iter(tag=etree.Element):
            if child.tag.endswith("Parameter"):
                targetChild = child
                for child in targetChild:
                    try:
                        if child.tag.endswith("Name"):
                            paramName = child.text
                        elif child.tag.endswith("Description"):
                            paramDesc = child.text
                        elif child.tag.endswith("Units"):
                            unit = child.text
                        elif child.tag.endswith("ValidMin"):
                            minVal = child.text
                        elif child.tag.endswith("ValidMax"):
                            maxVal = child.text
                    except AttributeError as err:
                        continue
                variable_measured.append({"@type": "PropertyValue", 
                                        "name": f"{paramName}",
                                        "description": f"{paramDesc}",
                                        "unitText": f"{unit}",
                                        "minValue": f"{minVal}",
                                        "maxValue": f"{maxVal}"})
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
        # Following schema:DataDownload found at: https://github.com/ESIPFed/science-on-schema.org/blob/main/guides/Dataset.md#accessing-data-through-a-service-endpoint
        distribution = []
        dataDownloads, potentialActions = get_accessURLs(self.metadata)
        for k, v in dataDownloads.items():
            distribution.append({"@type": "DataDownload",
                                "contentUrl": f"{k}",
                                "encodingFormat": f"{v[0]}"})
        for k, v in potentialActions.items():
            encoder = v[0]
            distribution.append({"@type": "DataDownload",
                                "contentUrl": f"{k}",
                                "encodingFormat": f"{encoder}"})
        return delete_null_values(distribution)

    def get_potential_action(self) -> Union[List[Dict], None]:
        # Mapping: schema:potentialAction = /spase:AccessInformation/spase:AccessURL/spase:URL
        # AND /spase:AccessInformation/spase:Format
        # Following schema:potentialAction found at: https://github.com/ESIPFed/science-on-schema.org/blob/main/guides/Dataset.md#accessing-data-through-a-service-endpoint
        potential_action = []
        dataDownloads, potentialActions = get_accessURLs(self.metadata)
        temp_covg = self.get_temporal_coverage()
        if temp_covg is not None:
            start, sep, end = temp_covg["temporalCoverage"].partition("/")
            if end == "":
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

            # loop thru all product keys if there are multiple
            for prodKey in prodKeys:
                prodKey = prodKey.replace("\"", "")
                # if link is a hapi link, provide the hapi interface web service to download data
                if "/hapi" in k:
                    potential_action.append({"@type": "SearchAction",
                                        "target": {"@type": "EntryPoint",
                                                    "contentType": f"{encoding}",
                                                    "urlTemplate": f"{k}/data?id={prodKey}&time.min=(start)&time.max=(end)",
                                                    "description": "Download dataset labeled by id based on the requested start and end dates",
                                                    "httpMethod": "GET"},
                                        "query-input": [
                                            {"@type": "PropertyValueSpecification",
                                            "valueName": "start",
                                            "description": f"A UTC ISO DateTime. {startSent}",
                                            "valueRequired": True,
                                            "valuePattern": f"{pattern}"},
                                            {"@type": "PropertyValueSpecification",
                                            "valueName": "end",
                                            "description": f"A UTC ISO DateTime. {endSent}",
                                            "valueRequired": True,
                                            "valuePattern": f"{pattern}"}
                                        ]
                    })
                # use GSFC CDAWeb portal to download CDF
                else:
                    potential_action.append({"@type": "SearchAction",
                                            "target": {"@type": "URL",
                                                        "encodingFormat": f"{encoding}",
                                                        "url": f"{k}",
                                                        "description": "Download dataset data in CSV or JSON form at this URL"}
                                            })
        return delete_null_values(potential_action)

    def get_date_created(self) -> Union[str, None]:
        # Mapping: schema:dateCreated = spase:ResourceHeader/spase:PublicationInfo/spase:PublicationDate
        # Using schema:DateTime as defined in: https://schema.org/DateTime
        #date_created = self.get_date_published

        release, revisions = get_dates(self.metadata)
        if revisions == []:
            date_created = str(release).replace(" ", "T")
        # find earliest date in revision history
        else:
            #print("RevisionHistory found!")
            date_created = str(revisions[0])
            if len(revisions) > 1:
                for i in range(1, len(revisions)):
                    if (revisions[i] < revisions[i-1]):
                        date_created = str(revisions[i])
            date_created = date_created.replace(" ", "T")
        return delete_null_values(date_created)

    def get_date_modified(self) -> Union[str, None]:
        # Mapping: schema:dateModified = spase:ResourceHeader/spase:ReleaseDate
        # Using schema:DateTime as defined in: https://schema.org/DateTime
        trigger = False
        release, revisions = get_dates(self.metadata)
        date_modified = str(release).replace(" ", "T")
        date_created = date_modified
        # confirm that ReleaseDate is the latest date in the record
        if revisions != []:
            #print("RevisionHistory found!")
            # find latest date in revision history
            date_created = str(revisions[0])
            if len(revisions) > 1:
                for i in range(1, len(revisions)):
                    if (revisions[i] > revisions[i-1]):
                        date_created = str(revisions[i])
            #print(date_created)
            #print(date_modified)
            if datetime.strptime(date_created, "%Y-%m-%d %H:%M:%S") != release:
                #raise ValueError("ReleaseDate is not the latest date in the record!")
                trigger = True
        return delete_null_values(date_modified), trigger, date_created

    def get_date_published(self) -> Union[str, None]:
        # Mapping: schema:datePublished = spase:ResourceHeader/spase:PublicationInfo/spase:PublicationDate
        # Using schema:DateTime as defined in: https://schema.org/DateTime        
        author, authorRole, pubDate, publisher, contributor, dataset, backups = get_authors(self.metadata)
        if pubDate == "":
            date_published = None
        else:
            date_published = pubDate.replace(" ", "T")
            date_published = date_published.replace("Z", "")
        return delete_null_values(date_published)

    def get_expires(self) -> None:
        expires = None
        return delete_null_values(expires)

    def get_temporal_coverage(self) -> Union[Dict, None]:
        # Mapping: schema:temporal_coverage = spase:TemporalDescription/spase:TimeSpan/*
        # Each object is:
        #   {"@context": schema.org, "@type": schema:Dataset, name: ResourceName, temporalCoverage: StartDate and StopDate|RelativeStopDate}
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
                temporal_coverage = {"temporalCoverage": f"{start}/{stop}"}
            else:
                temporal_coverage = {"temporalCoverage": f"{start}/.."}
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
        return delete_null_values(spatial_coverage)

    def get_creator(self) -> Union[List, None]:
        # Mapping: schema:creator = spase:ResourceHeader/spase:PublicationInfo/spase:Authors 
        # OR schema:creator = spase:ResourceHeader/spase:Contact/spase:PersonID
        # Each item is:
        #   {@type: Role, roleName: Contact Role, creator: {@type: Person, name: Author Name, givenName: First Name, familyName: Last Name}}
        # Using schema:Creator as defined in: https://github.com/ESIPFed/science-on-schema.org/blob/main/guides/Dataset.md#roles-of-people
        author, authorRole, pubDate, pub, contributor, dataset, backups = get_authors(self.metadata)
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
                path, sep, authorStr = person.partition("Person/")
                # get rid of extra quotations
                authorStr = authorStr.replace("'","")
                givenName, sep, familyName = authorStr.partition(".")
                # if name has initial(s)
                if ("." in familyName):
                    initial, sep, familyName = familyName.partition(".")
                    givenName = givenName + ' ' + initial + '.'
                authorStr = givenName + " " + familyName
                authorStr = authorStr.replace("\"", "")
                creator.append({"@type": "Role", 
                                "roleName": f"{authorRole[index]}",
                                "creator": {"@type": "Person",
                                            "name": f"{authorStr}",
                                            "givenName": f"{givenName}",
                                            "familyName": f"{familyName}"}
                                            })
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
                        grp = re.search(r'[\w]{1}\.$', person)
                        if grp is None:
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
                person = authorStr.replace("\"","")
                if authorRole == ["Author"]:
                    familyName, sep, givenName = person.partition(",")
                    # handle case when name is not formatted correctly
                    if givenName == "":
                        givenName, sep, familyName = familyName.partition(". ")
                        initial, sep, familyName = familyName.partition(" ")
                        givenName = givenName + ". " + initial[0] + "."
                    creator.append({"@type": "Role", 
                                    "roleName": f"{authorRole[0]}",
                                    "creator": {"@type": "Person",
                                                "name": f"{person}",
                                                "givenName": f"{givenName}",
                                                "familyName": f"{familyName}"}
                                                })
        return delete_null_values(creator)

    def get_contributor(self) -> Union[List, None]:
        # Mapping: schema:contributor = spase:ResourceHeader/spase:Contact/spase:PersonID
        # Each item is:
        #   {@type: Role, roleName: Contributor, contributor: {@type: Person, name: Author Name, givenName: First Name, familyName: Last Name}}
        # Using schema:Person as defined in: https://schema.org/Person
        author, authorRole, pubDate, pub, contributors, dataset, backups = get_authors(self.metadata)
        contributorStr = str(contributors).replace("[", "").replace("]","")
        contributor = []
        for person in contributors:
            path, sep, contributorStr = person.partition("Person/")
            # get rid of extra quotations
            contributorStr = contributorStr.replace("'","")
            givenName, sep, familyName = contributorStr.partition(".")
            # if name has initial(s)
            if ("." in familyName):
                initial, sep, familyName = familyName.partition(".")
                givenName = givenName + ' ' + initial + '.'
            contributorStr = givenName + " " + familyName
            contributorStr = contributorStr.replace("\"", "")
            contributor.append({"@type": "Role", 
                                "roleName": "Contributor",
                                "contributor": {"@type": "Person",
                                                "name": f"{contributorStr}",
                                                "givenName": f"{givenName}",
                                                "familyName": f"{familyName}"}
                                        })
        return delete_null_values(contributor)

    def get_provider(self) -> None:
        provider = None
        return delete_null_values(provider)

    def get_publisher(self) -> Union[Dict, None]:
        # Mapping: schema:publisher = spase:ResourceHeader/spase:Contacts
        # OR spase:ResourceHeader/spase:PublicationInfo/spase:PublishedBy
        # Each item is:
        #   {@type: Organization, name: PublishedBy OR Contact (if Role = Publisher)}
        # Using schema:Organization as defined in: https://github.com/ESIPFed/science-on-schema.org/blob/main/guides/Dataset.md#publisher-and-provider
        author, authorRole, pubDate, publisher, contributor, dataset, backups = get_authors(self.metadata)
        if publisher == "":
            publisher = None
            #RepoID = get_repoID(self.metadata)
            #(before, sep, publisher) = RepoID.partition("Repository/")
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
        # Using schema:MonetaryGrant as defined in: https://github.com/ESIPFed/science-on-schema.org/blob/main/guides/Dataset.md#funding
        funding = None
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
            funding = []
            i = 0
            for funder in agency:
                # if award number was found
                if award:
                    # funded by an agency
                    if ";" not in funder:
                        funding.append({"@type": "MonetaryGrant",
                                        "funder": {"@type": "Organization",
                                                    "name": f"{funder}"
                                        },
                                        "identifier": f"{award[i]}",
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

    def get_is_based_on(self) -> Union[List, None]:
        # Mapping: schema:isBasedOn = spase:ResourceHeader/spase:Association/spase:AssociationID
        is_based_on = []
        derivations = []
        is_related_to = []
        for child in self.desiredRoot.iter(tag=etree.Element):
            if child.tag.endswith("Association"):
                targetChild = child
                for child in targetChild:
                    if child.tag.endswith("AssociationID"):
                        A_ID = child.text
                    elif child.tag.endswith("AssociationType"):
                        type = child.text
                if type == "DerivedFrom":
                    derivations.append(A_ID)
            elif child.tag.endswith("PriorID"):
                is_related_to.append(child.text)
        if derivations == []:
            is_based_on = None
        else:
            is_based_on = [{"@type": "CreativeWork",
                                "isBasedOn": f"{derivations}"},
                            {"@type": "Product",
                                "isRelatedTo": f"{is_related_to}"}]
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
        publisher, and publication title. It then returns these items, with the author and
        author roles as lists and the rest as strings.

    :param metadata:    The SPASE metadata object as an XML tree.
    :type entry: etree.ElementTree object
    :returns: The highest priority authors found within the SPASE record as a list
                as well as a list of their roles, the publication date, publisher,
                and the title of the publication.
    :rtype: tuple
    """
    # local vars needed
    author = []
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
    # holds role values that are not considered for author var
    UnapprovedAuthors = ["MetadataContact", "ArchiveSpecialist",
                        "HostContact", "User"]

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
                                    elif child.text == "Contributor":
                                        contributor.append(PersonID)
                                    # backup publisher
                                    elif child.text == "Publisher":
                                        pub = child.text
                                    elif child.text not in UnapprovedAuthors:
                                        backups[PersonID] = child.text
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
    return author, authorRole, pubDate, pub, contributor, dataset, backups

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
                dataDownloads and potentialActions, depending on if they have a product key
                associated with them or not.
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
        # if URL has no prodKeys at all, add to the dataDownloads dictionary
        if not v:
            #print(i)
            dataDownloads[k] = [encoder[i]]
        # if URL has prodKeys, add to the potentialActions dictionary
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

def export_dates(R_IDs_Dates, R_Names_Dates, createdDates, modifiedDates, latestDates, DOIs_dates) -> None:
    # export records w incorrect dates to an excel file
    df_dates = pd.DataFrame({'ResourceID': R_IDs_Dates,
                            'ResourceName': R_Names_Dates,
                            'DOI': DOIs_dates,
                            'Date of Creation': createdDates,
                            'Current Release Date': modifiedDates,
                            'Most Recent Date': latestDates})
    file_name_dates = "C:/Users/zboquet/Documents/IncorrectDates.xlsx"
    df_dates.to_excel(file_name_dates,sheet_name='Dates')

def export_authors(R_IDs, R_Names, authors, roles, DOIs) -> None:
    # export records w/o desired authors to an excel file
    df_authors = pd.DataFrame({'ResourceID': R_IDs,
                    'ResourceName': R_Names,
                    'DOI': DOIs,
                    'Name': authors,
                    'Role': roles})
    #file_name_authors = "C:/Users/zboquet/Documents/noCreatorsDisplayData.xlsx"
    file_name_authors = "C:/Users/zboquet/Documents/noCreatorsNumericalData.xlsx"
    df_authors.to_excel(file_name_authors,sheet_name='Contacts')

def get_repoID(metadata: etree.ElementTree) -> str:
    root = metadata.getroot()
    repoID = ""
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

#TODO: add docstring
def main(folder, printFlag = True, desiredProperties = ["keywords", "citation", "identifier", "creator", "publisher",
                                                        "variable_measured", "temporal_coverage", "distribution",
                                                        "potential_action", "funding", "date_created", "date_modified",
                                                        "contributor", "date_published", "is_based_on"]) -> tuple:
    # list that holds SPASE records already checked
    searched = []

    SPASE_paths = []
    authors = []
    roles = []
    R_IDs = []
    R_Names = []
    R_IDs_Dates = []
    R_Names_Dates = []
    createdDates = []
    modifiedDates = []
    latestDates = []
    DOIs = []
    DOIs_dates =[]
    createdDates_Pub = []
    R_IDs_Pub = []
    RepoIDs = []

    # obtains all filepaths to all SPASE records found in given directory
    SPASE_paths = getPaths(folder, SPASE_paths)
    print("You entered " + folder)
    if len(SPASE_paths) == 0:
        print("No records found. Returning.")
    else:
        print("The number of records is " + str(len(SPASE_paths)))
        # iterate through all SPASE records
        # Note: starting at record 24 in ACE/EPAM folder, end of author string is formatted wrong with "and first last" instead of "and last, first" (SPASE issue)
        # Successfully passed for all 129 records in NumericalData/ACE/EPAM folder and all 187 in DisplayData
        # In DisplayData, records 130, 167-70 has authors formatted wrong
        # DisplayData: record 70 is ex w multiple contacts, ACE has ex's w multiple authors
        # ReleaseDate is not most recent at this dataset (causes dateModified to be incorrect): C:/Users/zboquet/NASA/DisplayData\SDO\AIA\SSC
        #   And some here too: C:/Users/zboquet/NASA/DisplayData\STEREO-A\SECCHI\, C:/Users/zboquet/NASA/DisplayData\STEREO-B\SECCHI
        #                       C:/Users/zboquet/NASA/NumericalData\Cluster-Rumba\WBD\BM2
        for r, record in enumerate(SPASE_paths):
            if record not in searched:
                # scrape metadata for each record
                statusMessage = f"Extracting metadata from record {r+1}"
                statusMessage += f" of {len(SPASE_paths)}"
                print(statusMessage)
                print(record)
                testSpase = SPASE(record)
                ResourceName = testSpase.get_name()
                ResourceID = testSpase.get_id()
                repoID = get_repoID(testSpase.metadata)

                #print(testSpase.get_is_accessible_for_free())
                keywords = testSpase.get_keywords()
                citation = testSpase.get_citation()
                identifier = testSpase.get_identifier()
                creator = testSpase.get_creator()
                publisher = testSpase.get_publisher()
                contributor = testSpase.get_contributor()
                variable_measured = testSpase.get_variable_measured()
                temporal_coverage = testSpase.get_temporal_coverage()
                distribution = testSpase.get_distribution()
                potential_action = testSpase.get_potential_action()
                funding = testSpase.get_funding()
                date_created = testSpase.get_date_created()
                date_modified, trigger, mostRecentDate = testSpase.get_date_modified()
                date_published = testSpase.get_date_published()
                is_based_on = testSpase.get_is_based_on()

                if printFlag:
                    for property in desiredProperties:
                        if property == "keywords":
                            if keywords is None:
                                print("No keywords found")
                            else:
                                print(f"Keywords: {keywords}")
                        elif property == "citation":
                            print(f"Citation: {citation}")
                        elif property == "identifier":
                            print(f"Identifier: {identifier}")
                        elif property == "creator":
                            if creator is not None:
                                print("Creator(s): ")
                                for each in creator:
                                    print(each)
                                #print("")
                            else:
                                print("No creators were found according to the priority rules. Exporting backups for further analysis.")
                                # append ResourceID, ResourceName, DOI, and authors with their roles to the export list
                                author, authorRole, pubDate, pub, contrib, dataset, backups = get_authors(testSpase.metadata)
                                R_IDs.append(ResourceID)
                                R_Names.append(ResourceName)
                                DOIs.append(identifier)
                                for k,v in backups.items():
                                    authors.append(k)
                                    roles.append(v)
                                    DOIs.append("")
                                    R_IDs.append("")
                                    R_Names.append("")
                                R_IDs = R_IDs[:len(R_IDs)-1]
                                R_Names = R_Names[:len(R_Names)-1]
                                DOIs = DOIs[:len(DOIs)-1]
                        elif property == "date_created":
                            print(f"Date Created: {date_created}")
                        elif property == "date_modified":
                            if trigger:
                                print("This record has incorrect dates. Exporting to spreadsheet for further analysis.")
                                # create a list of the records who have incorrect dates for exporting to excel
                                R_IDs_Dates.append(ResourceID)
                                R_Names_Dates.append(ResourceName)
                                createdDates.append(date_created)
                                modifiedDates.append(date_modified)
                                latestDates.append(mostRecentDate)
                                DOIs_dates.append(identifier)
                            else:
                                print(f"Date Modified: {date_modified}")
                                #print("")
                        elif property == "date_published":
                            if date_published is not None:
                                print(f"Date Published: {date_published}")
                            else:
                                print("No publication date was found.")
                        elif property == "publisher":
                            if publisher is not None:
                                print(f"Publisher: {publisher}") 
                            else:
                                print("No publisher was found. Exporting to spreadsheet for further analysis.")
                                R_IDs_Pub.append(ResourceID)
                                RepoIDs.append(repoID)
                                createdDates_Pub.append(date_created)
                        elif property == "contributor":
                            # pos 1161-2 in NumericalData
                            if contributor is not None:
                                print("Contributor(s): ")
                                for person in contributor:
                                    print(person)
                            else:
                                print("No contributors found.")
                        elif property == "distribution" or property == "potential_action":
                            print("AccessURLs: ")
                            if property == "distribution":
                                for url in distribution:
                                    print(url)
                            else:
                                if potential_action is not None:
                                    for download_links in potential_action:
                                        print(download_links)
                        elif property == "temporal_coverage":
                            if temporal_coverage is not None:
                                print(f"Temporal Coverage: {temporal_coverage}")
                            else:
                                print("No start/stop times were found.")
                        elif property == "funding":
                            if funding is not None:
                                print("Funding: ")
                                for funder in funding:
                                    print(funder)
                            else:
                                print("No funding info was found.")
                        elif property == "is_based_on":
                            # only 16 in DisplayData have this, none in ACE/EPAM, 6 in NumericalData
                            if is_based_on is not None:
                                print("AssociationIDs: ")
                                for each in is_based_on:
                                    print(each)
                            else:
                                print("No AssociationID was found.")
                        elif property == "variable_measured":
                            if variable_measured is not None:
                                print("Parameters: ")
                                for variable in variable_measured:
                                    print(variable)
                print("Metadata extraction completed")
                print()

                # add record to searched
                searched.append(record)
    return R_IDs, R_Names, R_IDs_Dates, R_Names_Dates, authors, roles, createdDates, modifiedDates, latestDates, DOIs, DOIs_dates, createdDates_Pub, R_IDs_Pub, RepoIDs

# test directories
#folder = "C:/Users/zboquet/NASA/DisplayData"
folder = "C:/Users/zboquet/NASA/NumericalData"
R_IDs, R_Names, R_IDs_Dates, R_Names_Dates, authors, roles, createdDates, modifiedDates, latestDates, DOIs, DOIs_dates, createdDates_Pub, R_IDs_Pub, RepoIDs = main(folder, True, ["publisher"])
#export_authors(R_IDs, R_Names, authors, roles, DOIs)

df_pub = pd.DataFrame({'ResourceID': R_IDs_Pub,
                    'RepositoryID': RepoIDs,
                    'Date of Creation': createdDates_Pub})
#file_name_pub = "C:/Users/zboquet/Documents/noPublishersDisplayData.xlsx"
file_name_pub = "C:/Users/zboquet/Documents/noPublishersNumericalData.xlsx"
df_pub.to_excel(file_name_pub)

#folder = "C:/Users/zboquet/NASA/NumericalData/ACE/EPAM"
#folder = "C:/Users/zboquet/NASA/NumericalData/Cassini/MAG"
#folder = "C:/Users/zboquet/NASA/NumericalData/MMS/4/HotPlasmaCompositionAnalyzer/Burst/Level2/Ion"
# start at list item 132 if want to skip EPAM folder
#folder = "C:/Users/zboquet/NASA/NumericalData/ACE"
# start at list item 163 if want to skip ACE folder
#folder = "C:/Users/zboquet/NASA/NumericalData"
#R_IDs2, R_Names2, R_IDs_Dates2, R_Names_Dates2, authors2, roles2, createdDates2, modifiedDates2, latestDates2, DOIs2, DOIs_dates2, createdDates_Pub2, R_IDs_Pub2, RepoIDs2 = main(folder, False, True)
#export_authors(R_IDs2, R_Names2, authors2, roles2, DOIs2)

# for exporting the dates into one spreadsheet
#R_IDs += R_IDs2
#R_Names += R_Names2
#R_IDs_Dates += R_IDs_Dates2
#R_Names_Dates += R_Names_Dates2
#authors += authors2
#roles += roles2
#createdDates += createdDates2
#modifiedDates += modifiedDates2
#latestDates += latestDates2
#DOIs += DOIs2
#DOIs_dates += DOIs_dates2
#export_dates(R_IDs_Dates, R_Names_Dates, createdDates, modifiedDates, latestDates, DOIs_dates)