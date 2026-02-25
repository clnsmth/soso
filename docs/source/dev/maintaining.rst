.. _maintaining:

Maintainers Guide
=================

Many thanks for your help maintaining our project! Without your contribution, development would be considerably slower and the user community left waiting longer.

This document complements the `Contributor's Guide <contributing.html>`_ by providing additional steps for integrating contributions into the project's code base. As a maintainer, you are also a contributor, so please use the contributor guide when making changes in order to keep the development process open and consistent (note :ref:`developing-features-as-a-maintainer`).

Be Courteous
------------

Sometimes we need to meet contributors halfway. This means more work on our part but for benefit of the project and community. Please be courteous and patient.

If you are unable to respond fully to a pull request or issue in a timely manner, please let the contributor know that you will get to it as soon as you can.

Pull Request Review
-------------------

Pull request review facilitates refinement of a contribution before it's incorporated into the project. The goals are to ensure the contribution is consistent with the project's design, is well-documented, and is well-tested. We are not looking for perfection, but rather that the contribution does what it is intended to do.

*Though pull request review is required by the project's GitHub branch protection rules, maintainers are allowed to bypass review. Having said this, we generally encourage review in all cases.*

Here are steps to help with your pull request review:

1. Start a GitHub review on the pull request.
2. Check that the :ref:`ci-workflow` passes. Even if successful, check the workflow run logs for Pylint related messages. Though not required, we recommend these messages be addressed.
3. New features or bug-fixes should include tests demonstrating the change.
4. Review the diffs of code and related documentation.
5. Check for compliance with our :ref:`commit-messages` style.
6. Submit the review.

When a pull request passes review, it is ready to be merged into the `main` branch.

Git and GitHub
--------------

We use a combination of git and GitHub features to version control and manage various aspects of our project. Generally, we prefer small, incremental changes that are easy to review and maintain.

Branch Management
~~~~~~~~~~~~~~~~~

The `main` branch is the releasable state. New work happens on `feature` branches and is rebased and merged into `main` via pull requests. Releases are cut from `main` using the :ref:`cd-workflow`.

.. _feature-branches:

Feature Branches
^^^^^^^^^^^^^^^^

Any sort of change, including new features, documentation, refactors, and fixes, should be done on a `feature branch` to facilitate iterative collaboration. It can be helpful when feature branch names reference the issue and describes the feature, for example, ``30-release-workflow``.

Releases
^^^^^^^^

When it's time to create a new release, a project maintainer with repository write access, will manually dispatch the :ref:`cd-workflow`, which will run a series of automated tasks.

Branch Protection Rules
~~~~~~~~~~~~~~~~~~~~~~~

GitHub branch protection rules are used to help ensure the integrity of the codebase. The following rules are enforced on the `main` branch:

* Require a pull request approval before merging
* Require status checks to pass before merging
* Require branches to be up to date before merging
* Require conversation resolution before merging
* Require linear history

*The only protection rule maintainers are allowed to ignore is the "pull request approval" requirement. Having said this, we generally encourage review in all cases.*

Secrets
~~~~~~~

A GitHub repository secret, containing the personal access token of one of the maintainers with write access, is required for the :ref:`cd-workflow` to complete. This token should be added to the project's repository secrets with the name ``RELEASE_TOKEN``. This authentication is used by `Python Semantic Release`_ to commit changes created during the release proces to the `main` branch.

.. _Python Semantic Release: https://python-semantic-release.readthedocs.io/en/latest/

Workflows
~~~~~~~~~

GitHub Actions are used for continuous integration and delivery.

.. _ci-workflow:

CI Workflow
^^^^^^^^^^^

The CI workflow is run on each pull request and push to `main` branch. It performs the following steps:

1. Formats code in *src/* and *tests/* using `Black`_. This check is strictly enforced and will fail the workflow.
2. Analyzes code in *src/* and *tests/* using the project's `Pylint`_ configuration (see :ref:`code-format-and-analysis`). This check is not strictly enforced and will not fail the workflow. However, generally, Pylint recommendations should be followed.
3. Runs tests in *tests/* using `Pytest`_. This check is strictly enforced and will fail the workflow.
4. Builds the documentation (see :ref:`documentation-contributions`). This check is strictly enforced and will fail the workflow.

.. _Black: https://black.readthedocs.io/en/stable/
.. _Pylint: https://pylint.pycqa.org/en/latest/
.. _Pytest: https://docs.pytest.org/en/latest/

.. _cd-workflow:

CD Workflow
^^^^^^^^^^^

The CD workflow is run via workflow dispatch for releases. It performs the following steps:

1. Runs `Python Semantic Release`_ to build the changelog, convert the distributions, bump the version number, and tag the release.
2. Releases the package to PyPI.

.. _developing-features-as-a-maintainer:

Developing Features as a Maintainer
-----------------------------------

As a maintainer, when developing a new feature, you don't have to fork the project repository to your personal GitHub, and submit pull requests via that route. Rather, you may create a `feature branch` in the project's remote repository, and submit a pull request from there.

Dependency and Environment Management
-------------------------------------

This project uses `Poetry`_ to manage dependencies for development and distribution. Poetry keeps track of necessary packages and their versions, ensuring a consistent development environment.

For those who prefer using `Conda`_ for environment management, we provide environment files to define the Conda environment. This means package dependencies need to be maintained with Conda as well as Poetry. Update the Conda environment definition using the following commands::

    conda env export --from-history --file environment-min.yml
    conda env export --no-builds --file environment.yml

While Poetry is the recommended method for installation, we offer users an option to install the package using `pip`_. To get a requirements.txt file listing::

    pip list --format=freeze > requirements.txt

.. _Poetry: https://python-poetry.org/
.. _Conda: https://conda.io/projects/conda/en/latest/
.. _pip: https://pip.pypa.io/en/stable/

Keeping Current with Science On Schema.Org
------------------------------------------

Project maintainers are responsible for ensuring mappings stay current with new SOSO conventions. Maintainers should monitor the `Science-On-Schema.org GitHub repository`_ and open a general notice as an issue on our GitHub whenever new changes may impact existing mappings and implementations. This issue serves as a collective call to action for the developer community, encouraging collaboration to update implementations.

.. _Science-On-Schema.org GitHub repository: https://github.com/ESIPFed/science-on-schema.org