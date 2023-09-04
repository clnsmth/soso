"""Utilities"""

import urllib.error
from importlib import resources
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
