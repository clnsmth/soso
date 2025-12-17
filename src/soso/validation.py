"""The validation module."""

import warnings
from importlib import resources
import pathlib
import pyshacl.validate


def validate(data_graph: str, shacl_graph: str = None) -> dict:
    """
    Validate a data graph against a SHACL shape graph.

    This is a simple wrapper around `pyshacl.validate`.

    :param data_graph: The path to the data graph file in JSON-LD format.
    :param shacl_graph: The path to the SHACL shape graph file in Turtle format.
        If shacl_graph is a valid file path,use it. If it matches a known
        resource, resolve from package. If `None`, a default SOSO SHACL shape is
        used. Available package resources include: ``soso_common_v1.2.3.ttl``.

    :returns: A dictionary with validation results, including:
        ``data_graph``: The input data graph path.
        ``shacl_graph``: The resolved SHACL shape graph path.
        ``conforms``: Boolean indicating if the data graph conforms to the SHACL shape.
        ``report``: Full SHACL validation report as text.
    """
    if not shacl_graph:
        shacl_graph = _get_shacl_file_path()
    shape_file = _resolve_shacl_shape(shacl_graph)

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", category=DeprecationWarning, module="rdflib|pyshacl"
        )
        conforms, _, results_text = pyshacl.validate(
            data_graph=data_graph,
            shacl_graph=shape_file,
            data_graph_format="json-ld",
            shacl_graph_format="turtle",
            inference="none",
            debug=False,
        )
        return {
            "data_graph": data_graph,
            "shacl_graph": shape_file,
            "conforms": conforms,
            "report": results_text,
        }


def _get_shacl_file_path() -> pathlib.Path:
    """Return the SHACL shape file path for the SOSO dataset graph.

    The shape file is for the current release version of the SOSO dataset
    graph.

    :returns: Path to the SHACL shape file.
    """
    file_path = resources.files("soso.data").joinpath("soso_common_v1.2.3.ttl")
    return file_path


def _resolve_shacl_shape(shacl_shape: str = None) -> str:
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
