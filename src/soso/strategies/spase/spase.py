"""The SPASE strategy module."""

import atexit
import json
import re
import os
import tempfile
import importlib.resources
from datetime import datetime, timedelta
from pathlib import Path
from typing import Union, List, Dict
import requests
from lxml import etree
from soso.interface import StrategyInterface
from soso.utilities import delete_null_values

# pylint: disable=duplicate-code
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=too-many-nested-blocks
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=no-member
# pylint: disable=pointless-string-statement
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=consider-using-f-string
# pylint: disable=consider-using-dict-items
# pylint: disable=consider-iterating-dictionary
# pylint: disable=no-else-return
# pylint: disable=consider-using-with


# create temp file which holds problematic records encountered during script
# Create a named temporary file which is deleted via garbage collection
temp_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8")
temp_file_path = temp_file.name
# print("Temp file exists?: " + str(os.path.exists(temp_file_path)) + ':' + temp_file_path)


def cleanup_temp_file():
    """Cleanup the temporary file on exit."""
    if not temp_file.closed:
        temp_file.close()


atexit.register(cleanup_temp_file)


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

        :ref:`A shared conversion script <spase_HowToConvert>` is available for
        this standard. It is designed for repositories that supplement SPASE
        metadata with shared infrastructure, using the ancillary information
        to generate a richer SOSO record.
    """

    def __init__(self, file: str, **kwargs: dict):
        """Initialize the strategy."""
        file = str(file)  # incase file is a Path object
        if not file.endswith(".xml"):  # file should be XML
            raise ValueError(file + " must be an XML file.")
        super().__init__(metadata=etree.parse(file))
        self.file = file
        self.schema_version = get_schema_version(self.metadata)
        self.kwargs = kwargs
        self.root = self.metadata.getroot()
        namespace = ""
        for ns in list(self.root.nsmap.values()):
            if "spase-group" in ns:
                namespace = ns
        self.namespaces = {"spase": namespace}
        # find element in tree to iterate over
        for elt in self.root.iter(tag=etree.Element):
            if (
                elt.tag.endswith("NumericalData")
                or elt.tag.endswith("DisplayData")
                or elt.tag.endswith("Observatory")
                or elt.tag.endswith("Instrument")
                or elt.tag.endswith("Collection")
            ):
                self.desired_root = elt
        # if want to see entire xml file as a string
        # print(etree.tostring(self.desired_root, pretty_print = True).decode(), end=' ')

    def get_id(self) -> str:
        # Mapping: schema:identifier = spase:ResourceHeader/spase:DOI
        #   OR spase-metadata.org landing page for the SPASE record
        url = self.get_url()
        if url:
            spase_id = url
        else:
            spase_id = None

        return delete_null_values(spase_id)

    def get_name(self) -> str:
        # Mapping: schema:name = spase:ResourceHeader/spase:ResourceName
        desired_tag = self.desired_root.tag.split("}")
        spase_location = (
            ".//spase:" + f"{desired_tag[1]}/spase:ResourceHeader/spase:ResourceName"
        )
        name = self.metadata.findtext(
            spase_location,
            namespaces=self.namespaces,
        )
        return delete_null_values(name)

    def get_description(self) -> str:
        # Mapping: schema:description = spase:ResourceHeader/spase:Description
        desired_tag = self.desired_root.tag.split("}")
        spase_location = (
            ".//spase:" + f"{desired_tag[1]}/spase:ResourceHeader/spase:Description"
        )
        description = self.metadata.findtext(
            spase_location,
            namespaces=self.namespaces,
        )
        return delete_null_values(description)

    def get_url(self) -> str:
        # Mapping: schema:url = spase:ResourceHeader/spase:DOI
        #   (or https://spase-metadata.org landing page, if no DOI)
        desired_tag = self.desired_root.tag.split("}")
        spase_location = (
            ".//spase:" + f"{desired_tag[1]}/spase:ResourceHeader/spase:DOI"
        )
        url = self.metadata.findtext(
            spase_location,
            namespaces=self.namespaces,
        )
        if delete_null_values(url) is None:
            resource_id = get_resource_id(self.metadata, self.namespaces)
            if resource_id:
                url = resource_id.replace("spase://", "https://spase-metadata.org/")
        return delete_null_values(url)

    def get_same_as(self) -> Union[List, None]:
        # Mapping: schema:sameAs = spase:ResourceHeader/spase:PriorID
        same_as = []

        # traverse xml to extract needed info
        for child in self.desired_root.iter(tag=etree.Element):
            if child.tag.endswith("PriorID"):
                same_as.append(child.text)
        if not same_as:
            same_as = None
        elif len(same_as) == 1:
            same_as = same_as[0]
        return delete_null_values(same_as)

    def get_version(self) -> None:
        version = None
        return delete_null_values(version)

    # commented out partial code that was put on hold due to licenses being added to SPASE soon
    def get_is_accessible_for_free(self) -> None:
        # free = None
        # """schema:description: spase:AccessInformation/AccessRights"""
        is_accessible_for_free = None
        # local vars needed
        # access = ""

        # iterate thru to find AccessInfo
        # for child in self.desired_root:
        #    if access == "Open":
        #        break
        #    if child.tag.endswith("AccessInformation"):
        #        target_child = child
        # iterate thru to find AccessRights
        #        for child in target_child:
        #            if child.tag.endswith("AccessRights"):
        #                access = child.text
        # if access == "Open":
        #    is_accessible_for_free = True
        # else:
        #    is_accessible_for_free = False
        return delete_null_values(is_accessible_for_free)

    def get_keywords(self) -> Union[List, None]:
        # Mapping: schema:keywords = spase:Keyword
        keywords = []

        # traverse xml to extract needed info
        for child in self.desired_root.iter(tag=etree.Element):
            if child.tag.endswith("Keyword"):
                keywords.append(child.text)
        if not keywords:
            keywords = None
        return delete_null_values(keywords)

    def get_identifier(self) -> Union[Dict, List[Dict], None]:
        # Mapping: schema:identifier = spase:ResourceHeader/spase:DOI
        #   (or https://spase-metadata.org landing page, if no DOI)
        # Each item is: {@id: URL, @type: schema:PropertyValue,
        #   propertyID: URI for identifier scheme, value: identifier value, url: URL}
        # Uses identifier scheme URI, provided at: https://schema.org/identifier
        #  OR schema:PropertyValue, provided at: https://schema.org/PropertyValue
        url = self.get_url()
        spase_id = get_resource_id(self.metadata, self.namespaces)
        if url:
            # if SPASE record has a DOI
            if "doi" in url:
                landing_page_url = spase_id.replace(
                    "spase://", "https://spase-metadata.org/"
                )
                temp = url.split("/")
                value = "doi:" + "/".join(temp[3:])
                identifier = {
                    "@list": [
                        {
                            "@type": "PropertyValue",
                            "propertyID": "https://registry.identifiers.org/registry/doi",
                            "value": value,
                            "url": url,
                            "name": value.replace("doi:", "DOI: "),
                        },
                        {
                            "@type": "PropertyValue",
                            "propertyID": "SPASE",
                            "value": spase_id,
                            "url": landing_page_url,
                        },
                    ]
                }
            # if SPASE record only has landing page instead
            else:
                identifier = {
                    "@type": "PropertyValue",
                    "propertyID": "SPASE",
                    "url": url,
                    "value": spase_id,
                }
        else:
            identifier = None
        return delete_null_values(identifier)

    def get_citation(self) -> Union[List[Dict], None]:
        # Mapping: schema:citation = spase:ResourceHeader/spase:InformationURL
        citation = []
        information_url = get_information_url(self.metadata)
        if information_url:
            for each in information_url:
                # most basic citation item
                entry = {
                    "@id": each["url"],
                    "@type": "CreativeWork",
                    "url": each["url"],
                    "identifier": each["url"],
                }
                if "name" in each.keys():
                    entry["name"] = each["name"]
                if "description" in each.keys():
                    entry["description"] = each["description"]
                citation.append(entry)
        else:
            citation = None
        return delete_null_values(citation)

    def get_variable_measured(self) -> Union[List[Dict], None]:
        # Mapping: schema:variable_measured = spase:Parameters/spase:Name,
        #   Description, Units, ParameterKey
        # Each object is:
        #   {"@type": schema:PropertyValue, "name": Name,
        #   "description": Description, "unitText": Units, "alternateName": ParameterKey}
        # Following schema:PropertyValue found at: https://schema.org/PropertyValue
        variable_measured = []
        # minVal = ""
        # maxVal = ""
        param_desc = ""
        param_name = ""
        units_found = []
        key = ""
        i = 0

        # traverse xml to extract needed info
        for child in self.desired_root.iter(tag=etree.Element):
            if child.tag.endswith("Parameter"):
                target_child = child
                for child in target_child:
                    units_found.append("")
                    try:
                        if child.tag.endswith("Name"):
                            param_name = child.text
                        elif child.tag.endswith("Description"):
                            substring = child.text.split("\n", 1)
                            param_desc = substring[0]
                        elif child.tag.endswith("Units"):
                            unit = child.text
                            units_found[i] = unit
                        elif child.tag.endswith("ParameterKey"):
                            key = child.text
                        # elif child.tag.endswith("ValidMin"):
                        # minVal = child.text
                        # elif child.tag.endswith("ValidMax"):
                        # maxVal = child.text
                    except AttributeError:
                        continue
                # most basic entry for variable measured
                entry = {"@type": "PropertyValue", "name": param_name}
                # "minValue": f"{minVal}",
                # "maxValue": f"{maxVal}"})
                if param_desc:
                    entry["description"] = param_desc
                if units_found[i]:
                    entry["unitText"] = units_found[i]
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

    def get_subject_of(self, *moreLicenseInfo) -> Union[Dict, None]:
        # Mapping: schema:subjectOf = {http://www.w3.org/2001/XMLSchema-instance}MetadataRights
        #   AND spase:ResourceHeader/spase:ReleaseDate
        # Following type:DataDownload found at: https://schema.org/DataDownload
        date_modified = self.get_date_modified()
        metadata_license = get_metadata_license(self.metadata)
        content_url = self.get_id()
        doi = False
        if "doi" in content_url:
            doi = True
            resource_id = get_resource_id(self.metadata, self.namespaces)
            content_url = resource_id.replace("spase://", "https://spase-metadata.org/")
        # small lookup table for commonly used licenses in SPASE
        #   (CC0 for NASA, CC-BY-NC-3.0 for ESA, etc)
        common_licenses = [
            {
                "fullName": "Creative Commons Zero v1.0 Universal",
                "identifier": "CC0-1.0",
                "url": "https://spdx.org/licenses/CC0-1.0.html",
            },
            {
                "fullName": "Creative Commons Attribution Non Commercial 3.0 Unported",
                "identifier": "CC-BY-NC-3.0",
                "url": "https://spdx.org/licenses/CC-BY-NC-3.0.html",
            },
            {
                "fullName": "Creative Commons Attribution 1.0 Generic",
                "identifier": "CC-BY-1.0",
                "url": "https://spdx.org/licenses/CC-BY-1.0.html",
            },
        ]
        # add additional licensing info provided by the user to the lookup table
        if moreLicenseInfo:
            if "https://spdx.org/licenses/" in moreLicenseInfo[2]:
                addition = {
                    "fullName": moreLicenseInfo[0],
                    "identifier": moreLicenseInfo[1],
                    "url": moreLicenseInfo[2],
                }
                common_licenses.append(addition)
            else:
                raise ValueError(
                    "Improper URL provided: Ensure that the URL"
                    "is pulled from the SPDX repo at"
                    "https://github.com/spdx/license-list-data/tree/main"
                    "and that it contains the text 'https://spdx.org/licenses/'"
                )

        if content_url:
            # basic format for item
            entry = {
                "@type": "DataDownload",
                "name": "SPASE metadata for dataset",
                "description": "The SPASE metadata describing the indicated dataset.",
                "encodingFormat": "application/xml",
                "contentUrl": content_url,
                "identifier": content_url,
            }
            # if spase-metadata.org landing page not used as top-level @id, include here as @id
            if doi:
                entry["@id"] = content_url
            if metadata_license:
                # find URL associated w license found in top-level SPASE line
                license_url = []
                for meta_license in metadata_license:
                    for each in common_licenses:
                        if each["fullName"] == meta_license:
                            license_url.append(each["url"])
                # if license is not in lookup table
                if not license_url:
                    # find license info from SPDX data file at
                    #   https://github.com/spdx/license-list-data/tree/main
                    #   and add to common_licenses dictionary OR provide the
                    #   fullName, identifier, and URL (in that order) as arguments
                    #   to the conversion function. Then rerun script for those that failed.
                    pass
                else:
                    entry["license"] = license_url

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
        #   {"@type": schema:DataDownload, "content_url": URL, "encodingFormat": Format}
        # Following schema:DataDownload found at: https://schema.org/DataDownload
        distribution = []
        data_downloads, _ = get_access_urls(self.metadata)
        for k, v in data_downloads.items():
            entry = {"@type": "DataDownload", "contentUrl": k, "encodingFormat": v[0]}
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
        potential_action_list = []
        start_sent = ""
        end_sent = ""
        _, potential_actions = get_access_urls(self.metadata)
        temp_covg = self.get_temporal_coverage()
        if temp_covg is not None:
            # obtain trial start and stop times for use in entry description
            start_sent, end_sent = make_trial_start_and_stop(temp_covg)

        # potential_actions[url] = [encoding, {"keys": [], "name": ""}]

        # loop thru all AccessURLs
        for k, v in potential_actions.items():
            prod_keys = v[1]["keys"]
            name = v[1]["name"]
            encoding = v[0]
            # regex pattern for DateTime objects
            pattern = (
                "(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-"
                "(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9])"
                ":([0-5][0-9])(.[0-9]+)?(Z)?"
            )
            multiple = False

            # most basic format for a potentialAction item
            entry = {
                "@type": "SearchAction",
                "target": {
                    "@type": "EntryPoint",
                    "contentType": encoding,
                    "url": k,
                    "description": f"Download dataset data as {encoding} file at this URL",
                },
            }
            # if link has no prod_key
            if prod_keys == []:
                # if not an ftp link, include url as @id
                if "ftp" not in k:
                    entry["target"]["@id"] = k
                    entry["target"]["identifier"] = k
                # if name available, add it
                if name:
                    entry["target"]["name"] = name
                potential_action_list.append(entry)
            else:
                # if name available, add it
                if name:
                    entry["target"]["name"] = name
                # find if multiple product keys
                if len(prod_keys) > 1:
                    multiple = True
                # let user know of product key names in description
                entry["target"][
                    "description"
                ] += f" using these product key(s): {str(prod_keys)}"
                # if link is a hapi link, provide the hapi interface
                #   web service to download data
                if "/hapi" in k:
                    # additions needed for each hapi link
                    query_format = [
                        {
                            "@type": "PropertyValueSpecification",
                            "valueName": "start",
                            "description": f"A UTC ISO DateTime. {start_sent}",
                            "valueRequired": False,
                            "valuePattern": f"{pattern}",
                        },
                        {
                            "@type": "PropertyValueSpecification",
                            "valueName": "end",
                            "description": f"A UTC ISO DateTime. {end_sent}",
                            "valueRequired": False,
                            "valuePattern": f"{pattern}",
                        },
                    ]
                    if "url" in entry["target"].keys():
                        entry["target"].pop("url")
                    # if multiple product keys, keep track of all of them
                    if multiple:
                        entry["target"]["urlTemplate"] = []
                        for prod_key in prod_keys:
                            prod_key = prod_key.replace('"', "")
                            entry["target"]["urlTemplate"].append(
                                f"{k}/data?id={prod_key}&time.min={{start}}&time.max={{end}}"
                            )
                    else:
                        prod_keys[0] = prod_keys[0].replace('"', "")
                        entry["target"][
                            "urlTemplate"
                        ] = f"{k}/data?id={prod_keys[0]}&time.min={{start}}&time.max={{end}}"
                    entry["target"]["description"] = (
                        "Download dataset labeled by id in CSV format based on "
                        "the requested start and end dates"
                    )
                    entry["target"]["httpMethod"] = "GET"
                    entry["query-input"] = query_format
                # if not ftp link, include url as @id
                if "ftp" not in k:
                    entry["target"]["@id"] = k
                    entry["target"]["identifier"] = k
                potential_action_list.append(entry)
        if len(potential_action_list) != 0:
            potential_action = potential_action_list
        else:
            potential_action = None
        return delete_null_values(potential_action)

    def get_date_created(self) -> Union[str, None]:
        # Mapping: schema:dateCreated = spase:ResourceHeader/
        #   spase:PublicationInfo/spase:PublicationDate
        # OR spase:ResourceHeader/spase:RevisionHistory/spase:ReleaseDate
        # Using schema:DateTime as defined in: https://schema.org/DateTime
        date_created = self.get_date_published()

        # release, revisions = get_dates(self.metadata)
        # if revisions == []:
        # date_created = str(release).replace(" ", "T")
        # find earliest date in revision history
        # else:
        # print("RevisionHistory found!")
        # date_created = str(revisions[0])
        # if len(revisions) > 1:
        # for i in range(1, len(revisions)):
        # if (revisions[i] < revisions[i-1]):
        # date_created = str(revisions[i])
        # date_created = date_created.replace(" ", "T")
        return delete_null_values(date_created)

    def get_date_modified(self) -> Union[str, None]:
        # Mapping: schema:dateModified = spase:ResourceHeader/spase:ReleaseDate
        # Using schema:DateTime as defined in: https://schema.org/DateTime
        # trigger = False
        release, _ = get_dates(self.metadata)
        date_modified = str(release).replace(" ", "T")
        # date_created = date_modified
        # confirm that ReleaseDate is the latest date in the record
        # if revisions != []:
        # print("RevisionHistory found!")
        # find latest date in revision history
        # date_created = str(revisions[0])
        # if len(revisions) > 1:
        # for i in range(1, len(revisions)):
        # if (revisions[i] > revisions[i-1]):
        # date_created = str(revisions[i])
        # print(date_created)
        # print(date_modified)
        # raise Error if releaseDate is not the latest in RevisionHistory
        # if datetime.strptime(date_created, "%Y-%m-%d %H:%M:%S") != release:
        # raise ValueError("ReleaseDate is not the latest date in the record!")
        # trigger = True
        return delete_null_values(date_modified)

    def get_date_published(self) -> Union[str, None]:
        # Mapping: schema:datePublished = spase:ResourceHeader/
        #   spase:PublicationInfo/spase:PublicationDate
        # OR spase:ResourceHeader/spase:RevisionHistory/spase:ReleaseDate
        # Using schema:DateTime as defined in: https://schema.org/DateTime
        (_, _, pub_date, _, _, _, _, _) = get_authors(self.metadata)
        date_published = None
        _, revisions = get_dates(self.metadata)
        if pub_date == "":
            if revisions:
                # find earliest date in revision history
                date_published = str(revisions[0])
                if len(revisions) > 1:
                    for i in range(1, len(revisions)):
                        if revisions[i] < revisions[i - 1]:
                            date_published = str(revisions[i])
                date_published = date_published.replace(" ", "T")
                date_published = date_published.replace("Z", "")
        else:
            date_published = pub_date.replace(" ", "T")
            date_published = date_published.replace("Z", "")
        return delete_null_values(date_published)

    def get_expires(self) -> None:
        expires = None
        return delete_null_values(expires)

    def get_temporal_coverage(self) -> Union[str, Dict, None]:
        # Mapping: schema:temporal_coverage = spase:TemporalDescription/spase:TimeSpan/*
        # Each object is:
        #   {temporalCoverage: StartDate and StopDate|RelativeStopDate}
        # Result is either schema:Text or schema:DateTime,
        #   found at https://schema.org/Text and https://schema.org/DateTime
        # Using format as defined in: 'https://github.com/ESIPFed/science-on-schema
        #   .org/blob/main/guides/Dataset.md#temporal-coverage'
        desired_tag = self.desired_root.tag.split("}")
        spase_location = (
            ".//spase:"
            + f"{desired_tag[1]}/spase:TemporalDescription/spase:TimeSpan/spase:StartDate"
        )
        start = self.metadata.findtext(
            spase_location,
            namespaces=self.namespaces,
        )
        spase_location = (
            ".//spase:"
            + f"{desired_tag[1]}/spase:TemporalDescription/spase:TimeSpan/spase:StopDate"
        )
        stop = self.metadata.findtext(
            spase_location,
            namespaces=self.namespaces,
        )

        if start:
            if stop:
                # temporal_coverage = {
                # "@type": "DateTime",
                # "temporalCoverage": f"{start.strip()}/{stop.strip()}",
                # }
                temporal_coverage = f"{start.strip()}/{stop.strip()}"
            # in case there is a RelativeStopDate
            else:
                temporal_coverage = f"{start}/.."
        else:
            temporal_coverage = None
        return delete_null_values(temporal_coverage)

    def get_spatial_coverage(self) -> Union[List[Dict], None]:
        # Mapping: schema:spatial_coverage = list of spase:NumericalData/spase:ObservedRegion
        spatial_coverage = []
        desired_tag = self.desired_root.tag.split("}")
        spase_location = ".//spase:" + f"{desired_tag[1]}/spase:ObservedRegion"
        all_regions = self.metadata.findall(spase_location, namespaces=self.namespaces)
        for item in all_regions:
            # Split string on '.'
            pretty_name = item.text.replace(".", " ")

            # most basic entry for spatialCoverage
            entry = {
                "@type": "Place",
                "keywords": {
                    "@type": "DefinedTerm",
                    "inDefinedTermSet": {
                        "@id": "https://spase-group.org/data/"
                        + "model/spase-latest/spase-latest_xsd.htm#Region"
                    },
                    "termCode": item.text,
                },
                "name": pretty_name,
            }

            # if this is the first item added, add additional info for DefinedTermSet
            if all_regions.index(item) == 0:
                entry["keywords"]["inDefinedTermSet"]["@type"] = "DefinedTermSet"
                entry["keywords"]["inDefinedTermSet"]["name"] = "SPASE Region"
                entry["keywords"]["inDefinedTermSet"]["url"] = (
                    "https://spase-group.org/data/model/spase-latest"
                    "/spase-latest_xsd.htm#Region"
                )
            spatial_coverage.append(entry)

        if len(spatial_coverage) == 0:
            spatial_coverage = None
        return delete_null_values(spatial_coverage)

    def get_creator(self) -> Union[List[Dict], None]:
        # Mapping: schema:creator = spase:ResourceHeader/spase:PublicationInfo/spase:Authors
        # OR schema:creator = spase:ResourceHeader/spase:Contact/spase:PersonID
        # Each item is:
        #   {@type: Role, roleName: Contact Role, creator:
        #   {@type: Person, name: Author Name, givenName:
        #   First Name, familyName: Last Name}}
        #   plus the additional properties if available: affiliation and identifier (ORCiD ID),
        #       which are pulled from SMWG Person SPASE records
        # Using schema:Creator as defined in: https://schema.org/creator
        creator = []
        multiple = False
        matching_contact = False
        given_name = ""
        family_name = ""
        home_dir = str(Path.home()).replace("\\", "/")
        (
            author,
            author_role,
            *_,
            contacts_list,
        ) = get_authors(self.metadata, self.file.replace(f"{home_dir}/", ""))
        author_str = str(author).replace("[", "").replace("]", "")
        if author:
            # if creators were found in Contact/PersonID
            if "Person/" in author_str:
                # if multiple found, split them and iterate thru one by one
                if "'," in author_str:
                    multiple = True
                for person in author:
                    if multiple:
                        # keep track of position so roles will match
                        index = author.index(person)
                    else:
                        index = 0
                    # split text from Contact into properly formatted name fields
                    author_str, given_name, family_name = name_splitter(person)
                    # get additional info (if any)
                    # uncomment if making snapshot and also add '**kwargs: dict' as parameter
                    # if not kwargs:
                    orcid_id, affiliation, ror = get_orcid_and_affiliation(
                        person, self.file
                    )
                    """else:
                        orcid_id = ""
                        ror = ""
                        affiliation = """
                    # create the dictionary entry for that person and append to list
                    creator_entry = person_format(
                        "creator",
                        author_role[index],
                        author_str,
                        given_name,
                        family_name,
                        affiliation,
                        orcid_id,
                        ror,
                    )
                    creator.append(creator_entry)
            # if creators were found in PublicationInfo/Authors
            else:
                # if there are multiple authors
                if len(author) > 1:
                    # get rid of extra quotations
                    for num, each in enumerate(author):
                        if "'" in each:
                            author[num] = each.replace("'", "")
                    # iterate over each person in author string
                    for person in author:
                        matching_contact = False
                        index = author.index(person)
                        family_name, _, given_name = person.partition(", ")
                        # find matching person in contacts, if any, to retrieve
                        #   affiliation and ORCiD
                        for key, val in contacts_list.items():
                            if not matching_contact:
                                if person == val:
                                    matching_contact = True
                                    # uncomment if making snapshot
                                    # if not kwargs:
                                    orcid_id, affiliation, ror = (
                                        get_orcid_and_affiliation(key, self.file)
                                    )
                                    """else:
                                        orcid_id = ""
                                        ror = ""
                                        affiliation = """
                                    creator_entry = person_format(
                                        "creator",
                                        author_role[index],
                                        person,
                                        given_name,
                                        family_name,
                                        affiliation,
                                        orcid_id,
                                        ror,
                                    )
                        if not matching_contact:
                            creator_entry = person_format(
                                "creator",
                                author_role[index],
                                person,
                                given_name,
                                family_name,
                            )
                        creator.append(creator_entry)
                # if there is only one author listed
                else:
                    # get rid of extra quotations
                    person = author_str.replace('"', "")
                    person = author_str.replace("'", "")
                    # determine if creator is a consortium
                    with open(
                        importlib.resources.files("soso.strategies.spase").joinpath(
                            "spase-ignoreCreatorSplit.txt"
                        ),
                        "r",
                        encoding="utf-8",
                    ) as f:
                        do_not_split = f.read()
                    if ", " in person:
                        # if file is not in list of ones to not have their creators split
                        if self.file.replace(home_dir, "") not in do_not_split:
                            family_name, _, given_name = person.partition(", ")
                            # find matching person in contacts, if any, to get affiliation and ORCiD
                            for key, val in contacts_list.items():
                                if not matching_contact:
                                    if person == val:
                                        matching_contact = True
                                        # uncomment if making snapshot
                                        # if not kwargs:
                                        orcid_id, affiliation, ror = (
                                            get_orcid_and_affiliation(key, self.file)
                                        )
                                        """else:
                                            orcid_id = ""
                                            ror = ""
                                            affiliation = """
                                        creator_entry = person_format(
                                            "creator",
                                            author_role[0],
                                            person,
                                            given_name,
                                            family_name,
                                            affiliation,
                                            orcid_id,
                                            ror,
                                        )
                        if not matching_contact:
                            creator_entry = person_format(
                                "creator",
                                author_role[0],
                                person,
                                given_name,
                                family_name,
                            )
                        creator.append(creator_entry)
                    # no comma = organization = no givenName and familyName
                    else:
                        creator_entry = person_format(
                            "creator", author_role[0], person, "", ""
                        )
                        creator.append(creator_entry)
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
        #   {@type: Role, roleName: Contributor or curator role,
        #   contributor: {@type: Person, name: Author Name,
        #   givenName: First Name, familyName: Last Name}}
        #   plus the additional properties if available: affiliation and identifier (ORCiD ID),
        #       which are pulled from SMWG Person SPASE records
        # Using schema:Person as defined in: https://schema.org/Person
        (*_, contributors, _, backups, contacts_list) = get_authors(self.metadata)
        contributor = []
        first_contrib = True
        # holds role values that are not initially considered for contributor var
        curator_roles = [
            "HostContact",
            "GeneralContact",
            "DataProducer",
            "MetadataContact",
            "TechnicalContact",
        ]

        # Step 1: check for ppl w author roles that were not found in PubInfo
        for key, val in contacts_list.items():
            # used so that DefinedTermSet info not repeated in output
            if contributor:
                first_contrib = False
            if "." not in val:
                # split contact into name, first name, and last name
                contributor_str, given_name, family_name = name_splitter(key)
                # attempt to get ORCiD and affiliation
                orcid_id, affiliation, ror = get_orcid_and_affiliation(key, self.file)
                # if contact has more than 1 role
                if len(val) > 1:
                    individual = person_format(
                        "contributor",
                        val,
                        contributor_str,
                        given_name,
                        family_name,
                        affiliation,
                        orcid_id,
                        ror,
                        first_contrib,
                    )
                else:
                    individual = person_format(
                        "contributor",
                        val[0],
                        contributor_str,
                        given_name,
                        family_name,
                        affiliation,
                        orcid_id,
                        ror,
                        first_contrib,
                    )
                contributor.append(individual)

        # Step 2a: check for non-author role contributors found in Contacts
        if contributors:
            for person in contributors:
                # used so that DefinedTermSet info not repeated in output
                if contributor:
                    first_contrib = False
                # split contact into name, first name, and last name
                contributor_str, given_name, family_name = name_splitter(person)
                # add call to get ORCiD and affiliation
                orcid_id, affiliation, ror = get_orcid_and_affiliation(
                    person, self.file
                )
                individual = person_format(
                    "contributor",
                    "Contributor",
                    contributor_str,
                    given_name,
                    family_name,
                    affiliation,
                    orcid_id,
                    ror,
                    first_contrib,
                )
                contributor.append(individual)
        # Step 2b: if no non-author role contributor is found, use backups (editors/curators)
        else:
            found = False
            i = 0
            # while a curator is not found
            while not found and i < len(curator_roles):
                # used so that DefinedTermSet info not repeated in output
                if contributor:
                    first_contrib = False
                # search for roles in backups that match curator_roles (in order of priority)
                keys = [key for key, val in backups.items() if curator_roles[i] in val]
                if keys != []:
                    for key in keys:
                        # split contact into name, first name, and last name
                        editor_str, given_name, family_name = name_splitter(key)
                        # add call to get ORCiD and affiliation
                        orcid_id, affiliation, ror = get_orcid_and_affiliation(
                            key, self.file
                        )
                        individual = person_format(
                            "contributor",
                            curator_roles[i],
                            editor_str,
                            given_name,
                            family_name,
                            affiliation,
                            orcid_id,
                            ror,
                            first_contrib,
                        )
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

        (
            *_,
            publisher,
            _,
            _,
            _,
            _,
        ) = get_authors(self.metadata)
        # ror = None

        # commented out ROR for now until capability added in SPASE
        """if 'spase://' in publisher:
            ORCiD, affil, ror = get_orcid_and_affiliation(publisher)
        else:
            # add full SPASE path to publisher name
            # how to do that???
            ORCiD, affil, ror = get_orcid_and_affiliation(publisher)
        if ror:
            publisher = {"@id": ror,
                        "@type": "Organization",
                        "name": publisher,
                        "identifier": ror}
        else:"""
        if publisher == "":
            publisher = None
        else:
            publisher = {"@type": "Organization", "name": publisher}
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
        # ror = None
        # iterate thru to find all info related to funding
        for child in self.desired_root.iter(tag=etree.Element):
            if child.tag.endswith("Funding"):
                target_child = child
                for child in target_child:
                    if child.tag.endswith("Agency"):
                        agency.append(child.text)
                    elif child.tag.endswith("Project"):
                        project.append(child.text)
                    elif child.tag.endswith("AwardNumber"):
                        award.append(child.text)
        # if funding info was found
        if agency:
            i = 0
            # ror = get_ROR(agency)
            for funder in agency:
                # basic format for funding item
                entry = {
                    "@type": "MonetaryGrant",
                    "funder": {"@type": "Organization", "name": funder},
                    "name": project[i],
                }
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
        licenses = []

        """<RightsList>
            <Rights>
                <SchemeURI>https://spdx.org/licenses/</SchemeURI>
                <RightsIdentifierScheme>SPDX</RightsIdentifierScheme>
                <RightsIdentifier>CC0-1.0</RightsIdentifier>
                <RightsURI>https://spdx.org/licenses/CC0-1.0.html</RightsURI>
                <RightsName>Creative Commons Zero v1.0 Universal</RightsName>
                <Note>CC0 1.0 Universal is the Creative Commons license applicable 
                    to all publicly available NASA Heliophysics data products</Note>
            </Rights>
        </RightsList>"""

        desired_tag = self.desired_root.tag.split("}")
        rights_uri = None
        spase_location = (
            ".//spase:"
            + f"{desired_tag[1]}/spase:AccessInformation/spase:RightsList/spase:Rights"
        )
        for item in self.metadata.findall(
            spase_location,
            namespaces=self.namespaces,
        ):
            for child in item.iter(tag=etree.Element):
                if child.tag.endswith("RightsURI"):
                    rights_uri = child.text
            if rights_uri not in licenses:
                licenses.append(rights_uri)
        if not licenses:
            licenses = None
        # elif len(licenses) == 1:
        #    licenses = licenses[0]
        return delete_null_values(licenses)

    def get_was_revision_of(self) -> Union[List[Dict], Dict, None]:
        # Mapping: prov:wasRevisionOf = spase:Association/spase:AssociationID
        #   (if spase:AssociationType is "RevisionOf")
        # prov:wasRevisionOf found at https://www.w3.org/TR/prov-o/#wasRevisionOf
        was_revision_of = get_relation(self.desired_root, ["RevisionOf"], self.file)
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
        is_based_on = get_relation(
            self.desired_root, ["ChildEventOf", "DerivedFrom"], self.file
        )
        return delete_null_values(is_based_on)

    def get_was_generated_by(self) -> Union[List[Dict], None]:
        # Mapping: prov:wasGeneratedBy = spase:InstrumentID/spase:ResourceID
        #   and spase:InstrumentID/spase:ResourceHeader/spase:ResourceName
        #   AND spase:InstrumentID/spase:ObservatoryID/spase:ResourceID
        #   and spase:InstrumentID/spase:ObservatoryID/spase:ResourceHeader/spase:ResourceName
        #   AND spase:InstrumentID/spase:ObservatoryID/spase:ObservatoryGroupID/spase:ResourceID
        #   and spase:InstrumentID/spase:ObservatoryID/spase:ObservatoryGroupID/
        #       spase:ResourceHeader/spase:ResourceName
        # prov:wasGeneratedBy found at https://www.w3.org/TR/prov-o/#wasGeneratedBy

        # commenting out observatories because of the email with Baptiste and Donny
        instruments = get_instrument(self.metadata, self.file)
        # only uncomment if trying to generate snapshot spase.json
        # instruments = get_instrument(
        #    self.metadata, self.file, **{"testing": "soso-spase/tests/data/spase/"}
        #    )
        # observatories = get_observatory(self.metadata, self.file)
        was_generated_by = []

        # if observatories:
        # for each in observatories:
        # was_generated_by.append({"@type": ["ResearchProject", "prov:Activity"],
        # "prov:used": each})
        if instruments:
            for each in instruments:
                was_generated_by.append(
                    {"@type": ["ResearchProject", "prov:Activity"], "prov:used": each}
                )

        if not was_generated_by:
            was_generated_by = None
        return delete_null_values(was_generated_by)


# Below are utility functions for the SPASE strategy.


def get_schema_version(metadata: etree.ElementTree) -> str:
    """
    :param metadata: The SPASE metadata object as an XML tree.

    :returns: The version of the SPASE schema used in the metadata record.
    """
    namespace = ""
    for ns in list(metadata.getroot().nsmap.values()):
        if "spase-group" in ns:
            namespace = ns
    schema_version = metadata.findtext(f"{{{namespace}}}Version")
    return schema_version


def get_authors(
    metadata: etree.ElementTree, file="PlaceholderText"
) -> tuple[List, List, str, str, List, str, Dict, Dict]:
    """
    Takes an XML tree and scrapes the desired authors (with their roles), publication date,
    publisher, contributors, and publication title. Also scraped are the names and roles of
    the backups, which are any Contacts found that are not considered authors. It then returns
    these items, with the author, author roles, and contributors as lists and the rest as strings,
    except for the backups which is a dictionary.

    :param metadata: The SPASE metadata object as an XML tree.
    :param file: The absolute path of the SPASE record being scraped.

    :returns: The highest priority authors found within the SPASE record as a list
                as well as a list of their roles, the publication date, publisher,
                contributors, and the title of the publication. It also returns any contacts found,
                along with their role(s) in two separate dictionaries: ones that are not considered
                for the author role and ones that are.
    """
    # local vars needed
    author = []
    contacts_list = {}
    author_role = []
    pub_date = ""
    pub = ""
    contributor = []
    dataset = ""
    backups = {}
    pi_child = None
    desired_root = None
    root = metadata.getroot()
    if file:
        file = file.replace("\\", "/")
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desired_root = elt

    # traverse xml to extract needed info
    # iterate thru to find ResourceHeader
    if desired_root is not None:
        for child in desired_root.iter(tag=etree.Element):
            if child.tag.endswith("ResourceHeader"):
                target_child = child
                # iterate thru to find PublicationInfo
                for child in target_child:
                    try:
                        if child.tag.endswith("PublicationInfo"):
                            pi_child = child
                        elif child.tag.endswith("Contact"):
                            c_child = child
                            # iterate thru Contact to find PersonID and Role
                            for child in c_child:
                                try:
                                    # find PersonID
                                    if child.tag.endswith("PersonID"):
                                        # store PersonID
                                        person_id = child.text.strip()
                                        backups[person_id] = []
                                        contacts_list[person_id] = []
                                    # find Role
                                    elif child.tag.endswith("Role"):
                                        # backup author
                                        if (
                                            ("PrincipalInvestigator" in child.text)
                                            or ("PI" in child.text)
                                            or ("CoInvestigator" in child.text)
                                            or ("Author" in child.text)
                                        ):
                                            if person_id not in author:
                                                author.append(person_id)
                                                author_role.append(child.text.strip())
                                            else:
                                                index = author.index(person_id)
                                                author_role[index] = [
                                                    author_role[index],
                                                    child.text.strip(),
                                                ]
                                            # store author roles found here in case PubInfo present
                                            contacts_list[person_id] += [
                                                child.text.strip()
                                            ]
                                        # preferred contributor
                                        elif child.text == "Contributor":
                                            contributor.append(person_id)
                                        # backup publisher (none found in SPASE currently)
                                        elif child.text == "Publisher":
                                            pub = child.text.strip()
                                        else:
                                            # use list for values in case one person
                                            #   has multiple roles
                                            # store contacts w non-author roles for
                                            #   use in contributors
                                            backups[person_id] += [child.text.strip()]
                                except AttributeError:
                                    continue
                    except AttributeError:
                        continue
        if pi_child is not None:
            for child in pi_child.iter(tag=etree.Element):
                # collect preferred author
                if child.tag.endswith("Authors"):
                    author = [child.text.strip()]
                    author_role = ["Author"]
                # collect preferred publication date
                elif child.tag.endswith("PublicationDate"):
                    pub_date = child.text.strip()
                # collect preferred publisher
                elif child.tag.endswith("PublishedBy"):
                    pub = child.text.strip()
                # collect preferred dataset
                elif child.tag.endswith("Title"):
                    dataset = child.text.strip()

        # remove contacts w/o role values
        contacts_copy = {}
        for contact, role in contacts_list.items():
            if role:
                contacts_copy[contact] = role
        # compare author and contacts_list to add author roles
        #   from contacts_list for matching people found in PubInfo
        # also formats the author list correctly for use in get_creator
        author, author_role, contacts_list = process_authors(
            author, author_role, contacts_copy, file
        )

    return (
        author,
        author_role,
        pub_date,
        pub,
        contributor,
        dataset,
        backups,
        contacts_list,
    )


def get_access_urls(metadata: etree.ElementTree) -> tuple[Dict, Dict]:
    """
    Splits the SPASE AccessURLs present in the record into either the distribution
    or potentialAction schema.org properties.

    :param metadata: The SPASE metadata object as an XML tree.

    :returns: The AccessURLs found in the SPASE record, separated into two dictionaries,
                data_downloads and potential_actions, depending on if they are a direct
                link to data or not. These dictionaries are setup to have the keys as
                the url and the values to be a list containing their data format(s),
                name, and product key (if applicable).
    """
    # needed local vars
    data_downloads = {}
    potential_actions = {}
    access_urls = {}
    encoding = []
    encoder = []
    i = 0
    j = 0
    desired_root = None
    root = metadata.getroot()
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desired_root = elt

    # get Formats before iteration due to order of elements in SPASE record
    desired_tag = desired_root.tag.split("}")
    spase_location = (
        ".//spase:" + f"{desired_tag[1]}/spase:AccessInformation/spase:Format"
    )
    namespace = ""
    for ns in list(root.nsmap.values()):
        if "spase-group" in ns:
            namespace = ns
    for item in metadata.findall(spase_location, namespaces={"spase": namespace}):
        encoding.append(item.text)

    # traverse xml to extract needed info
    # iterate thru children to locate Access Information
    for child in desired_root.iter(tag=etree.Element):
        if child.tag.endswith("AccessInformation"):
            target_child = child
            # iterate thru children to locate AccessURL and Format
            for child in target_child:
                if child.tag.endswith("AccessURL"):
                    target_child = child
                    name = ""
                    # iterate thru children to locate URL
                    for child in target_child:
                        if child.tag.endswith("URL"):
                            url = child.text
                            # provide "NULL" value in case no keys are found
                            access_urls[url] = {"keys": [], "name": name}
                            # append an encoder for each URL
                            encoder.append(encoding[j])
                        # check if URL has a product key
                        elif child.tag.endswith("ProductKey"):
                            prod_key = child.text
                            # if only one prod_key exists
                            if access_urls[url]["keys"] == []:
                                access_urls[url]["keys"] = [prod_key]
                            # if multiple prod_keys exist
                            else:
                                access_urls[url]["keys"] += [prod_key]
                        elif child.tag.endswith("Name"):
                            name = child.text
            j += 1
    for k, v in access_urls.items():
        # if URL has no access key
        if not v["keys"]:
            # non_data_file_ext = ["html", "com", "gov", "edu", "org", "eu", "int"]
            data_file_ext = [
                "csv",
                "cdf",
                "fits",
                "txt",
                "nc",
                "jpeg",
                "png",
                "gif",
                "tar",
                "netcdf3",
                "netcdf4",
                "hdf5",
                "zarr",
                "asdf",
                "zip",
            ]
            substring = k.split("://")
            domain = substring[1]
            domain, _, download_file = domain.rpartition("/")
            download_file, _, ext = download_file.rpartition(".")
            # see if file extension is one associated w data files
            if ext not in data_file_ext:
                downloadable = False
            else:
                downloadable = True
            # if URL is direct link to download data, add to the data_downloads dictionary
            if downloadable:
                if v["name"]:
                    data_downloads[k] = [encoder[i], v["name"]]
                else:
                    data_downloads[k] = [encoder[i]]
            else:
                potential_actions[k] = [encoder[i], v]
        # if URL has access key, add to the potential_actions dictionary
        else:
            potential_actions[k] = [encoder[i], v]
        i += 1
    return data_downloads, potential_actions


def get_dates(
    metadata: etree.ElementTree,
) -> Union[tuple[datetime, List[datetime]], tuple[str, List]]:
    """
    Scrapes the ReleaseDate and RevisionHistory:ReleaseDate(s) SPASE properties for use
    in the dateModified, dateCreated, and datePublished schema.org properties.

    :param metadata: The SPASE metadata object as an XML tree.

    :returns: The ReleaseDate and a list of all the dates found in RevisionHistory
    """
    desired_root = None
    root = metadata.getroot()
    for elt in root.iter(tag=etree.Element):
        if (
            elt.tag.endswith("NumericalData")
            or elt.tag.endswith("DisplayData")
            or elt.tag.endswith("Collection")
        ):
            desired_root = elt
    revision_history = []
    release_date = ""

    # traverse xml to extract needed info
    for child in desired_root.iter(tag=etree.Element):
        if child.tag.endswith("ResourceHeader"):
            target_child = child
            for child in target_child:
                # find ReleaseDate and construct datetime object from the string
                try:
                    if child.tag.endswith("ReleaseDate"):
                        date, _, time_str = child.text.partition("T")
                        if "Z" in child.text:
                            time_str = time_str.replace("Z", "")
                        if "." in child.text:
                            time_str, _, _ = time_str.partition(".")
                        dt_string = date + " " + time_str
                        dt_obj = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
                        release_date = dt_obj
                    elif child.tag.endswith("RevisionHistory"):
                        rev_hist_child = child
                        for child in rev_hist_child:
                            rev_ev_child = child
                            for child in rev_ev_child:
                                if child.tag.endswith("ReleaseDate"):
                                    date, _, time_str = child.text.partition("T")
                                    if "Z" in child.text:
                                        time_str = time_str.replace("Z", "")
                                    if "." in child.text:
                                        time_str, _, _ = time_str.partition(".")
                                    dt_string = date + " " + time_str
                                    try:
                                        dt_obj = datetime.strptime(
                                            dt_string, "%Y-%m-%d %H:%M:%S"
                                        )
                                    # catch error when RevisionHistory is not formatted w time
                                    except ValueError:
                                        dt_obj = datetime.strptime(
                                            dt_string.strip(), "%Y-%m-%d"
                                        ).date()
                                    finally:
                                        revision_history.append(dt_obj)
                except AttributeError:
                    continue
    return release_date, revision_history


def person_format(
    person_type: str,
    role_name: Union[str, List],
    name: str,
    given_name: str,
    family_name: str,
    affiliation: str = "",
    orcid_id: str = "",
    ror: str = "",
    first_entry: bool = False,
) -> Dict:
    """
    Groups up all available metadata associated with a given contact
    into a dictionary following the SOSO guidelines.

    :param person_type: The type of person being formatted. Values can be either:
        contributor or creator.
    :param role_name: The value found in the Role field associated with this Contact
    :param name: The full name of the Contact, as formatted in the SPASE record
    :param given_name: The first name/initial and middle name/initial of the Contact
    :param family_name: The last name of the Contact
    :param affiliation: The organization this Contact is affiliated with.
    :param orcid_id: The ORCiD identifier for this Contact
    :param ror: The ROR ID for the associated affiliation
    :param first_entry: Boolean signifying if this person is the
        first entry into its respective property result.

    :returns: The entry in the correct format to append to the contributor or creator dictionary
    """

    *_, orcid_val = orcid_id.rpartition("/")
    entry = None
    if name:
        # add check for organization
        if ", " in name or ". " in name or (given_name and family_name) or "_" in name:
            item_type = "Person"
        else:
            item_type = "Organization"
        # most basic format for creator item
        if person_type == "creator":
            entry = {"@type": item_type, "name": name}
            if (given_name and family_name) and item_type == "Person":
                entry["familyName"] = family_name.strip()
                entry["givenName"] = given_name.strip()
        elif person_type == "contributor":
            if isinstance(role_name, list):
                pretty_name = []
                for role in role_name:
                    # Split string on uppercase characters
                    res = re.split(r"(?=[A-Z])", role)
                    # prevent 'PI' from turning into 'P I'
                    if "PI" in role:
                        first, sep, _ = role.partition("PI")
                        if "Co" in first:
                            separated_name = first + "-" + sep
                        else:
                            separated_name = first + " " + sep
                    # Remove empty strings and join with space or hypen depending on role
                    elif "Co" in role:
                        pattern = r"{}(?=[A-Z])".format(re.escape("Co"))
                        if bool(re.search(pattern, role)):
                            separated_name = "-".join(filter(None, res))
                        else:
                            separated_name = " ".join(filter(None, res))
                    else:
                        separated_name = " ".join(filter(None, res))
                    pretty_name.append(separated_name.strip())
            else:
                # Split string on uppercase characters
                res = re.split(r"(?=[A-Z])", role_name)
                # prevent 'PI' from turning into 'P I'
                if "PI" in role_name:
                    first, sep, _ = role_name.partition("PI")
                    if "Co" in first:
                        pretty_name = first + "-" + sep
                    else:
                        pretty_name = first + " " + sep
                # Remove empty strings and join with space or hypen depending on role_name
                elif "Co" in role_name:
                    pattern = r"{}(?=[A-Z])".format(re.escape("Co"))
                    if bool(re.search(pattern, role_name)):
                        pretty_name = "-".join(filter(None, res))
                    else:
                        pretty_name = " ".join(filter(None, res))
                else:
                    pretty_name = " ".join(filter(None, res))
                pretty_name = pretty_name.strip()
            # most basic format for contributor item
            entry = {
                "@type": ["Role", "DefinedTerm"],
                "contributor": {"@type": item_type, "name": name},
                "inDefinedTermSet": {
                    "@id": "https://spase-group.org/data/model/spase-latest/"
                    + "spase-latest_xsd.htm#Role"
                },
                "roleName": pretty_name,
                "termCode": role_name,
            }

            if (given_name and family_name) and item_type == "Person":
                entry["contributor"]["familyName"] = family_name.strip()
                entry["contributor"]["givenName"] = given_name.strip()

            if first_entry:
                entry["inDefinedTermSet"]["@type"] = "DefinedTermSet"
                entry["inDefinedTermSet"]["name"] = "SPASE Role"
                entry["inDefinedTermSet"][
                    "url"
                ] = "https://spase-group.org/data/model/spase-latest/spase-latest_xsd.htm#Role"

        if item_type == "Person":
            if orcid_id:
                if person_type == "contributor":
                    entry[f"{person_type}"]["identifier"] = {
                        "@id": f"https://orcid.org/{orcid_id}",
                        "@type": "PropertyValue",
                        "propertyID": "https://registry.identifiers.org/registry/orcid",
                        "url": f"https://orcid.org/{orcid_id}",
                        "value": f"orcid:{orcid_val}",
                    }
                    entry[f"{person_type}"]["@id"] = f"https://orcid.org/{orcid_id}"
                else:
                    entry["identifier"] = {
                        "@id": f"https://orcid.org/{orcid_id}",
                        "@type": "PropertyValue",
                        "propertyID": "https://registry.identifiers.org/registry/orcid",
                        "url": f"https://orcid.org/{orcid_id}",
                        "value": f"orcid:{orcid_val}",
                    }
                    entry["@id"] = f"https://orcid.org/{orcid_id}"
            if affiliation:
                if person_type == "contributor":
                    if ror:
                        entry["contributor"]["affiliation"] = {
                            "@type": "Organization",
                            "name": affiliation,
                            "identifier": {
                                "@id": f"https://ror.org/{ror}",
                                "@type": "PropertyValue",
                                "propertyID": "https://registry.identifiers.org/registry/ror",
                                "url": f"https://ror.org/{ror}",
                                "value": f"ror:{ror}",
                            },
                        }
                    else:
                        entry["contributor"]["affiliation"] = {
                            "@type": "Organization",
                            "name": affiliation,
                        }
                else:
                    if ror:
                        entry["affiliation"] = {
                            "@type": "Organization",
                            "name": affiliation,
                            "identifier": {
                                "@id": f"https://ror.org/{ror}",
                                "@type": "PropertyValue",
                                "propertyID": "https://registry.identifiers.org/registry/ror",
                                "url": f"https://ror.org/{ror}",
                                "value": f"ror:{ror}",
                            },
                        }
                    else:
                        entry["affiliation"] = {
                            "@type": "Organization",
                            "name": affiliation,
                        }
    return entry


def name_splitter(person: str) -> tuple[str, str, str]:
    """
    Splits the given PersonID found in the SPASE Contacts container into
    three separate strings holding their full name, first name (and middle initial),
    and last name.

    :param person: The string found in the Contacts field as is formatted in the SPASE record.

    :returns: The string containing the full name of the Contact, the string
        containing the first name/initial of the Contact,
        and the string containing the last name of the Contact
    """
    if person:
        *_, name_str = person.partition("Person/")
        # get rid of extra quotations
        name_str = name_str.replace("'", "")
        if "." in name_str:
            given_name, _, family_name = name_str.partition(".")
            # if first name is also initial
            if len(given_name) == 1:
                given_name += "."
            # if person has a generational suffix
            if (
                family_name.endswith(".II")
                or family_name.endswith(".III")
                or family_name.endswith(".Jr")
                or family_name.endswith(".Sr")
            ):
                family_name, _, suffix = family_name.rpartition(".")
                family_name = family_name + " " + suffix
            # if name has initial(s)
            while "." in family_name:
                initial, _, family_name = family_name.partition(".")
                if len(initial) > 1:
                    initial = initial[0]
                given_name = given_name + " " + initial + "."
            name_str = given_name + " " + family_name
            name_str = name_str.replace('"', "")
        else:
            given_name = ""
            family_name = ""
    else:
        raise ValueError(
            "This function only takes a nonempty string as an argument. Try again."
        )
    return name_str, given_name, family_name


def get_information_url(metadata: etree.ElementTree) -> Union[List[Dict], None]:
    """
    Returns all relevant information from the SPASE informationURL(s) property for use
    within the schema.org citation property.

    :param metadata: The SPASE metadata object as an XML tree.

    :returns: The name, description, and url(s) for all InformationURL
                sections found in the ResourceHeader, formatted as a
                list of dictionaries.
    """
    root = metadata.getroot()
    information_url = []
    name = ""
    description = ""
    url = ""
    desired_root = None
    for elt in root.iter(tag=etree.Element):
        if (
            elt.tag.endswith("NumericalData")
            or elt.tag.endswith("DisplayData")
            or elt.tag.endswith("Observatory")
            or elt.tag.endswith("Instrument")
            or elt.tag.endswith("Collection")
        ):
            desired_root = elt
    # traverse xml to extract needed info
    for child in desired_root.iter(tag=etree.Element):
        if child.tag.endswith("ResourceHeader"):
            target_child = child
            # iterate thru children to locate AccessURL and Format
            for child in target_child:
                try:
                    if child.tag.endswith("InformationURL"):
                        target_child = child
                        # iterate thru children to locate URL
                        for child in target_child:
                            if child.tag.endswith("Name"):
                                name = child.text
                            elif child.tag.endswith("URL"):
                                url = child.text
                            elif child.tag.endswith("Description"):
                                description = child.text
                        if name:
                            if description:
                                information_url.append(
                                    {
                                        "name": name,
                                        "url": url,
                                        "description": description,
                                    }
                                )
                            else:
                                information_url.append({"name": name, "url": url})
                        else:
                            information_url.append({"url": url})
                except AttributeError:
                    continue
    if not information_url:
        information_url = None
    return information_url


def get_instrument(
    metadata: etree.ElementTree, path: str, **kwargs: dict
) -> Union[List[Dict], None]:
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
    desired_root = None
    instrument = []
    instrument_ids = {}
    if path:
        path = path.replace("\\", "/")
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desired_root = elt
    for child in desired_root.iter(tag=etree.Element):
        if child.tag.endswith("InstrumentID"):
            instrument_ids[child.text] = {}
    if not instrument_ids:
        instrument = None
    else:
        # if called by testing function, only test first link
        if kwargs:
            for key, val in instrument_ids.items():
                if key == "spase://SMWG/Instrument/MMS/4/FIELDS/FGM":
                    instrument_ids = {key: val}
        # follow link provided by instrumentID to instrument page
        # from there grab name and url
        for item in instrument_ids.keys():
            instrument_ids[item]["name"] = ""
            instrument_ids[item]["URL"] = ""

            # get home directory
            home_dir = str(Path.home())
            home_dir = home_dir.replace("\\", "/")
            # get current working directory
            cwd = str(Path.cwd()).replace("\\", "/")
            # split path into needed substrings
            if "src/soso/strategies/spase/" in path:
                abs_path, _, after = path.partition("src/soso/strategies/spase/")
            else:
                _, abs_path, after = path.partition(f"{home_dir}/")
            repo_name, _, after = after.partition("/")
            # add original SPASE repo to log file that holds name of repos needed
            update_log(cwd, repo_name, "requiredRepos")
            # add SPASE repo that contains instruments also
            repo_name, _, after = item.replace("spase://", "").partition("/")
            update_log(cwd, repo_name, "requiredRepos")
            # format record
            if "src/soso/strategies/spase/" in path:
                # being called by testing function = change directory to xml file in tests folder
                # only uncomment these lines if using snapshot creation script
                # if "soso-spase/" in path:
                #    record = abs_path + item.replace("spase://", "") + ".xml"
                # else:
                # if called by CI
                *_, file_name = item.rpartition("/")
                record = abs_path + "tests/data/spase/" + f"spase-{file_name}" + ".xml"
                # to ensure correct file path used for those not found in tests/data
                if not os.path.isfile(record):
                    if "soso-spase/" in path:
                        abs_path, _, _ = path.partition("soso-spase/")
                    record = abs_path + item.replace("spase://", "") + ".xml"
            else:
                record = abs_path + item.replace("spase://", "") + ".xml"
            record = record.replace("'", "")
            if os.path.isfile(record):
                test_spase = SPASE(record)
                root = test_spase.metadata.getroot()
                instrument_ids[item]["name"] = test_spase.get_name()
                instrument_ids[item]["URL"] = test_spase.get_url()
            else:
                # add file to log containing problematic records/files
                if os.path.exists(temp_file_path):
                    temp_file.seek(0)
                    if temp_file.read():
                        temp_file.write(f", {record}")
                    else:
                        temp_file.write(f"{record}")
        for k in instrument_ids.keys():
            if instrument_ids[k]["URL"]:
                instrument.append(
                    {
                        "@id": instrument_ids[k]["URL"],
                        "@type": ["IndividualProduct", "prov:Entity", "sosa:System"],
                        "identifier": {
                            "@id": instrument_ids[k]["URL"],
                            "@type": "PropertyValue",
                            "propertyID": "SPASE Resource ID",
                            "value": k,
                        },
                        "name": instrument_ids[k]["name"],
                        "url": instrument_ids[k]["URL"],
                    }
                )
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
    # Mapping: schema:ResearchProject, prov:Entity, and sosa:Platform =
    #   spase:InstrumentID/spase:ObservatoryID
    #   AND spase:InstrumentID/spase:ObservatoryID/spase:ObservatoryGroupID if available
    # schema:ResearchProject found at https://schema.org/ResearchProject
    # prov:Entity found at https://www.w3.org/TR/prov-o/#Entity
    # sosa:Platform found at https://w3c.github.io/sdw-sosa-ssn/ssn/#SOSAPlatform

    instrument = get_instrument(metadata, path)
    if instrument is not None:
        observatory = []
        observatory_group_id = ""
        observatory_id = ""
        recorded_ids = []
        instrument_ids = []
        if path:
            path = path.replace("\\", "/")

        for each in instrument:
            instrument_ids.append(each["identifier"]["value"])
        for item in instrument_ids:
            # get home directory
            home_dir = str(Path.home())
            home_dir = home_dir.replace("\\", "/")
            # get current working directory
            cwd = str(Path.cwd()).replace("\\", "/")
            # split path into needed substrings
            if "src/soso/strategies/spase/" in path:
                abs_path, _, after = path.partition("src/soso/strategies/spase/")
            else:
                _, abs_path, after = path.partition(f"{home_dir}/")
            repo_name, _, after = after.partition("/")
            # add original SPASE repo to log file that holds name of repos needed
            update_log(cwd, repo_name, "requiredRepos")
            if "src/soso/strategies/spase/" in path:
                # being called by testing function = change directory
                #   to xml file in tests folder
                *_, file_name = item.rpartition("/")
                record = abs_path + "tests/data/spase/" + f"spase-{file_name}" + ".xml"
            else:
                record = abs_path + item.replace("spase://", "") + ".xml"
            record = record.replace("'", "")
            # follow link provided by instrument to instrument page,
            #   from there grab ObservatoryID
            if os.path.isfile(record):
                test_spase = SPASE(record)
                root = test_spase.metadata.getroot()
                for elt in root.iter(tag=etree.Element):
                    if elt.tag.endswith("Instrument"):
                        desired_root = elt
                for child in desired_root.iter(tag=etree.Element):
                    if child.tag.endswith("ObservatoryID"):
                        observatory_id = child.text
                # add SPASE repo that contains observatories to log file also
                repo_name, _, after = observatory_id.replace("spase://", "").partition(
                    "/"
                )
                update_log(cwd, repo_name, "requiredRepos")
                # use observatory_id as record to get observatory_group_id and other info
                if "src/soso/strategies/spase/" in path:
                    # being called by test function = change directory to xml file in tests folder
                    *_, file_name = observatory_id.rpartition("/")
                    record = (
                        abs_path
                        + "tests/data/spase/"
                        + f"spase-MMS-{file_name}"
                        + ".xml"
                    )
                else:
                    record = abs_path + observatory_id.replace("spase://", "") + ".xml"
                record = record.replace("'", "")
                if os.path.isfile(record):
                    url = ""
                    test_spase = SPASE(record)
                    root = test_spase.metadata.getroot()
                    for elt in root.iter(tag=etree.Element):
                        if elt.tag.endswith("Observatory"):
                            desired_root = elt
                    for child in desired_root.iter(tag=etree.Element):
                        if child.tag.endswith("ObservatoryGroupID"):
                            observatory_group_id = child.text
                    name = test_spase.get_name()
                    url = test_spase.get_url()
                    # finally, follow that link to grab name and url from there
                    if observatory_group_id:
                        # add SPASE repo that contains observatory group to log file also
                        repo_name, _, after = observatory_group_id.replace(
                            "spase://", ""
                        ).partition("/")
                        update_log(cwd, repo_name, "requiredRepos")
                        # format record
                        if "src/soso/strategies/spase/" in path:
                            # being called by test function = change directory to xml file in tests
                            #   folder
                            *_, file_name = observatory_group_id.rpartition("/")
                            record = (
                                abs_path
                                + "tests/data/spase/"
                                + f"spase-{file_name}"
                                + ".xml"
                            )
                        else:
                            record = (
                                abs_path
                                + observatory_group_id.replace("spase://", "")
                                + ".xml"
                            )
                        record = record.replace("'", "")
                        if os.path.isfile(record):
                            group_url = ""
                            test_spase = SPASE(record)
                            group_name = test_spase.get_name()
                            group_url = test_spase.get_url()
                            if group_url:
                                if observatory_group_id not in recorded_ids:
                                    observatory.append(
                                        {
                                            "@type": [
                                                "ResearchProject",
                                                "prov:Entity",
                                                "sosa:Platform",
                                            ],
                                            "@id": group_url,
                                            "name": group_name,
                                            "identifier": {
                                                "@id": group_url,
                                                "@type": "PropertyValue",
                                                "propertyID": "SPASE Resource ID",
                                                "value": observatory_group_id,
                                            },
                                            "url": group_url,
                                        }
                                    )
                                    recorded_ids.append(observatory_group_id)
                        else:
                            # add obsGrp to log file containing problematic records/files
                            if os.path.exists(temp_file_path):
                                temp_file.seek(0)
                                if temp_file.read():
                                    temp_file.write(f", {record}")
                                else:
                                    temp_file.write(f"{record}")
                    if url and (observatory_id not in recorded_ids):
                        observatory.append(
                            {
                                "@type": [
                                    "ResearchProject",
                                    "prov:Entity",
                                    "sosa:Platform",
                                ],
                                "@id": url,
                                "name": name,
                                "identifier": {
                                    "@id": url,
                                    "@type": "PropertyValue",
                                    "propertyID": "SPASE Resource ID",
                                    "value": observatory_id,
                                },
                                "url": url,
                            }
                        )
                        recorded_ids.append(observatory_id)
                else:
                    if os.path.exists(temp_file_path):
                        temp_file.seek(0)
                        if temp_file.read():
                            temp_file.write(f", {record}")
                        else:
                            temp_file.write(f"{record}")
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
    desired_root = None
    for elt in root.iter(tag=etree.Element):
        if (
            elt.tag.endswith("NumericalData")
            or elt.tag.endswith("DisplayData")
            or elt.tag.endswith("Collection")
        ):
            desired_root = elt
    for child in desired_root.iter(tag=etree.Element):
        if child.tag.endswith("ResourceHeader"):
            target_child = child
            # iterate thru children to locate AlternateName for dataset
            for child in target_child:
                try:
                    if child.tag.endswith("AlternateName"):
                        alternate_name = child.text
                except AttributeError:
                    continue
    return alternate_name


def get_cadence_context(cadence: str) -> Union[str, None]:
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
    if cadence is not None:
        start, _, end = cadence.partition("P")
        # cadence is in hrs, min, or sec
        if "T" in end:
            start, _, time_str = end.partition("T")
            if "H" in time_str:
                # hrs
                start, _, end = time_str.partition("H")
                context += start + " hour cadence"
            elif "M" in time_str:
                # min
                start, _, end = time_str.partition("M")
                context += start + " minute cadence"
            elif "S" in time_str:
                # sec
                start, _, end = time_str.partition("S")
                context += start + " second cadence"
        # one of the 3 base cadences
        else:
            if "D" in end:
                # days
                start, _, end = end.partition("D")
                context += start + " day cadence"
            elif "M" in end:
                # months
                start, _, end = end.partition("M")
                context += start + " month cadence"
            elif "Y" in end:
                # yrs
                start, _, end = end.partition("Y")
                context += start + " year cadence"
    if context == "The time series is periodic with a ":
        context = None
    return context


def get_mentions(
    metadata: etree.ElementTree, file: str, **kwargs: dict
) -> Union[List[Dict], Dict, None]:
    """
    Scrapes any AssociationIDs with the AssociationType "Other" and formats them
    as dictionaries using the get_relation function.

    :param metadata: The SPASE metadata object as an XML tree.
    :param file: The file path of the SPASE record being scraped.
    :param **kwargs: Allows for additional parameters to be passed (only to be used for testing).

    :returns: The ID's of other SPASE records related to this one in some way.
    """
    # Mapping: schema:mentions = spase:Association/spase:AssociationID
    #   (if spase:AssociationType is "Other")
    # schema:mentions found at https://schema.org/mentions
    root = metadata.getroot()
    desired_root = None
    for elt in root.iter(tag=etree.Element):
        if (
            elt.tag.endswith("NumericalData")
            or elt.tag.endswith("DisplayData")
            or elt.tag.endswith("Collection")
        ):
            desired_root = elt
    mentions = get_relation(desired_root, ["Other"], file, **kwargs)
    return mentions


def get_is_part_of(
    metadata: etree.ElementTree, file: str, **kwargs: dict
) -> Union[List[Dict], Dict, None]:
    """
    Scrapes any AssociationIDs with the AssociationType "PartOf" and formats them
    as dictionaries using the get_relation function.

    :param metadata: The SPASE metadata object as an XML tree.
    :param file: The file path of the SPASE record being scraped.
    :param **kwargs: Allows for additional parameters to be passed (only to be used for testing).

    :returns: The ID(s) of the larger resource this SPASE record is a portion of, as a dictionary.
    """
    # Mapping: schema:isBasedOn = spase:Association/spase:AssociationID
    #   (if spase:AssociationType is "PartOf")
    # schema:isPartOf found at https://schema.org/isPartOf
    root = metadata.getroot()
    desired_root = None
    for elt in root.iter(tag=etree.Element):
        if (
            elt.tag.endswith("NumericalData")
            or elt.tag.endswith("DisplayData")
            or elt.tag.endswith("Collection")
        ):
            desired_root = elt
    is_part_of = get_relation(desired_root, ["PartOf"], file, **kwargs)
    return is_part_of


def get_orcid_and_affiliation(spase_id: str, file: str) -> tuple[str, str, str]:
    """
    Uses the given PersonID to scrape the ORCiD and affiliation (and its ROR ID if provided)
    associated with this contact.

    :param spase_id: The SPASE ID linking the page with the Person's or Repository's info.
    :param file: The absolute path of the original xml file scraped.

    :returns: The ORCiD ID and organization name (with its ROR ID, if found) this
                Contact is affiliated with, as strings.
    """
    # takes spase_id and follows its link to get ORCIdentifier, OrganizationName, and RORIdentifier
    orcid_id = ""
    affiliation = ""
    ror = ""
    desired_root = None
    if file:
        file = file.replace("\\", "/")
    if (spase_id is not None) and (file is not None):
        # get home directory
        home_dir = str(Path.home()).replace("\\", "/")
        # get current working directory
        cwd = str(Path.cwd()).replace("\\", "/")
        # split record into needed substrings
        if "src/soso/strategies/spase/" in file:
            abs_path, _, after = file.partition("src/soso/strategies/spase/")
        else:
            _, abs_path, after = file.partition(f"{home_dir}/")
        repo_name, _, after = after.partition("/")
        # add original SPASE repo to log file that holds name of repos needed
        update_log(cwd, repo_name, "requiredRepos")
        # add SPASE repo that contains Person descriptions to log file also
        repo_name, _, after = spase_id.replace("spase://", "").partition("/")
        update_log(cwd, repo_name, "requiredRepos")
        # format record name
        if "src/soso/strategies/spase/" in file:
            # being called by testing function = change directory to xml file in tests folder
            *_, file_name = spase_id.rpartition("/")
            record = abs_path + "tests/data/spase/" + f"spase-{file_name}" + ".xml"
            # to ensure correct file path used for those not found in tests/data
            # comment these lines out if using snapshot creation script
            if not os.path.isfile(record):
                if "soso-spase/" in file:
                    abs_path, _, _ = file.partition("soso-spase/")
                record = abs_path + spase_id.replace("spase://", "") + ".xml"
        else:
            record = abs_path + spase_id.replace("spase://", "") + ".xml"
        record = record.replace("'", "")
        if os.path.isfile(record):
            test_spase = SPASE(record)
            root = test_spase.metadata.getroot()
            # iterate thru xml to get desired info
            for elt in root.iter(tag=etree.Element):
                if elt.tag.endswith("Person") or elt.tag.endswith("Repository"):
                    desired_root = elt
            for child in desired_root.iter(tag=etree.Element):
                if child.tag.endswith("ORCIdentifier"):
                    orcid_id = child.text
                elif child.tag.endswith("OrganizationName"):
                    affiliation = child.text
                elif child.tag.endswith("RORIdentifier"):
                    ror = child.text
        else:
            # add file to log containing problematic records/files
            if os.path.exists(temp_file_path):
                temp_file.seek(0)
                if temp_file.read():
                    temp_file.write(f", {record}")
                else:
                    temp_file.write(f"{record}")
    return orcid_id, affiliation, ror


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
    desired_root = None
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desired_root = elt

    desired_tag = desired_root.tag.split("}")
    spase_location = (
        ".//spase:" + f"{desired_tag[1]}/spase:TemporalDescription/spase:Cadence"
    )
    repeat_frequency = metadata.findtext(
        spase_location,
        namespaces=namespaces,
    )

    explanation = ""

    if repeat_frequency:
        explanation = get_cadence_context(repeat_frequency)
        temporal = [explanation, repeat_frequency]
    else:
        temporal = None
    return delete_null_values(temporal)


def get_metadata_license(metadata: etree.ElementTree) -> Union[str, None]:
    """
    :param metadata: The metadata object as an XML tree.

    :returns: The metadata license(s) of the SPASE record.
    """

    """<MetadataRightsList>
            <Rights>
                <SchemeURI>https://spdx.org/licenses/</SchemeURI>
                <RightsIdentifierScheme>SPDX</RightsIdentifierScheme>
                <RightsIdentifier>CC0-1.0</RightsIdentifier>
                <RightsURI>https://spdx.org/licenses/CC0-1.0.html</RightsURI>
                <RightsName>Creative Commons Zero v1.0 Universal</RightsName>
                <Note>CC0 1.0 Universal is the Creative Commons license applicable 
                    to all publicly available SPASE metadata descriptions</Note>
            </Rights>
        </MetadataRightsList>"""
    metadata_license = []
    desired_root = None
    root = metadata.getroot()
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("MetadataRightsList"):
            desired_root = elt
    if desired_root is not None:
        for elt in desired_root.iter(tag=etree.Element):
            if elt.tag.endswith("Rights"):
                target_child = elt
                for child in target_child:
                    if child.tag.endswith("RightsName"):
                        metadata_license.append(child.text)
        if not metadata_license:
            metadata_license = None
    else:
        metadata_license = None
    return metadata_license


def process_authors(
    author: List, author_role: List, contacts_list: Dict, file="PlaceholderText"
) -> tuple[List, List, Dict]:
    """
    Groups any contact names from the SPASE Contacts container with their matching names, if
    found, in PubInfo:Authors, and adds any additional author roles (such as PI) to their
    corresponding entry in the author_roles list. Any contact with an author role not
    listed in PubInfo:Authors is added to the contacts_list with the rest of the
    non-matching contacts for use in get_contributors.

    :param author: The list of names found in SPASE record to be used in get_creator
    :param author_role: The list of roles associated with each person found in author list
    :param contacts_list: The dictionary containing the names of people considered to
                            be authors as formatted in the Contacts container in the
                            SPASE record, as well as their roles

    :returns: The updated author, author_roles, and contacts_list items after merging any author
                roles from Contacts with the roles associated with them if found in PubInfo.
    """
    # loop thru all contacts to find any that match authors, unless no PubInfo was found
    # if matches found, add roles to author_roles and remove them from contacts_list
    # if no match found for person(s), leave in contacts_list for use in get_contributors

    author_str = str(author).replace("[", "").replace("]", "")
    if file:
        file = file.replace("\\", "/")
    # if creators were found in Contact/PersonID (no PubInfo)
    # remove author roles from contacts_list so not duplicated in contributors
    #   (since already in author list)
    if "Person/" in author_str:
        contacts_copy = {}
        for person, val in contacts_list.items():
            contacts_copy[person] = []
            for role in val:
                # if role is not considered for author, add to acceptable roles
                #   list for use in contributors
                if (
                    ("PrincipalInvestigator" not in role)
                    and ("PI" not in role)
                    and ("CoInvestigator" not in role)
                    and ("Author" not in role)
                ):
                    contacts_copy[person].append(role)
            # if no acceptable roles were found, remove that author from contributor consideration
            if contacts_copy[person] == []:
                contacts_copy.pop(person)
        return author, author_role, contacts_copy
    # if all creators were found in PublicationInfo/Authors
    else:
        # determine if authors are a consortium
        with open(
            importlib.resources.files("soso.strategies.spase").joinpath(
                "spase-ignoreCreatorSplit.txt"
            ),
            "r",
            encoding="utf-8",
        ) as f:
            do_not_split = f.read()
        # if file is not in list of ones to not have their creators split
        # and there are multiple authors
        if (
            ("; " in author_str)
            or ("., " in author_str)
            or (" and " in author_str)
            or (" & " in author_str)
        ) and file not in do_not_split:
            if ";" in author_str:
                author = author_str.split("; ")
            elif ".," in author_str:
                author = author_str.split("., ")
            elif " and " in author_str:
                author = author_str.split(" and ")
            else:
                author = author_str.split(" & ")
            # fix num of roles
            while len(author_role) < len(author):
                author_role += ["Author"]
            # get rid of extra quotations
            for num, each in enumerate(author):
                if "'" in each:
                    author[num] = each.replace("'", "")
            # iterate over each person in author string
            for person in author:
                matching_contact = None
                index = author.index(person)
                # if first name doesnt have a period, check if it is an initial
                if not person.endswith("."):
                    # if first name is an initial w/o a period, add one
                    grp = re.search(r"[\.\s]{1}[\w]{1}$", person)
                    if grp is not None:
                        person += "."
                # remove 'and' from name
                if "and " in person:
                    person = person.replace("and ", "")
                # continued formatting fixes
                if ", " in person:
                    family_name, _, given_name = person.partition(", ")
                else:
                    given_name, _, family_name = person.partition(". ")
                    given_name += "."
                if "," in given_name:
                    given_name = given_name.replace(",", "")
                # iterate thru contacts to find one that matches the current person
                for contact in contacts_list.keys():
                    if matching_contact is None:
                        initial = None
                        first_name, _, last_name = contact.rpartition(".")
                        first_name, _, initial = first_name.partition(".")
                        *_, first_name = first_name.rpartition("/")
                        if len(first_name) == 1:
                            first_name = first_name[0] + "."
                        # Assumption: if first name initial, middle initial, and last name
                        #   match = same person
                        # remove <f"{first_name[0]}."> in the lines below if this assumption
                        #   is no longer accurate
                        # if no middle name
                        if not initial:
                            if (
                                (f"{first_name[0]}." in person)
                                or (first_name in person)
                            ) and (last_name in person):
                                matching_contact = contact
                        # if middle name is not initialized, check whole string
                        elif len(initial) > 1:
                            if (
                                (
                                    (f"{first_name[0]}." in person)
                                    or (first_name in person)
                                )
                                and (initial in person)
                                and (last_name in person)
                            ):
                                matching_contact = contact
                        else:
                            if (
                                (
                                    (f"{first_name[0]}." in person)
                                    or (first_name in person)
                                )
                                and (f"{initial}." in person)
                                and (last_name in person)
                            ):
                                matching_contact = contact
                # if match is found, add role to author_role and replace role with formatted
                #   person name in contacts_list
                if matching_contact is not None:
                    if author_role[index] != contacts_list[matching_contact]:
                        author_role[index] = [author_role[index]] + contacts_list[
                            matching_contact
                        ]
                    if not initial:
                        contacts_list[matching_contact] = f"{last_name}, {first_name}"
                    elif len(initial) > 1:
                        contacts_list[matching_contact] = (
                            f"{last_name}, {first_name} {initial}"
                        )
                    else:
                        contacts_list[matching_contact] = (
                            f"{last_name}, {first_name} {initial}."
                        )
                author[index] = (f"{family_name}, {given_name}").strip()
        # if there is only one author listed or file has consortium
        else:
            matching_contact = None
            # get rid of extra quotations
            person = author_str.replace('"', "")
            person = author_str.replace("'", "")
            if author_role == ["Author"]:
                # if author is a person (assuming names contain a comma)
                if ", " in person and file not in do_not_split:
                    family_name, _, given_name = person.partition(", ")
                    # also used when there are 3+ comma separated orgs
                    #   listed as authors - not intended (how to fix?)
                    if "," in given_name:
                        given_name = given_name.replace(",", "")
                    # iterate thru contacts to find one that matches the current person
                    contacts_list, author_role = find_match(
                        contacts_list, person, author_role
                    )
                    author[0] = (f"{family_name}, {given_name}").strip()
                else:
                    # handle case when assumption 'names have commas' fails
                    if ". " in person and file not in do_not_split:
                        given_name, _, family_name = person.partition(". ")
                        if " " in family_name:
                            initial, _, family_name = family_name.partition(" ")
                            given_name = given_name + ". " + initial[0] + "."
                        # iterate thru contacts to find one that matches the current person
                        contacts_list, author_role = find_match(
                            contacts_list, person, author_role
                        )
                        author[0] = (f"{family_name}, {given_name}").strip()
                    # author is an organization, so no splitting is needed
                    else:
                        author[0] = person.strip()
    return author, author_role, contacts_list


def verify_type(url: str) -> tuple[bool, bool, dict]:
    """
    Verifies that the link found in AssociationID is to a dataset or journal article and acquires
    more information if a dataset is not hosted by NASA.

    :param url: The link provided as an Associated work/reference for the SPASE record

    :returns: Boolean values signifying if the link is a Dataset/ScholarlyArticle.
                Also a dictionary with additional info about the related Dataset
                acquired from DataCite API if it is not hosted by NASA.
    """
    # tests SPASE records to make sure they are datasets or a journal article
    is_dataset = False
    is_article = False
    non_spase_info = {}
    if url is not None:
        if "spase-metadata.org" in url:
            if "Data" in url:
                is_dataset = True
        # case where url provided is a DOI
        else:
            link = requests.head(url, timeout=30)
            # check to make sure doi resolved to an spase-metadata.org page
            if "spase-metadata.org" in link.headers["location"]:
                if "Data" in link.headers["location"]:
                    is_dataset = True
            # if not, call DataCite API to check resourceTypeGeneral
            #   property associated w the record
            else:
                *_, doi = url.partition("doi.org/")
                # dataciteLink = f"https://api.datacite.org/dois/{doi}"
                # headers = {"accept": "application/vnd.api+json"}
                # response = requests.get(dataciteLink, headers=headers)
                response = requests.get(
                    f"https://api.datacite.org/application/vnd.datacite.datacite+json/{doi}",
                    timeout=30,
                )
                if response.raise_for_status() is None:
                    datacite_dict = json.loads(response.text)
                    if "resourceType" in datacite_dict["types"].keys():
                        if datacite_dict["types"]["resourceType"]:
                            if datacite_dict["types"]["resourceType"] == "Dataset":
                                is_dataset = True
                            elif (
                                datacite_dict["types"]["resourceType"]
                                == "JournalArticle"
                            ):
                                is_article = True
                        else:
                            if (
                                datacite_dict["types"]["resourceTypeGeneral"]
                                == "Dataset"
                            ):
                                is_dataset = True
                            elif (
                                datacite_dict["types"]["resourceTypeGeneral"]
                                == "JournalArticle"
                            ):
                                is_article = True
                    else:
                        if datacite_dict["types"]["resourceTypeGeneral"] == "Dataset":
                            is_dataset = True
                        elif (
                            datacite_dict["types"]["resourceTypeGeneral"]
                            == "JournalArticle"
                        ):
                            is_article = True
                        # if wish to add more checks, simply add more "elif" stmts like above
                        # and adjust provenance/relationship functions to include new type check
                    if is_dataset:
                        # grab name, description, license, and creators
                        non_spase_info["name"] = datacite_dict["titles"][0]["title"]
                        if datacite_dict["descriptions"]:
                            non_spase_info["description"] = datacite_dict[
                                "descriptions"
                            ][0]["description"]
                        else:
                            non_spase_info["description"] = (
                                f"No description currently available for {url}."
                            )
                        if datacite_dict["rightsList"]:
                            non_spase_info["license"] = []
                            for each in datacite_dict["rightsList"]:
                                non_spase_info["license"].append(each["rightsUri"])
                        for creator in datacite_dict["creators"]:
                            if ("givenName" in creator.keys()) and (
                                "familyName" in creator.keys()
                            ):
                                family_name = creator["familyName"]
                                given_name = creator["givenName"]
                            elif ", " in creator["name"]:
                                family_name, _, given_name = creator["name"].partition(
                                    ", "
                                )
                            else:
                                family_name = ""
                                given_name = ""
                            # adjust DataCite format to conform to schema.org format
                            if creator["affiliation"]:
                                non_spase_info["creators"] = person_format(
                                    "creator",
                                    "",
                                    creator["name"],
                                    given_name,
                                    family_name,
                                    creator["affiliation"]["name"],
                                )
                            else:
                                non_spase_info["creators"] = person_format(
                                    "creator",
                                    "",
                                    creator["name"],
                                    given_name,
                                    family_name,
                                )

    return is_dataset, is_article, non_spase_info


def get_resource_id(metadata: etree.ElementTree, namespaces: Dict) -> Union[str, None]:
    """
    :param metadata: The SPASE metadata object as an XML tree.
    :param namespaces: The SPASE namespaces used in the form of a dictionary.

    :returns: The ResourceID for the SPASE record.
    """
    root = metadata.getroot()
    desired_root = None
    dataset_id = None
    # pylint: disable=too-many-boolean-expressions
    for elt in root.iter(tag=etree.Element):
        if (
            elt.tag.endswith("NumericalData")
            or elt.tag.endswith("DisplayData")
            or elt.tag.endswith("Observatory")
            or elt.tag.endswith("Instrument")
            or elt.tag.endswith("Person")
            or elt.tag.endswith("Collection")
        ):
            desired_root = elt

    desired_tag = desired_root.tag.split("}")
    spase_location = ".//spase:" + f"{desired_tag[1]}/spase:ResourceID"
    dataset_id = metadata.findtext(spase_location, namespaces=namespaces)
    return dataset_id


def get_measurement_method(
    metadata: etree.ElementTree, namespaces: Dict
) -> Union[List, None]:
    """
    Scrapes all measurementType fields found in the SPASE record and maps them to
    the schema.org property measurementMethod.

    :param metadata: The SPASE metadata object as an XML tree.
    :param namespaces: The SPASE namespaces used in the form of a dictionary.

    :returns: The MeasurementType(s) for the SPASE record.
    """
    # Mapping: schema:measurementMethod = spase:MeasurementType
    # schema:measurementMethod found at https://schema.org/measurementMethod
    measurement_method = []
    desired_root = None
    root = metadata.getroot()
    for elt in root.iter(tag=etree.Element):
        if elt.tag.endswith("NumericalData") or elt.tag.endswith("DisplayData"):
            desired_root = elt
    desired_tag = desired_root.tag.split("}")
    spase_location = ".//spase:" + f"{desired_tag[1]}/spase:MeasurementType"
    all_measures = metadata.findall(spase_location, namespaces=namespaces)
    for item in all_measures:
        # Split string on uppercase characters
        res = re.split(r"(?=[A-Z])", item.text)
        # Remove empty strings and join with space
        pretty_name = " ".join(filter(None, res))

        # most basic entry for measurementMethod
        entry = {
            "@type": "DefinedTerm",
            "inDefinedTermSet": {
                "@id": "https://spase-group.org/data/model/spase-latest/spase-latest_xsd"
                + ".htm#MeasurementType"
            },
            "name": pretty_name,
            "termCode": item.text,
        }

        # if this is the first item added, add additional info for DefinedTermSet
        if all_measures.index(item) == 0:
            entry["inDefinedTermSet"]["@type"] = "DefinedTermSet"
            entry["inDefinedTermSet"]["name"] = "SPASE MeasurementType"
            entry["inDefinedTermSet"]["url"] = (
                "https://spase-group.org/data/model/spase-latest/spase-latest_xsd."
                "htm#MeasurementType"
            )
        measurement_method.append(entry)

    if len(measurement_method) == 0:
        measurement_method = None
    elif len(measurement_method) == 1:
        measurement_method = measurement_method[0]
    return measurement_method


def get_relation(
    desired_root: etree.Element, association: list[str], file="", **kwargs: dict
) -> Union[List[Dict], Dict, None]:
    """
    Scrapes through the SPASE record and returns the AssociationIDs which have the
    given AssociationType. These are formatted as dictionaries and use the verify_type
    function to add the correct type to each entry.

    :param desired_root: The element in the SPASE metadata tree object we are searching from.
    :param association: The AssociationType(s) we are searching for in the SPASE record.
    :param file: The file path of the SPASE record being converted.
    :param **kwargs: Allows for additional parameters to be passed (only to be used for testing).

    :returns: The ID's of other SPASE records related to this one in some way.
    """
    relations = []
    assoc_id = ""
    assoc_type = ""
    relational_records = {}
    if file:
        file = file.replace("\\", "/")
    # iterate thru xml to find desired info
    if desired_root is not None:
        for child in desired_root.iter(tag=etree.Element):
            if child.tag.endswith("Association"):
                target_child = child
                for child in target_child:
                    if child.tag.endswith("AssociationID"):
                        assoc_id = child.text
                    elif child.tag.endswith("AssociationType"):
                        assoc_type = child.text
                for each in association:
                    if assoc_type == each:
                        relations.append(assoc_id)
        if not relations:
            relation = None
        else:
            i = 0
            # try and get DOI instead of SPASE ID
            for record in relations:
                # get home directory
                home_dir = str(Path.home())
                home_dir = home_dir.replace("\\", "/")
                # get current working directory
                cwd = str(Path.cwd()).replace("\\", "/")
                # add SPASE repo that contains related SPASE record to log file
                repo_name, _, _ = record.replace("spase://", "").partition("/")
                update_log(cwd, repo_name, "requiredRepos")
                # format record
                if ("src/soso/strategies/spase/" in file) or kwargs:
                    # being called by test function = change directory to xml file in tests folder
                    *_, file_name = record.rpartition("/")
                    if "src/soso/strategies/spase/" in file:
                        # if called by snapshot creation script
                        if "soso-spase/" in file:
                            record = (
                                f"{home_dir}/soso-spase/"
                                + "tests/data/spase/"
                                + f"spase-{file_name}"
                                + ".xml"
                            )
                        # being called by CI workflow
                        else:
                            abs_path, _, _ = file.partition(
                                "src/soso/strategies/spase/"
                            )
                            record = (
                                f"{abs_path}"
                                + "tests/data/spase/"
                                + f"spase-{file_name}"
                                + ".xml"
                            )
                    # print(record)
                else:
                    record = home_dir + "/" + record.replace("spase://", "") + ".xml"
                record = record.replace("'", "")
                if os.path.isfile(record):
                    test_spase = SPASE(record)
                    url = test_spase.get_url()
                    name = test_spase.get_name()
                    description = test_spase.get_description()
                    spase_license = test_spase.get_license()
                    # to ensure snapshot matches when running in local env
                    # uncomment if creating snapshot
                    # if "soso-spase" in file:
                    #    creators = test_spase.get_creator(
                    #    **{"placeholder": "so that snapshot matches"}
                    #    )
                    # else:
                    creators = test_spase.get_creator()
                    if creators is None:
                        creators = "No creators were found. View record for contacts."
                    relational_records[url] = {
                        "name": name,
                        "description": description,
                        "creators": creators,
                    }
                    if spase_license is not None:
                        relational_records[url]["license"] = spase_license

                else:
                    if os.path.exists(temp_file_path):
                        temp_file.seek(0)
                        if temp_file.read():
                            temp_file.write(f", {record}")
                        else:
                            temp_file.write(f"{record}")
                i += 1
            # add correct type
            if len(relations) > 1:
                relation = []
            # not SPASE records
            if not relational_records:
                for each in relations:
                    if "spase" not in each:
                        # most basic entry into relation
                        entry = {"@id": each, "identifier": each, "url": each}
                        is_dataset, is_article, non_spase_info = verify_type(each)
                        if is_dataset:
                            entry["@type"] = "Dataset"
                            entry["name"] = non_spase_info["name"]
                            entry["description"] = non_spase_info["description"]
                            if "license" in non_spase_info.keys():
                                entry["license"] = non_spase_info["license"]
                            entry["creator"] = non_spase_info["creators"]
                        elif is_article:
                            entry["@type"] = "ScholarlyArticle"
                        if len(relations) > 1:
                            relation.append(entry)
                        else:
                            relation = entry
            else:
                for each in relational_records.keys():
                    # most basic entry into relation
                    entry = {"@id": each, "identifier": each, "url": each}
                    is_dataset, is_article, non_spase_info = verify_type(each)
                    if is_dataset:
                        entry["@type"] = "Dataset"
                        entry["name"] = relational_records[each]["name"]
                        entry["description"] = relational_records[each]["description"]
                        if "license" in relational_records[each].keys():
                            entry["license"] = relational_records[each]["license"]
                        entry["creator"] = relational_records[each]["creators"]
                    elif is_article:
                        entry["@type"] = "ScholarlyArticle"
                    if len(relations) > 1:
                        relation.append(entry)
                    else:
                        relation = entry
    else:
        relation = None
    return relation


def update_log(cwd: str, addition: str, log_file_name: str) -> None:
    """
    Updates a log file with the given addition. Log files currently updated
    using this method are one containing the SPASE repositories needed for the
    metadata conversion to work as intended and another containing all of the
    SPASE records that could not be accessed.

    :param cwd: The current working directory of your workstation.
    :param addition: The addition to the log file, such as the name of the repository
    needed to access the SPASE record or the SPASE record itself.
    """
    if (cwd is not None) and (addition is not None):
        # create test requiredRepos.txt file for testing suite
        if os.path.isfile(f"{cwd}/{log_file_name}.txt"):
            """with open(f"{cwd}/{log_file_name}.txt", "w", encoding="utf-8") as f:
            f.write("This is placeholder text.")"""
            with open(f"{cwd}/{log_file_name}.txt", "r", encoding="utf-8") as f:
                text = f.read()
            if addition not in text:
                with open(f"{cwd}/{log_file_name}.txt", "a", encoding="utf-8") as f:
                    f.write(f"\n{addition}")


def make_trial_start_and_stop(
    temp_covg: Union[str, Dict]
) -> Union[tuple[str, str], None]:
    """
    Creates a test end time for the dataset based on the TemporalDescription found in
    the SPASE record. Returns two sentences describing the start and stop times for use
    in the description(s) for datasets with HAPI links.

    :param temp_covg: The value returned from the get_temporal_coverage function

    :returns: Two sentence descriptions of the start and (newly created) trial stop times
    """
    if temp_covg:
        start_sent = ""
        end_sent = ""
        if isinstance(temp_covg, str):
            start, _, end = temp_covg.partition("/")
        else:
            start, _, end = temp_covg["temporalCoverage"].partition("/")
        # create test end time
        date, _, time_str = start.partition("T")
        time_str = time_str.replace("Z", "")
        if "." in time_str:
            substring2 = time_str.split(".", 1)
            time_str = substring2[0]
        dt_string = date + " " + time_str
        dt_obj = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
        # make test stop time 1 minute after start time
        test_end = dt_obj + timedelta(minutes=1)
        test_end = str(test_end).replace(" ", "T")
        # set test_end as end time if no end time found in record
        if end in ("", ".."):
            end = test_end
        else:
            end_sent = f"Data is available up to {end}. "
        end_sent += f"Use {test_end} as a test end value."
        start_sent = f"Use {start} as default value."
    else:
        start_sent = None
        end_sent = None
    return start_sent, end_sent


def find_match(
    contacts_list: dict, person: str, author_role: list, matching_contact: bool = None
) -> tuple[dict, list]:
    """
    Attempts to find a match in the provided dictionary of contacts (with their roles)
    found in the SPASE record to the given person name. If a match is found, that role
    is added to corresponding entry in the given list of author roles, and, in the
    dictionary of contacts, the role value is replaced with the formatted person name.

    :param contacts_list: The dictionary containing the contacts found in the SPASE record as keys
                            and their roles as values.
    :param person: The string containing the name of the person you wish to find a match for.
    :param author_role: The list of author roles.
    :param matching_contact: The string containing the contact from the contacts_list parameter
                                that matches the person parameter

    :returns: The updated versions of the given dictionary of contacts and list of author roles.
    """
    if contacts_list and person and author_role:
        for contact in contacts_list.keys():
            if matching_contact is None:
                initial = None
                first_name, _, last_name = contact.rpartition(".")
                first_name, _, initial = first_name.partition(".")
                *_, first_name = first_name.rpartition("/")
                if len(first_name) == 1:
                    first_name = first_name[0] + "."
                # Assumption: if first name initial, middle initial, and last name
                #   match = same person
                # remove <f"{first_name[0]}."> in the lines below if this assumption
                #   is no longer accurate
                # if no middle name
                if not initial:
                    if ((f"{first_name[0]}." in person) or (first_name in person)) and (
                        last_name in person
                    ):
                        matching_contact = contact
                # if middle name is not initialized, check whole string
                elif len(initial) > 1:
                    if (
                        ((f"{first_name[0]}." in person) or (first_name in person))
                        and (initial in person)
                        and (last_name in person)
                    ):
                        matching_contact = contact
                else:
                    if (
                        ((f"{first_name[0]}." in person) or (first_name in person))
                        and (f"{initial}." in person)
                        and (last_name in person)
                    ):
                        matching_contact = contact
        # if match is found, add role to author_role and replace role with
        #   formatted person name in contacts_list
        if matching_contact is not None:
            if author_role[0] != contacts_list[matching_contact]:
                author_role[0] = [author_role[0]] + contacts_list[matching_contact]
            if not initial:
                contacts_list[matching_contact] = f"{last_name}, {first_name}"
            elif len(initial) > 1:
                contacts_list[matching_contact] = f"{last_name}, {first_name} {initial}"
            else:
                contacts_list[matching_contact] = (
                    f"{last_name}, {first_name} {initial}."
                )
    return contacts_list, author_role


def get_problematic_records() -> str:
    """Saves input from various functions to the temp file containing problematic
    records found during script, closes the file, and returns the content."""
    problematic_records = ""
    if os.path.exists(temp_file_path):
        temp_file.seek(0)
        problematic_records = temp_file.read()
        # print("Records are: " + problematic_records)
        temp_file.close()  # Close and remove the temp file object
    return problematic_records
