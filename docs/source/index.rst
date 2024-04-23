Welcome to `soso`
==============================================

Release v\ |version|. (:ref:`Installation <quickstart>`)

.. image:: https://www.repostatus.org/badges/latest/wip.svg
    :target: https://www.repostatus.org/#wip
    :alt: Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.

.. image:: https://github.com/clnsmth/soso/actions/workflows/ci-cd.yml/badge.svg
    :target: https://github.com/clnsmth/soso/actions/workflows/ci-cd.yml
    :alt: CI/CD pipeline status

.. image:: https://codecov.io/gh/clnsmth/soso/branch/convert/graph/badge.svg
    :target: https://app.codecov.io/github/clnsmth/soso?branch=convert
    :alt: Code coverage status

For creating `Science On Schema.Org`_ (SOSO) markup in dataset landing pages to improve data discovery through search engines.

.. _Science On Schema.Org: https://github.com/ESIPFed/science-on-schema.org

-------------------

To convert a metadata record, specify the file path and conversion strategy (standard).

    >>> from soso.main import convert
    >>> r = convert(file='metadata.xml', strategy='eml')
    >>> r
    '{"@context": {"@vocab": "https://schema.org/", "prov": "http://www. ...}'

Not all SOSO properties are present in the metadata. To include these, use method overriding to process custom arguments.

    >>> from soso.strategies.eml import EML
    >>> def get_url(self):
    ...     return self.kwargs['url']
    >>> EML.get_url = get_url
    >>> r = convert(file='metadata.xml', strategy='eml', url='https://www.sample-data-repository.org/dataset/472032')
    >>> r
    '{"@context": {"@vocab": "https://schema.org/", "prov": "http://www. ...}'

Features
--------

* Convert common metadata standards to SOSO.
* Customize for unique use cases.


The User Guide
--------------

This part of the documentation begins with some background information about soso, then focuses on step-by-step instructions for getting the most out of it.

.. toctree::
   :maxdepth: 2

   user/quickstart
   user/advanced
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
   dev/design
   dev/conduct

The Maintainer Guide
--------------------

If you are a project maintainer, this part of the documentation is for
you.

.. toctree::
   :maxdepth: 3

   dev/maintaining
