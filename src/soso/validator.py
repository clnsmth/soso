"""For validation related operations."""

import warnings
import pyshacl.validate
from soso.datasets import get_soso_common


def validate(graph):
    """Validate a graph against the SOSO shape

    Parameters
    ----------
    graph : str
        File path of the graph JSON-LD to validate.

    Returns
    -------
    bool
        Whether the graph conforms to the SOSO shape.
    """
    res = pyshacl.validate(
        data_graph=graph,
        shacl_graph=str(get_soso_common()),
        data_graph_format="json-ld",
        shacl_graph_format="turtle",
    )
    conforms, results_graph, results_text = res
    if not conforms:
        warnings.warn(results_text)
    return conforms
