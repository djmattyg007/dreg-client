=======================
Contributing Guidelines
=======================

Code Style
==========

Code style is checked by running ``inv lint``. You can reformat all of the code automatically with
``inv reformat``. This should ensure your code passes the style-related linting checks for CI.

Type Checking
=============

Type checking is performed by running ``inv type-check``. This runs mypy under the hood. It is
expected that there are no typing errors before a pull request is merged.

Testing
=======

Tests are run with ``inv test``. Please write tests for new code.

CI
==

We use Github Actions for CI. The build must be passing in order to merge a pull request.

Deploying
=========

dreg-client is deployed to `pypi <https://pypi.org/project/dreg-client>`_
