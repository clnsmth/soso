# soso

[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)
![example workflow](https://github.com/clnsmth/soso/actions/workflows/ci-cd.yml/badge.svg)
[![codecov](https://codecov.io/github/clnsmth/soso/graph/badge.svg?token=2J4MNIXCTD)](https://codecov.io/github/clnsmth/soso)

For converting metadata records into [Science-On-Schema.Org](https://github.com/ESIPFed/science-on-schema.org) markup.

## Installation

Currently, `soso` is only available on GitHub.  To install it, you need to have [pip](https://pip.pypa.io/en/stable/installation/) installed. Once pip is installed, you can install `soso` by running the following command in your terminal:

    $ pip install git+https://github.com/clnsmth/soso.git@main

## Metadata Conversion

The primary function is to convert metadata records into SOSO markup. To perform a conversion, specify the file path of the metadata and the desired conversion strategy. Each metadata standard corresponds to a specific strategy.

    >>> from soso.main import convert
    >>> r = convert(file='metadata.xml', strategy='EML')
    >>> r
    '{"@context": {"@vocab": "https://schema.org/", "prov": "http://www. ...}'

Some SOSO properties may not be derived from metadata records alone. In such cases, additional information can be provided via `kwargs`, where keys match the property name, and values are the property value.

For example, the `url` property representing the landing page URL does not exist in an EML metadata record. But this information is known to the repository hosting the dataset.

    >>> kwargs = {'url': 'https://sample-data-repository.org/dataset/472032'}
    >>> r = convert(file='metadata.xml', strategy='EML', **kwargs)
    >>> r
    '{"@context": {"@vocab": "https://schema.org/", "prov": "http://www. ...}'

It's worth noting that this `kwargs` approach is not limited to supplying unmappable properties; it can be utilized to override any top-level SOSO property.

Unmappable properties are listed in the strategy documentation.

## API Reference and User Guide

The API reference and user guide are available on [Read the Docs](https://soso.readthedocs.io).

## Code of Conduct

In the spirit of collaboration, we emphasize the importance of maintaining a respectful and inclusive environment.

See the [Code of Conduct](https://soso.readthedocs.io/en/latest/dev/conduct.html#conduct) for details.

