## Code Style

Code style is checked by running ``inv lint``. You can reformat all of the code automatically with
``inv reformat``. This should ensure your code passes the style-related linting checks for CI.

## Testing

Tests are run with ``inv test``. Please write tests for new code.

## CI

We use Github Actions for CI. The build must be passing in order to merge a pull request.

## Deploying

dreg-client is deployed to `pypi <https://pypi.org/project/dreg-client>`_
