"""Utilities"""

import urllib.error
from importlib import resources
import warnings
import pyshacl.validate
from soso.utilities import get_soso_common


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
            shacl_graph=str(get_soso_common()),
            data_graph_format="json-ld",
            shacl_graph_format="turtle",
        )
        conforms = res[0]
        results_text = res[2]
        if not conforms:
            warnings.warn(results_text)
        return conforms
    except urllib.error.URLError as e:
        warnings.warn(e)
        return None


def get_soso_common():
    """Return the path to the SHACL shape file for the SOSO dataset graph.

    The shape file is for the current release version of the SOSO dataset
    graph.

    Returns
    -------
    str
        Path to the SHACL shape file.
    """
    with resources.path("soso.data", "soso_common_v1.2.3.ttl") as f:
        return f
