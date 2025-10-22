"""Core validation functions."""

import urllib.error
from importlib import resources
import pathlib
import warnings
import pyshacl.validate


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


def get_shacl_file_path() -> pathlib.Path:
    """Return the SHACL shape file path for the SOSO dataset graph.

    The shape file is for the current release version of the SOSO dataset
    graph.

    :returns: Path to the SHACL shape file.
    """
    file_path = resources.files("soso.data").joinpath("soso_common_v1.2.3.ttl")
    return file_path
