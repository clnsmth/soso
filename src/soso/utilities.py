"""Utilities"""

import mimetypes
import re
import urllib.error
from urllib.parse import urlparse
from importlib import resources
from numbers import Number
from json import dumps
import pathlib
from typing import Any, Union
import warnings
import pyshacl.validate
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


def get_shacl_file_path() -> pathlib.Path:
    """Return the SHACL shape file path for the SOSO dataset graph.

    The shape file is for the current release version of the SOSO dataset
    graph.

    :returns: Path to the SHACL shape file.
    """
    file_path = resources.files("soso.data").joinpath("soso_common_v1.2.3.ttl")
    return file_path


def get_sssom_file_path(strategy: str) -> pathlib.Path:
    """Return the SSSOM file path for the specified strategy.

    :param strategy: Metadata strategy. Can be: EML.

    :returns: File path.
    """
    file_name = "soso-" + str.lower(strategy) + ".sssom.tsv"
    file_path = resources.files("soso.data").joinpath(file_name)
    return file_path


def get_example_metadata_file_path(strategy: str) -> pathlib.Path:
    """Return the file path of an example metadata file.

    :param strategy: Metadata strategy. Can be: EML, SPASE.

    :returns: File path.
    """
    if strategy.lower() == "eml":
        file_path = resources.files("soso.data").joinpath("eml.xml")
    elif strategy.lower() == "spase":
        file_path = resources.files("soso.data").joinpath("spase.xml")
    else:
        raise ValueError("Invalid choice!")
    return file_path


def get_empty_metadata_file_path(strategy: str) -> pathlib.Path:
    """
    :param strategy: Metadata strategy. Can be: EML.

    :returns:   File path of an empty metadata file.
    """
    if strategy.lower() == "eml":
        file_path = resources.files("soso.data").joinpath("eml_empty.xml")
    elif strategy.lower() == "spase":
        file_path = resources.files("soso.data").joinpath("spase_empty.xml")
    else:
        raise ValueError("Invalid choice!")
    return file_path


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

        # An HTTPS prefixed invalid DOI will return an HTML document that is
        # not a citation. This is an issue in the content negotiation defined
        # at: https://citation.crosscite.org/docs.html#sec-4-1.
        if is_html(response.text):
            return None

        return response.text
    except requests.exceptions.RequestException as citation_error:
        print(f"An error occurred while generating the citation: " f"{citation_error}")
        return None


def limit_to_5000_characters(text: str) -> str:
    """
    :param text: The text to limit to 5000 characters.

    :returns:   The text limited to 5000 characters as per Google
        recommendations for textual properties.
    """
    if len(text) > 5000:
        return text[:5000]
    return text


def as_numeric(value: Any) -> Union[None, int, float]:
    """
    :param value: The value to convert to a numeric value.

    :returns: A numeric value.
    """
    if not value:
        return None
    try:
        numeric_value = int(value)
    except ValueError:
        try:
            numeric_value = float(value)
        except ValueError:
            numeric_value = None
    return numeric_value


def is_url(text: str) -> bool:
    """
    :param text: The string to be checked.
    :returns: True if the string is likely a URL, False otherwise.
    :note: A string is considered a URL if it has scheme and network
        location values.
    """
    res = urlparse(text)
    if len(res.scheme) > 0 and len(res.netloc) > 0:
        return True
    return False


def is_html(text: str) -> bool:
    """
    :param text: The string to be checked.
    :returns: True if the string is likely an HTML document, False otherwise.
    """
    basic_html_pattern = r"<!DOCTYPE\s+html>|<html.*?>.*</html>"
    return bool(re.search(basic_html_pattern, text, re.DOTALL | re.IGNORECASE))


# This will hold our dedicated MimeTypes instance, created only once.
_CUSTOM_MIMETYPES_INSTANCE = None


# pylint: disable=global-statement
def _get_custom_mimetypes_instance():
    """
    Creates and returns a sandboxed MimeTypes instance loaded ONLY
    with our custom, bundled mime.types file. Returns None if the
    file can't be found.
    """
    global _CUSTOM_MIMETYPES_INSTANCE
    if _CUSTOM_MIMETYPES_INSTANCE is not None:
        return _CUSTOM_MIMETYPES_INSTANCE

    try:
        mime_file_path = resources.files("soso.data").joinpath("mime.types")
        # Create a DEDICATED instance, don't touch the global one.
        _CUSTOM_MIMETYPES_INSTANCE = mimetypes.MimeTypes(
            filenames=[str(mime_file_path)]
        )
        return _CUSTOM_MIMETYPES_INSTANCE
    except (ModuleNotFoundError, FileNotFoundError):
        warnings.warn(
            "Custom 'mime.types' file not found. Fallback to system "
            "defaults will be used for all lookups.",
            UserWarning,
        )
        # Return a dummy empty instance to prevent trying again.
        _CUSTOM_MIMETYPES_INSTANCE = mimetypes.MimeTypes()
        return _CUSTOM_MIMETYPES_INSTANCE


def guess_mime_type_with_fallback(filename: str) -> str | None:
    """
    Guesses a MIME type by first checking our consistent, bundled database.
    If no match is found, it falls back to the operating system's default.

    :param filename: The file name or path to guess the MIME type for.
    :returns: The guessed MIME type as a string, or None if no type could be
        determined.
    """
    # Step 1: Try our custom, consistent database first.
    custom_guesser = _get_custom_mimetypes_instance()
    custom_guess, _ = custom_guesser.guess_type(filename)

    if custom_guess is not None:
        return custom_guess

    # Step 2: If our custom database has no opinion, fall back to the system.
    # The global `mimetypes.guess_type` uses the system's configuration.
    warnings.warn(
        f"'{filename}' not found in custom DB, falling back to system guess.",
        UserWarning,
    )
    system_guess, _ = mimetypes.guess_type(filename)
    return system_guess
