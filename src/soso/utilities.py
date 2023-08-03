"""Utilities"""

import urllib.error
import warnings
import pyshacl.validate
from soso.datasets import get_soso_common


def validate(graph):
    """Validate a graph against the SOSO shape.

    Parameters
    ----------
    graph : str
        File path of the graph JSON-LD to validate.

    Returns
    -------
    bool
        Whether the graph conforms to the SOSO shape. If no internet connection
        is available, None is returned.

    Notes
    -----
    This function wraps `pyshacl.validate`, which requires an internet
    connection. Without it, this function will return None and a warning will
    be raised. The warning is a bit cryptic: `nodename nor servname provided,
    or not known`.
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
