from __future__ import annotations

import json
import re
from unittest.mock import Mock

import pytest
import responses
from requests import HTTPError

from dreg_client.auth_service import AuthService
from dreg_client.client import Client
from dreg_client.manifest import ImageConfig, LegacyManifest, Platform

from .conftest import DockerJsonBlob


def test_init_failure():
    errmsg = "^" + re.escape("Cannot supply session.auth and auth_service together.") + "$"
    session = Mock()
    session.auth = ("username", "password")
    with pytest.raises(ValueError, match=errmsg):
        Client(session, auth_service=Mock(spec=AuthService))


def test_build_with_session_failure():
    errmsg = "^" + re.escape("Cannot supply auth and auth_service together.") + "$"
    with pytest.raises(ValueError, match=errmsg):
        Client.build_with_session(
            "https://registry.example.com:5000/v2/",
            auth=("username", "password"),
            auth_service=Mock(spec=AuthService),
        )


def test_check_status_success():
    with responses.RequestsMock() as rsps:
        rsps.add(rsps.GET, "https://registry.example.com:5000/v2/", json={})

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        assert client.check_status() is True


def test_check_status_failure():
    with responses.RequestsMock() as rsps:
        rsps.add(rsps.GET, "https://registry.example.com:5000/v2/", status=404)

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        assert client.check_status() is False

    with responses.RequestsMock() as rsps:
        rsps.add(rsps.GET, "https://registry.example.com:5000/v2/", body="{'abc'}")

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        assert client.check_status() is False


def test_catalog_success():
    with responses.RequestsMock() as rsps:
        result = {"repositories": ["abc", "def"]}
        rsps.add(rsps.GET, "https://registry.example.com:5000/v2/_catalog", json=result)

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        assert client.catalog() == result


def test_catalog_failure():
    with responses.RequestsMock() as rsps:
        rsps.add(rsps.GET, "https://registry.example.com:5000/v2/_catalog", status=404)

        client = Client.build_with_session("https://registry.example.com:5000/v2/")

        errmsg = re.escape("404 Client Error")
        with pytest.raises(HTTPError, match=errmsg) as exc_info:
            client.catalog()
        assert exc_info.value.response.status_code == 404

    with responses.RequestsMock() as rsps:
        rsps.add(rsps.GET, "https://registry.example.com:5000/v2/_catalog", body="{'abc'}")

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        with pytest.raises(ValueError):  # noqa: PT011
            client.catalog()


