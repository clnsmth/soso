.. _quickstart:

Quickstart
==========

Welcome to the Quickstart guide! Whether you're a beginner or experienced developer, this guide helps you install our package, set up dependencies, and explore core functionalities.

Installation
------------

Currently, `soso` is only available on GitHub.  To install it, you need to have `pip <https://pip.pypa.io/en/stable/installation/>`_ installed.

Once pip is installed, you can install `soso` by running the following command in your terminal::

    $ pip install git+https://github.com/clnsmth/soso.git#egg=soso




Metadata Conversion
-------------------

The primary function is to convert metadata records into SOSO markup. To perform a conversion, specify the file path of the metadata and the desired conversion strategy. Each metadata standard corresponds to a specific strategy.

    >>> from soso.main import convert
    >>> r = convert(file='metadata.xml', strategy='EML')
    >>> r
    '{"@context": {"@vocab": "https://schema.org/", "prov": "http://www. ...}'

For a list of available strategies, please refer to the documentation of the `main.convert` function.


Adding Unmappable Properties
----------------------------

Some SOSO properties may not be derived from metadata records alone. In such cases, additional information can be provided via `kwargs`, where keys match the property name, and values are the property value.

For example, the `url` property representing the landing page URL does not exist in an EML metadata record. But this information is known to the repository hosting the dataset.

    >>> kwargs = {'url': 'https://sample-data-repository.org/dataset/472032'}
    >>> r = convert(file='metadata.xml', strategy='EML', **kwargs)
    >>> r
    '{"@context": {"@vocab": "https://schema.org/", "prov": "http://www. ...}'

Unmappable properties are listed in the strategy documentation.

Overwriting Properties
----------------------

Any top level property of the SOSO graph can be overwritten using `kwargs`, where keys match the property name, and values are the property value.

For example, the `description` property, providing a short summary of a dataset can be overwritten with a new value.

    >>> kwargs = {'description': 'New description of the dataset'}
    >>> r = convert(file='metadata.xml', strategy='EML', **kwargs)
    >>> r
    '{"@context": {"@vocab": "https://schema.org/", "prov": "http://www. ...}'

Overriding Property Methods
---------------------------

In some cases you may wish to change only a part of the return value of a property method. This can be done by overriding the method in the strategy class, with your modifications, and calling the original method with the same arguments.

For example, in the EML standard, there is no built-in way to define the Spatial Reference System (SRS) for spatial coverage. However, if you have this information for a collection of metadata records, you can add it to the `get_spatial_coverage` method.

.. code-block:: python

    # Import the EML strategy
    from soso.strategies.eml import EML

    # Modify the get_spatial_coverage method
    def get_spatial_coverage(self) -> Union[list, None]:
        geo = []
        for item in self.metadata.xpath(".//dataset/coverage/geographicCoverage"):
            object_type = get_spatial_type(item)
            if object_type == "Point":
                geo.append(get_point(item))
            elif object_type == "Box":
                geo.append(get_box(item))
            elif object_type == "Polygon":
                geo.append(get_polygon(item))
        if geo:
            spatial_coverage = {"@type": "Place", "geo": geo}
            # Add Spatial Reference System ---------------------
            spatial_coverage["additionalProperty"] = {
                "@type": "PropertyValue",
                "propertyID": "http://dbpedia.org/resource/Spatial_reference_system",
                "value": "https://spatialreference.org/ref/epsg/wgs-84-nsidc-sea-ice-polar-stereographic-north/",
            }
            # --------------------------------------------------
            return delete_null_values(spatial_coverage)
        return None

    # Override the method in the EML strategy
    EML.get_spatial_coverage = get_spatial_coverage

    # Convert metadata
    r = convert(file='metadata.xml', strategy='EML')

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

            # Modify the get_subject_of method to return the contentUrl
            def get_subject_of(self) -> dict:
                encoding_format = get_encoding_format(self.metadata)
                date_modified = self.get_date_modified()
                if encoding_format and date_modified:
                    subject_of = {
                        "@type": "DataDownload",
                        "name": "EML metadata for dataset",
                        "description": "EML metadata describing the dataset",
                        "encodingFormat": encoding_format,
                        "contentUrl": "https://www.sample-data-repository/metadata/"
                                      + self.file.split("/")[-1],  # Add the contentUrl
                        "dateModified": date_modified,
                    }
                    return delete_null_values(subject_of)
                return None
            EML.get_subject_of = get_subject_of  # Override the method

            # Call the convert function with the additional properties and overriden
            # method
            r = convert(
                file=metadata_file,
                strategy="EML",
                url=url,
                version=version,
                isAccessibleForFree=is_accessible_for_free,
                citation=citation,
                provider=provider,
                publisher=publisher,
            )

            return r


If you have any questions or need help, please don't hesitate to reach out to us.

Notes
-----

**Adding Vocabularies**

The `main.convert` function only recognizes vocabularies that are specified within its implementation. You can view the source code for more details on these vocabularies. If you add additional vocabularies to a SOSO graph using property overwrites and method overrides, these vocabularies will have to be defined within an embedded context.

**Leverage Partial Property Method Implementations**

Before creating methods for unmappable properties, check for partial implementations that you can build upon and that can save you time. For instance, the `get_subject_of` method in the EML strategy is mostly complete; it only lacks the `contentUrl`.

