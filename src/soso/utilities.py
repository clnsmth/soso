"""Utilities"""

import urllib.error
from importlib import resources
from numbers import Number
from collections import deque
import warnings
import pyshacl.validate
import pandas as pd


def validate(graph):
    """Validate a graph against the SOSO dataset SHACL shape.

    Parameters
    ----------
    graph : str
        File path of the JSON-LD graph to validate.

    Returns
    -------
    bool
        Whether the graph conforms to the SOSO shape. If no internet connection
        is available, None is returned.

    Notes
    -----
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


def get_shacl_file_path():
    """Return the SHACL shape file path for the SOSO dataset graph.

    The shape file is for the current release version of the SOSO dataset
    graph.

    Returns
    -------
    PosixPath
        Path to the SHACL shape file.
    """
    file_path = resources.files("soso.data").joinpath("soso_common_v1.2.3.ttl")
    return file_path


def get_sssom_file_path(strategy):
    """Return the SSSOM file path for the specified strategy.

    Parameters
    ----------
    strategy : str
        Metadata strategy. Can be: EML.

    Returns
    -------
    PosixPath
        File path.
    """
    file_name = "soso-" + str.lower(strategy) + ".sssom.tsv"
    file_path = resources.files("soso.data").joinpath(file_name)
    return file_path


def get_example_metadata_file_path(strategy):
    """Return the file path of an example metadata file.

    Parameters
    ----------
    strategy : str
        Metadata strategy. Can be: EML.

    Returns
    -------
    PosixPath
        File path.
    """
    if strategy.lower() == "eml":
        file_path = resources.files("soso.data").joinpath("eml.xml")
    else:
        raise ValueError("Invalid choice!")
    return file_path


def read_sssom(strategy):
    """Return the SSSOM for the specified strategy.

    Parameters
    ----------
    strategy : str
        Metadata strategy. Can be: EML.

    Returns
    -------
    DataFrame
        Pandas dataframe.
    """
    sssom_file_path = get_sssom_file_path(strategy)
    sssom = pd.read_csv(sssom_file_path, delimiter="\t")
    return sssom


def is_empty(value):
    """
    This function checks if a value is considered empty/null in JSON-LD
    context.

    Parameters
    ----------
    value: Any
        The value to check.

    Returns
    -------
    bool
        True if the value is empty/null, False otherwise.
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


def clean_jsonld(data):
    """
    This function recursively cleans empty/null values from a JSON-LD document,
    starting from the deepest level and working backwards.

    Parameters
    ----------
    data: Any
        The JSON-LD document represented as a dictionary.

    Returns
    -------
    Any
        A new dictionary with all empty/null values removed.
    """
    if isinstance(data, dict):
        # Handle dictionaries
        cleaned_data = {}
        for k, v in data.items():
            cleaned_value = clean_jsonld(v)
            if not is_empty(cleaned_value):
                cleaned_data[k] = cleaned_value
        # if len(data) == 0:  # NOTE change from original
        #     cleaned_data = None  # NOTE change from original
        # if isinstance(data, dict) and (len(data) == 1 and "@type" in data):  # NOTE change from original
        #     cleaned_data = None  # NOTE change from original
        return cleaned_data
    elif isinstance(data, list):
        # Handle lists
        # if len(data) == 0:  # NOTE change from original
        #     return None  # NOTE change from original
        return [clean_jsonld(item) for item in data if not is_empty(item)]
    else:
        # Return non-empty values as-is
        return data


def clean_jsonld_x2(data):
    """Wrapper to clean_jsonld to handle outtermore layer to return None if empty."""
    # recursive cleaning
    cleaned_data = clean_jsonld(data)

    # atomic cleaning
    if isinstance(cleaned_data, (None.__class__, bool, Number)):
        return cleaned_data
    if len(cleaned_data) == 0:
        return None
    if isinstance(data, dict) and (
        len(data) == 1 and "@type" in data
    ):  # NOTE change from original
        cleaned_data = None  # NOTE change from original
    if len(data) == 0:  # NOTE change from original
        return None  # NOTE change from original
    return cleaned_data
