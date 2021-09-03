import re
from unittest.mock import Mock
from uuid import uuid4

import pytest

from dreg_client.manifest import (
    UnusableManifestPayloadError,
    UnusableManifestResponseError,
    parse_manifest_response,
)


@pytest.mark.parametrize("content_type", ("text/plain", "application/json", "text/html"))
def test_unknown_contenttype_header(content_type: str):
    response = Mock()
    response.headers = {
        "Content-Type": content_type,
    }

    errmsg = "^" + re.escape("Unknown Content-Type header in response.") + "$"
    with pytest.raises(UnusableManifestResponseError, match=errmsg):
        parse_manifest_response(response)


def test_missing_contenttype_header():
    response = Mock()
    response.headers = {}

    errmsg = "^" + re.escape("Unknown Content-Type header in response.") + "$"
    with pytest.raises(UnusableManifestResponseError, match=errmsg):
        parse_manifest_response(response)


def test_missing_digest_header():
    response = Mock()
    response.headers = {
        "Content-Type": "application/vnd.docker.distribution.manifest.v2+json",
    }

    errmsg = "^" + re.escape("No digest specified in response headers") + "$"
    with pytest.raises(UnusableManifestResponseError, match=errmsg):
        parse_manifest_response(response)


def test_missing_contentlength_header():
    response = Mock()
    response.headers = {
        "Content-Type": "application/vnd.docker.distribution.manifest.v2+json",
        "Docker-Content-Digest": str(uuid4()),
    }

    errmsg = "^" + re.escape("No content length specified in response headers.") + "$"
    with pytest.raises(UnusableManifestResponseError, match=errmsg):
        parse_manifest_response(response)


def test_invalid_contentlength_header():
    response = Mock()
    response.headers = {
        "Content-Length": "docker",
        "Content-Type": "application/vnd.docker.distribution.manifest.v2+json",
        "Docker-Content-Digest": str(uuid4()),
    }

    errmsg = "^" + re.escape("Invalid content length specified in response headers.") + "$"
    with pytest.raises(UnusableManifestResponseError, match=errmsg) as exc_info:
        parse_manifest_response(response)

    assert isinstance(exc_info.value.__cause__, ValueError)


def test_invalid_json():
    response = Mock()
    response.headers = {
        "Content-Length": "42",
        "Content-Type": "application/vnd.docker.distribution.manifest.v2+json",
        "Docker-Content-Digest": str(uuid4()),
    }
    response.json.return_value = []

    errmsg = "^" + re.escape("Non-dictionary payload returned.") + "$"
    with pytest.raises(UnusableManifestPayloadError, match=errmsg):
        parse_manifest_response(response)


def test_misrepresented_payload():
    response = Mock()
    response.headers = {
        "Content-Length": "42",
        "Content-Type": "application/vnd.docker.distribution.manifest.v2+json",
        "Docker-Content-Digest": str(uuid4()),
    }
    response.json.return_value = {
        "schemaVersion": 1,
    }

    errmsg = "^" + re.escape("Unknown schema version in payload.") + "$"
    with pytest.raises(UnusableManifestPayloadError, match=errmsg):
        parse_manifest_response(response)


def test_mismatched_content_type():
    response = Mock()
    response.headers = {
        "Content-Length": "42",
        "Content-Type": "application/vnd.docker.distribution.manifest.v2+json",
        "Docker-Content-Digest": str(uuid4()),
    }
    response.json.return_value = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.docker.distribution.manifest.list.v2+json",
    }

    errmsg = "^" + re.escape("Mismatched media type between headers and payload.") + "$"
    with pytest.raises(UnusableManifestPayloadError, match=errmsg):
        parse_manifest_response(response)


def test_mismatched_list_content_type():
    response = Mock()
    response.headers = {
        "Content-Length": "42",
        "Content-Type": "application/vnd.docker.distribution.manifest.list.v2+json",
        "Docker-Content-Digest": str(uuid4()),
    }
    response.json.return_value = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
    }

    errmsg = "^" + re.escape("Mismatched media type between headers and payload.") + "$"
    with pytest.raises(UnusableManifestPayloadError, match=errmsg):
        parse_manifest_response(response)
