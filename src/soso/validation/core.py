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


def resolve_shacl_shape(shacl_shape: str = None) -> str:
    """Resolve the SHACL shape to a usable file path.

    If `shacl_shape` is a valid file path it is returned. If it matches a bundled
    resource name, the corresponding package resource is returned. If
    `shacl_shape` is `None`, the default bundled file name (`soso_common_v1.2.3.ttl`)
    is used.

    :param shacl_shape: File path or bundled resource name.
    :returns: Resolved file path to the SHACL shape.
    :returns: Path to the SHACL shape file.
    """
    default_shape = "soso_common_v1.2.3.ttl"
    if shacl_shape is None:
        shacl_shape = default_shape

    shape_path = pathlib.Path(shacl_shape)
    if shape_path.exists():
        # It's a local file path
        return str(shape_path)
    # Try to resolve as a bundled resource
    try:
        resource = resources.files("soso.data").joinpath(shacl_shape)
        # Optionally check existence
        if hasattr(resource, "is_file") and not resource.is_file():
            raise FileNotFoundError
        return str(resource)
    except Exception as exc:
        raise FileNotFoundError(
            f"SHACL shape not found as file or bundled resource: {shacl_shape}"
        ) from exc
