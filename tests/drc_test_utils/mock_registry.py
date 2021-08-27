import json

from flexmock import flexmock
from requests.exceptions import HTTPError
from requests.models import Response

from dreg_client import client


REGISTRY_URL = "https://registry.example.com:5000"
TEST_NAMESPACE = "mynamespace"
TEST_REPO = "myrepo"
TEST_NAME = "%s/%s" % (TEST_NAMESPACE, TEST_REPO)
TEST_TAG = "latest"
TEST_MANIFEST_DIGEST = "sha256:6c3c624b58dbbcd3c0dd82b4c53f04194d1247c6eebdaab7c610cf7d66709b3b"


def format_url(s):
    return s.format(
        namespace=TEST_NAMESPACE,
        repo=TEST_REPO,
        name=TEST_NAME,
        tag=TEST_TAG,
        digest=TEST_MANIFEST_DIGEST,
    )


class MockResponse:
    def __init__(self, code, data=None, text=None, headers=None):
        self.ok = 200 <= code < 400
        self.status_code = code
        self.data = data
        self.text = text or ""
        self.headers = headers or {}
        self.reason = ""

    @property
    def content(self):
        if self.data is None:
            return None

        return json.dumps(self.data).encode()

    def raise_for_status(self):
        if not self.ok:
            response = Response()
            response.status_code = self.status_code
            raise HTTPError(response=response)

    def json(self):
        return self.data


class MockRegistry:
    TAGS = format_url("/v2/{name}/tags/list")
    TAGS_LIBRARY = format_url("/v2/{repo}/tags/list")
    MANIFEST_TAG = format_url("/v2/{name}/manifests/{tag}")
    MANIFEST_DIGEST = format_url("/v2/{name}/manifests/{digest}")

    GET_MAP = {
        "/v2/": MockResponse(200),
        "/v2/_catalog": MockResponse(200, data={"repositories": [TEST_NAME, "otherrepo"]}),
        TAGS: MockResponse(200, data={"name": TEST_NAME, "tags": [TEST_TAG]}),
        TAGS_LIBRARY: MockResponse(200, data={"name": TEST_NAME, "tags": [TEST_TAG]}),
        MANIFEST_TAG: MockResponse(
            200,
            data={"name": TEST_NAME, "tag": TEST_TAG, "fsLayers": []},
            headers={
                "Docker-Content-Digest": TEST_MANIFEST_DIGEST,
            },
        ),
    }

    DELETE_MAP = {
        MANIFEST_DIGEST: MockResponse(202, data={}),
    }

    def call(self, response_map, url, json=None, headers=None):
        assert url.startswith(REGISTRY_URL)
        request = format_url(url[len(REGISTRY_URL) :])
        try:
            return response_map[request]
        except KeyError:
            return MockResponse(code=404, text="Not found: %s" % request)

    def get(self, *args, **kwargs):
        return self.call(self.GET_MAP, *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.call(self.DELETE_MAP, *args, **kwargs)


def mock_registry():
    registry = MockRegistry()
    flexmock(client, get=registry.get, delete=registry.delete)
    return REGISTRY_URL
