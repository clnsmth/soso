"""Utilities"""

import urllib.error
from importlib import resources
from numbers import Number
from json import dumps
import pathlib
from typing import Any, Union
import warnings
import pyshacl.validate
import pandas as pd
import requests


def validate(graph: str) -> bool:
    """Validate a graph against the SOSO dataset SHACL shape.

    :param graph: File path of the JSON-LD graph to validate.

    :returns:   Whether the graph conforms to the SOSO shape. If no internet
                connection is available, None is returned.

    Notes:
        This function wraps `pyshacl.validate`, which requires an internet
        connection.
    """
    try:
        res = pyshacl.validate(
            data_graph=graph,
            shacl_graph=str(get_shacl_file_path()),
            data_graph_format="json-ld",
            shacl_graph_format="turtle",
        )
        conforms = res[0]
        results_text = res[2]
        if not conforms:
            warnings.warn(results_text)
        return conforms
    except urllib.error.URLError as errors:
        warnings.warn(errors)
        return None


def get_shacl_file_path() -> pathlib.PosixPath:
    """Return the SHACL shape file path for the SOSO dataset graph.

    The shape file is for the current release version of the SOSO dataset
    graph.

    :returns: Path to the SHACL shape file.
    """
    file_path = resources.files("soso.data").joinpath("soso_common_v1.2.3.ttl")
    return file_path


def get_sssom_file_path(strategy: str) -> pathlib.PosixPath:
    """Return the SSSOM file path for the specified strategy.

    :param strategy: Metadata strategy. Can be: EML.

    :returns: File path.
    """
    file_name = "soso-" + str.lower(strategy) + ".sssom.tsv"
    file_path = resources.files("soso.data").joinpath(file_name)
    return file_path


def get_example_metadata_file_path(strategy: str) -> pathlib.PosixPath:
    """Return the file path of an example metadata file.

    :param strategy: Metadata strategy. Can be: EML.

    :returns: File path.
    """
    if strategy.lower() == "eml":
        file_path = resources.files("soso.data").joinpath("eml.xml")
    else:
        raise ValueError("Invalid choice!")
    return file_path


def read_sssom(strategy: str) -> pd.DataFrame:
    """Return the SSSOM for the specified strategy.

    :param strategy: Metadata strategy. Can be: EML.

    :returns: The SSSOM table.
    """
    sssom_file_path = get_sssom_file_path(strategy)
    sssom = pd.read_csv(sssom_file_path, delimiter="\t")
    return sssom


def delete_null_values(res: Any) -> Any:
    """Remove null values from results returned by strategy methods.

    :param res: The results to clean.

    :returns:   The results with all null values removed. None is returned if
                all values are null.

    Notes:
        This function is to help developers of strategy methods clean their
        results before returning them to the user, to ensure that the results
        are free of meaningless values.

        Null values are defined as follows:
            - None
            - An empty string
            - An empty list
            - An empty dictionary
            - A dictionary with only one key, "@type"
    """

    def is_null(value: Any) -> bool:
        """
        :param value: The value to check for "nullness".

        :returns: Whether the value is null.
        """
        return (
            value is None
            or (isinstance(value, str) and not value)
            or (isinstance(value, list) and not value)
            or (
                isinstance(value, dict)
                and (not value or (len(value) == 1 and "@type" in value))
            )
        )

    def deep_clean(data: Any) -> Any:
        """
        :param data: The results to clean.

        :returns:   The input data with all null values removed by way of
                    recursive cleaning.
        """
        if isinstance(data, dict):
            # Handle dictionaries
            cleaned_data = {}
            for key, value in data.items():
                cleaned_value = deep_clean(value)
                if not is_null(cleaned_value):
                    cleaned_data[key] = cleaned_value
            return cleaned_data
        if isinstance(data, list):
            # Handle lists
            return [deep_clean(item) for item in data if not is_null(item)]
        # Return non-empty values as-is
        return data

    # The cleaning is done in two passes. The first pass is a recursive
    # depth-first cleaning, and the second pass is a follow-up cleaning to
    # remove any null values resulting from the recursive cleaning. The
    # recursive cleaning uses a depth-first search to remove null values from
    # nested dictionaries and lists.

    # Recursive cleaning
    cleaned_data = deep_clean(res)

    # Follow-up cleaning, to remove any null values resulting from the
    # recursive cleaning
    if isinstance(cleaned_data, (None.__class__, bool, Number)):
        return cleaned_data
    if len(cleaned_data) == 0:
        return None
    if isinstance(res, dict) and (len(res) == 1 and "@type" in res):
        cleaned_data = None
    if len(res) == 0:
        return None
    return cleaned_data


def delete_unused_vocabularies(graph: dict) -> dict:
    """Delete unused vocabularies from the top level JSON-LD @context. This
    function is to help clean the graph created by `main.convert` before
    returning it to the user.

    :param graph: The JSON-LD graph.

    :returns:   The JSON-LD graph, with unused vocabularies removed from the
                top level @context.
    """
    # Create a copy of the graph for comparison
    graph_copy = graph.copy()
    del graph_copy["@context"]
    graph_copy = dumps(graph_copy)
    # Remove vocabularies whose keys are not in the graph, @vocab is preserved
    for key in list(graph["@context"]):
        if (
            key != "@vocab" and key + ":" not in graph_copy
        ):  # ":" is added to avoid partial matches
            del graph["@context"][key]
    return graph


def generate_citation_from_doi(url: str, style: str, locale: str) -> Union[str, None]:
    """
    :param url: The URL prefixed DOI.
    :param style:   The citation style. For example, "apa". Options are listed
                    `here <https://github.com/citation-style-language/styles>`_.
    :param locale:  The locale. For example, "en-US". Options are listed
                    `here <https://github.com/citation-style-language/locales>`_.

    :returns:   The citation in the specified style and locale. None is
                returned if the DOI is invalid or if the citation could not be
                generated.

    Notes:
        This function supports the DOI registration agencies and methods listed
        `here <https://citation.crosscite.org/docs.html#sec-4>`_.
    """
    try:
        headers = {"Accept": "text/x-bibliography; style=" + style, "locale": locale}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as citation_error:
        print(f"An error occurred while generating the citation: " f"{citation_error}")
        return None
