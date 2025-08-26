soso
====

Release v\ |version|. (:ref:`Installation <quickstart>`)

.. image:: https://www.repostatus.org/badges/latest/wip.svg
    :target: https://www.repostatus.org/#wip
    :alt: Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.

.. image:: https://github.com/clnsmth/soso/actions/workflows/ci-cd.yml/badge.svg
    :target: https://github.com/clnsmth/soso/actions/workflows/ci-cd.yml
    :alt: CI/CD pipeline status

.. image:: https://codecov.io/github/clnsmth/soso/graph/badge.svg?token=2J4MNIXCTD
    :target: https://codecov.io/github/clnsmth/soso
    :alt: Code coverage status

.. image:: https://zenodo.org/badge/666558073.svg
    :target: https://zenodo.org/badge/latestdoi/666558073
    :alt: Latest Zenodo DOI

For converting dataset metadata into `Science On Schema.Org`_ markup.

.. _Science On Schema.Org: https://github.com/ESIPFed/science-on-schema.org

-------------------

**Metadata Conversion**

To perform a conversion, specify the file path of the metadata and the desired conversion strategy. Each metadata standard corresponds to a specific strategy.

    >>> from soso.main import convert
    >>> r = convert(file='metadata.xml', strategy='EML')
    >>> r
    '{"@context": {"@vocab": "https://schema.org/", "prov": "http://www. ...}'

For a list of available strategies, please refer to the documentation of the `convert` function.

**Adding Unmappable Properties**

Some SOSO properties may not be derived from metadata records alone. In such cases, additional information can be provided via `kwargs`, where keys match the top level property name, and values are the property value.

For example, the `url` property representing the landing page URL does not exist in an EML metadata record. But this information is known to the repository hosting the dataset.

    >>> kwargs = {'url': 'https://sample-data-repository.org/dataset/472032'}
    >>> r = convert(file='metadata.xml', strategy='EML', **kwargs)
    >>> r
    '{"@context": {"@vocab": "https://schema.org/", "prov": "http://www. ...}'

It's worth noting that this `kwargs` approach is not limited to supplying unmappable properties; it can be utilized to override any top-level SOSO property.

Unmappable properties are listed in the strategy documentation.

**Other Modifications**

Any additional modifications can be made to the resulting JSON-LD string before it is used. Simply parse the string into a Python dictionary, make the necessary changes, and then convert it back to a JSON-LD string.

The User Guide
--------------

This part of the documentation begins with some background information about `soso`, then focuses on step-by-step instructions for getting the most out of it.

.. toctree::
   :maxdepth: 2

   user/quickstart
   user/support

The API Documentation / Guide
-----------------------------

If you are looking for information on a specific function, class, or method,
this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   user/api


The Contributor Guide
---------------------

If you want to contribute to the project, this part of the documentation is for
you.

.. toctree::
   :maxdepth: 3

   dev/contributing

The Maintainer Guide
--------------------

If you are a project maintainer, this part of the documentation is for
you.

.. toctree::
   :maxdepth: 3

   dev/maintaining

Project Design
--------------

The project design documentation provides an overview of the project's
architecture and design decisions.

.. toctree::
   :maxdepth: 3

   dev/design

Code of Conduct
---------------

In the spirit of collaboration, we emphasize the importance of maintaining a respectful and inclusive environment.

See the :ref:`Code of Conduct <conduct>` for details.