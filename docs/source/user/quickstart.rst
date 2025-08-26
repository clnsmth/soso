.. _quickstart:

Quickstart
==========

Welcome to the Quickstart guide! Whether you're a beginner or experienced developer, this guide helps you install the package, set up dependencies, and explore core functionalities.

Installation
------------

Currently, `soso` is only available on GitHub.  To install it, you need to have `pip <https://pip.pypa.io/en/stable/installation/>`_ installed.

Once pip is installed, you can install `soso` by running the following command in your terminal::

    $ pip install git+https://github.com/clnsmth/soso.git@main

For the latest development version::

    $ pip install git+https://github.com/clnsmth/soso.git@development


Metadata Conversion
-------------------

To perform a conversion, specify the file path of the metadata and the desired conversion strategy. Each metadata standard corresponds to a specific strategy.

    >>> from soso.main import convert
    >>> r = convert(file='metadata.xml', strategy='EML')
    >>> r
    '{"@context": {"@vocab": "https://schema.org/", "prov": "http://www. ...}'

For a list of available strategies, please refer to the documentation of the `convert` function.


Adding Unmappable Properties
----------------------------

Some SOSO properties may not be derived from metadata records alone. In such cases, additional information can be provided via `kwargs`, where keys match the top level property name, and values are the property value.

For example, the `url` property representing the landing page URL does not exist in an EML metadata record. But this information is known to the repository hosting the dataset.

    >>> kwargs = {'url': 'https://sample-data-repository.org/dataset/472032'}
    >>> r = convert(file='metadata.xml', strategy='EML', **kwargs)
    >>> r
    '{"@context": {"@vocab": "https://schema.org/", "prov": "http://www. ...}'

It's worth noting that this `kwargs` approach is not limited to supplying unmappable properties; it can be utilized to override any top-level SOSO property.

Unmappable properties are listed in the strategy documentation.

Other Modifications
-------------------

Any additional modifications can be made to the resulting JSON-LD string before it is used. Simply parse the string into a Python dictionary, make the necessary changes, and then convert it back to a JSON-LD string.

Wrapping it All Up
------------------

The `soso` package is designed to be both flexible and extensible. By following the examples provided, you can customize the conversion process to meet your specific needs. Below is an example of a wrapper function that incorporates all the customization options.

.. code-block:: python

        from soso.main import convert
        from soso.strategies.eml import EML
        from soso.strategies.eml import get_encoding_format
        from soso.utilities import delete_null_values
        from soso.utilities import generate_citation_from_doi


        def dataset(metadata_file: str, dataset_id: str, doi: str) -> str:
            """Wrapper function for the convert function that adds additional
            properties

            :param metadata_file: The path to the metadata file.
            :param dataset_id: The dataset identifier, assigned by the repository.
            :param doi: The dataset's Digital Object Identifier."""

            # Add properties that can't be derived from the EML record
            url = "https://www.sample-data-repository.org/dataset/" + dataset_id
            version = dataset_id.split(".")[1]
            is_accessible_for_free = True
            citation = generate_citation_from_doi(doi, style="apa", locale="en-US")
            provider = {"@id": "https://www.sample-data-repository.org"}
            publisher = {"@id": "https://www.sample-data-repository.org"}

            # Call convert to process data with additional properties
            additional_properties = {
                "url": url,
                "version": version,
                "isAccessibleForFree": is_accessible_for_free,
                "citation": citation,
                "provider": provider,
                "publisher": publisher
            }
            r = convert(
                file=metadata_file,
                strategy="EML",
                **additional_properties
            )

            return r


If you have any questions or need help, please don't hesitate to reach out.

Notes
-----

**Adding Vocabularies**

The `convert` function only recognizes vocabularies that are specified within its implementation. You can view the source code for more details on these vocabularies. If you add additional vocabularies to a SOSO graph using property overwrites and method overrides, these vocabularies will have to be defined within an embedded context.

**Leverage Partial Property Method Implementations**

Before creating functions for unmappable properties, check for partial implementations that you can build upon and that can save you time. For instance, the `get_subject_of` method in the EML strategy is mostly complete; it only lacks the `contentUrl`.

