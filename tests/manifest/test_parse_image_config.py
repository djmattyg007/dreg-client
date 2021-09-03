import re
from unittest import mock
from uuid import uuid4

import pytest

from dreg_client.manifest import UnusableImageConfigBlobResponseError, UnusableImageConfigBlobPayloadError, parse_image_config_blob_response


def test_missing_digest_header():
    response = mock.Mock()
    response.headers = {}

    errmsg = "^" + re.escape("No digest specified in response headers.") + "$"
    with pytest.raises(UnusableImageConfigBlobResponseError, match=errmsg):
        parse_image_config_blob_response(response)


def test_missing_contentlength_header():
    response = mock.Mock()
    response.headers = {
        "Docker-Content-Digest": str(uuid4()),
    }

    errmsg = "^" + re.escape("No content length specified in response headers.") + "$"
    with pytest.raises(UnusableImageConfigBlobResponseError, match=errmsg):
        parse_image_config_blob_response(response)


def test_invalid_contentlength_header():
    response = mock.Mock()
    response.headers = {
        "Content-Length": "docker",
        "Docker-Content-Digest": str(uuid4()),
    }

    errmsg = "^" + re.escape("Invalid content length specified in response headers.") + "$"
    with pytest.raises(UnusableImageConfigBlobResponseError, match=errmsg) as exc_info:
        parse_image_config_blob_response(response)

    assert isinstance(exc_info.value.__cause__, ValueError)


def test_invalid_json():
    response = mock.Mock()
    response.headers = {
        "Content-Length": "42",
        "Docker-Content-Digest": str(uuid4()),
    }
    response.json.return_value = []

    errmsg = "^" + re.escape("Non-dictionary payload returned.") + "$"
    with pytest.raises(UnusableImageConfigBlobPayloadError, match=errmsg):
        parse_image_config_blob_response(response)
