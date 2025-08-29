# soso

[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)
![example workflow](https://github.com/clnsmth/soso/actions/workflows/ci-cd.yml/badge.svg)
[![codecov](https://codecov.io/github/clnsmth/soso/graph/badge.svg?token=2J4MNIXCTD)](https://codecov.io/github/clnsmth/soso)
[![DOI](https://zenodo.org/badge/666558073.svg)](https://zenodo.org/badge/latestdoi/666558073)
![PyPI - Version](https://img.shields.io/pypi/v/soso?color=blue)

For converting dataset metadata into [Science On Schema.Org](https://github.com/ESIPFed/science-on-schema.org) markup.

## Quick Start

### Installation

Install from PyPI:

    $ pip install soso

### Metadata Conversion

To perform a conversion, specify the file path of the metadata and the desired conversion strategy. Each metadata standard corresponds to a specific strategy.

    >>> from soso.main import convert
    >>> r = convert(file='metadata.xml', strategy='EML')
    >>> r
    '{"@context": {"@vocab": "https://schema.org/", "prov": "http://www. ...}'

For a list of available strategies, please refer to the documentation of the `convert` function.

### Adding Unmappable Properties

Some SOSO properties may not be derived from metadata records alone. In such cases, additional information can be provided via `kwargs`, where keys match the top level property name, and values are the property value.

For example, the `url` property representing the landing page URL does not exist in an EML metadata record. But this information is known to the repository hosting the dataset.

    >>> kwargs = {'url': 'https://sample-data-repository.org/dataset/472032'}
    >>> r = convert(file='metadata.xml', strategy='EML', **kwargs)
    >>> r
    '{"@context": {"@vocab": "https://schema.org/", "prov": "http://www. ...}'

It's worth noting that this `kwargs` approach is not limited to supplying unmappable properties; it can be utilized to override any top-level SOSO property.

Unmappable properties are listed in the strategy documentation.

### Other Modifications

Any additional modifications can be made to the resulting JSON-LD string before it is used. Simply parse the string into a Python dictionary, make the necessary changes, and then convert it back to a JSON-LD string.

### Shared Conversion Scripts

When data repositories use a common metadata standard and adopt shared infrastructure, such as databases containing ancillary information, a shared conversion script can be used. These scripts reliably reference the shared infrastructure to create a richer SOSO record by incorporating this additional information. Below is a list of available scripts and their usage examples:

- [SPASE-schema.org Conversion Script](https://soso.readthedocs.io/en/latest/user/examples/spase-HowToConvert.html)

## API Reference and User Guide

The API reference and user guide are available on [Read the Docs](https://soso.readthedocs.io).

## Code of Conduct

In the spirit of collaboration, we emphasize the importance of maintaining a respectful and inclusive environment.

See the [Code of Conduct](https://soso.readthedocs.io/en/latest/dev/conduct.html#conduct) for details.

