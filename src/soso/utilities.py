"""Utilities"""

import urllib.error
from importlib import resources
from numbers import Number
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


def rm_null_values(res):
    """
    Remove null values from results returned by strategy methods. This
    function is to help developers of strategy methods clean their results
    before returning them to the user, to ensure that the results are free of
    meaningless values.

    Parameters
    ----------
    res: Any
        The results to clean.

    Returns
    -------
    Any
        The results with all null values removed. None is returned if all
        values are null.
    """

    def is_null(value):
        """
        Parameters
        ----------
        value: Any
            The value to check for "nullness".

        Returns
        -------
        bool
            True if the value is null, False otherwise.
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

    def deep_clean(data):
        """
        Parameters
        ----------
        data: Any
            The results to clean.

        Returns
        -------
        Any
            The input data with all null values removed by way of recursive
            cleaning.
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