def test_get_repository_tags_success():
    with responses.RequestsMock() as rsps:
        result = {"name": "testns/testrepo", "tags": ["2019", "2020", "2021"]}
        rsps.add(
            rsps.GET, "https://registry.example.com:5000/v2/testns/testrepo/tags/list", json=result
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        assert client.get_repository_tags("testns/testrepo") == result


def test_get_repository_tags_failure():
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.GET, "https://registry.example.com:5000/v2/testns/testrepo/tags/list", status=404
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")

        errmsg = re.escape("404 Client Error")
        with pytest.raises(HTTPError, match=errmsg) as exc_info:
            client.get_repository_tags("testns/testrepo")
        assert exc_info.value.response.status_code == 404

    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.GET,
            "https://registry.example.com:5000/v2/testns/testrepo/tags/list",
            body="{'abc'}",
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        with pytest.raises(ValueError):  # noqa: PT011
            client.get_repository_tags("testns/testrepo")


def test_check_manifest_success():
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.HEAD,
            "https://registry.example.com:5000/v2/testns/testrepo/manifests/abcdef",
            content_type="application/vnd.docker.distribution.manifest+v1+prettyjws",
            headers={
                "Content-Length": "1000",
                "Docker-Content-Digest": "sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667",
            },
        )
        rsps.add(
            rsps.HEAD,
            "https://registry.example.com:5000/v2/testns/testrepo/manifests/sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667",
            content_type="application/vnd.docker.distribution.manifest+v1+prettyjws",
            headers={
                "Content-Length": "1000",
                "Docker-Content-Digest": "sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667",
            },
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")

        digest1 = client.check_manifest("testns/testrepo", "abcdef")
        assert digest1 == "sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667"

        digest2 = client.check_manifest(
            "testns/testrepo",
            "sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667",
        )
        assert digest2 == digest1


def test_check_manifest_failure():
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.HEAD,
            "https://registry.example.com:5000/v2/testns/testrepo/manifests/abcdef",
            status=404,
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        digest = client.check_manifest("testns/testrepo", "abcdef")
        assert digest is None

    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.HEAD,
            "https://registry.example.com:5000/v2/testns/testrepo/manifests/abcdef",
            status=500,
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")

        errmsg = re.escape("500 Server Error")
        with pytest.raises(HTTPError, match=errmsg) as exc_info:
            client.check_manifest("testns/testrepo", "abcdef")
        assert exc_info.value.response.status_code == 500


def test_get_manifest_success(manifest_v1: DockerJsonBlob):
    # TODO: Clean this up once this PR is released: https://github.com/getsentry/responses/pull/398
    content_length = len(json.dumps(manifest_v1))

    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.GET,
            "https://registry.example.com:5000/v2/testns/testrepo/manifests/abcdef",
            json=manifest_v1,
            content_type="application/vnd.docker.distribution.manifest.v1+prettyjws",
            headers={
                "Content-Length": str(content_length),
                "Docker-Content-Digest": "sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667",
            },
        )
        rsps.add(
            rsps.GET,
            "https://registry.example.com:5000/v2/testns/testrepo/manifests/sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667",
            json=manifest_v1,
            content_type="application/vnd.docker.distribution.manifest.v1+prettyjws",
            headers={
                "Content-Length": str(content_length),
                "Docker-Content-Digest": "sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667",
            },
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")

        manifest1 = client.get_manifest("testns/testrepo", "abcdef")
        assert isinstance(manifest1, LegacyManifest)
        assert (
            manifest1.digest
            == "sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667"
        )
        assert manifest1.short_digest == "1a067fa67b5b"
        assert manifest1.content_type == "application/vnd.docker.distribution.manifest.v1+prettyjws"
        assert manifest1.content == manifest_v1

        manifest2 = client.get_manifest(
            "testns/testrepo",
            "sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667",
        )
        assert isinstance(manifest2, LegacyManifest)
        assert manifest2 == manifest1
        assert manifest2.digest == manifest1.digest
        assert manifest2.short_digest == manifest1.short_digest
        assert manifest2.content_type == manifest1.content_type
        assert manifest2.content == manifest1.content


def test_get_manifest_failure():
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.GET,
            "https://registry.example.com:5000/v2/testns/testrepo/manifests/abcdef",
            status=404,
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")

        errmsg = re.escape("404 Client Error")
        with pytest.raises(HTTPError, match=errmsg) as exc_info:
            client.get_manifest("testns/testrepo", "abcdef")
        assert exc_info.value.response.status_code == 404

    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.GET,
            "https://registry.example.com:5000/v2/testns/testrepo/manifests/abcdef",
            content_type="application/vnd.docker.distribution.manifest.v1+prettyjws",
            body="{'abc'}",
            headers={
                "Content-Length": "7",
                "Docker-Content-Digest": "sha256:0ca2177c6caa494f76e40d9badc253d8bbca6df4cbe1e1630875b7c087f85d56",
            },
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        with pytest.raises(ValueError):  # noqa: PT011
            client.get_manifest("testns/testrepo", "abcdef")


def test_delete_manifest_success():
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.DELETE,
            "https://registry.example.com:5000/v2/testns/testrepo/manifests/sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667",
            status=202,
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        response = client.delete_manifest(
            "testns/testrepo",
            "sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667",
        )
        assert response.status_code == 202


def test_delete_manifest_failure():
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.DELETE,
            "https://registry.example.com:5000/v2/testns/testrepo/manifests/sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667",
            status=404,
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")

        errmsg = re.escape("404 Client Error")
        with pytest.raises(HTTPError, match=errmsg) as exc_info:
            client.delete_manifest(
                "testns/testrepo",
                "sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667",
            )
        assert exc_info.value.response.status_code == 404


def test_get_image_config_blob_success(blob_container_image_v1: DockerJsonBlob):
    # TODO: Clean this up once this PR is released: https://github.com/getsentry/responses/pull/398
    content_length = len(json.dumps(blob_container_image_v1))

    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.GET,
            "https://registry.example.com:5000/v2/testns/testrepo/blobs/sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667",
            json=blob_container_image_v1,
            headers={
                "Content-Length": str(content_length),
                "Docker-Content-Digest": "sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667",
            },
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        config = client.get_image_config_blob(
            "testns/testrepo",
            "sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667",
        )

        assert isinstance(config, ImageConfig)
        assert (
            config.digest
            == "sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667"
        )
        assert config.short_digest == "1a067abcdef1"
        assert config.platform_name == "linux/amd64"
        assert config.platform == Platform("linux", "amd64", None)
        assert config.created_at == "2021-08-28T01:35:59.758616391Z"


def test_get_blob_success(blob_container_image_v1: DockerJsonBlob):
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.GET,
            "https://registry.example.com:5000/v2/testns/testrepo/blobs/sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667",
            json=blob_container_image_v1,
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        response = client.get_blob(
            "testns/testrepo",
            "sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667",
        )
        blob = response.json()
        assert blob == blob_container_image_v1


def test_get_blob_failure():
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.GET,
            "https://registry.example.com:5000/v2/testns/testrepo/blobs/sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667",
            status=404,
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")

        errmsg = re.escape("404 Client Error")
        with pytest.raises(HTTPError, match=errmsg) as exc_info:
            client.get_blob(
                "testns/testrepo",
                "sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667",
            )
        assert exc_info.value.response.status_code == 404

    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.GET,
            "https://registry.example.com:5000/v2/testns/testrepo/blobs/sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667",
            body="{'abc'}",
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        response = client.get_blob(
            "testns/testrepo",
            "sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667",
        )
        with pytest.raises(ValueError):  # noqa: PT011
            response.json()


def test_delete_blob_success():
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.DELETE,
            "https://registry.example.com:5000/v2/testns/testrepo/blobs/sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667",
            status=202,
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        response = client.delete_blob(
            "testns/testrepo",
            "sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667",
        )
        assert response.status_code == 202


def test_delete_blob_failure():
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.DELETE,
            "https://registry.example.com:5000/v2/testns/testrepo/blobs/sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667",
            status=404,
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")

        errmsg = re.escape("404 Client Error")
        with pytest.raises(HTTPError, match=errmsg) as exc_info:
            client.delete_blob(
                "testns/testrepo",
                "sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667",
            )
        assert exc_info.value.response.status_code == 404
