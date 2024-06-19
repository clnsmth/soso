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
