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


Unmappable Properties
---------------------

Some SOSO properties may not be derived from metadata records alone. In such cases, additional information can be provided via `kwargs`, where keys match the property name, and values are the property value.

For example, the `url` property representing the landing page URL does not exist in an EML metadata record. But this information is known to the repository hosting the dataset.

    >>> kwargs = {'url': 'https://sample-data-repository.org/dataset/472032'}
    >>> r = convert(file='metadata.xml', strategy='EML', **kwargs)
    >>> r
    '{"@context": {"@vocab": "https://schema.org/", "prov": "http://www. ...}'

It's worth noting that this `kwargs` approach is not limited to supplying unmappable properties; it can be utilized to override any top-level SOSO property.

Unmappable properties are listed in the strategy documentation.
