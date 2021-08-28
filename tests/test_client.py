import pytest
import requests
import responses

from dreg_client.client import Client

from .drc_test_utils.mock_registry import TEST_NAME, TEST_TAG, mock_registry


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
        try:
            client.catalog()
        except requests.HTTPError as exc:
            assert exc.response.status_code == 404
        else:
            pytest.fail("Client.catalog() did not throw an exception for HTTP 404 as expected.")

    with responses.RequestsMock() as rsps:
        rsps.add(rsps.GET, "https://registry.example.com:5000/v2/_catalog", body="{'abc'}")

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        with pytest.raises(ValueError):
            client.catalog()


def test_get_repository_tags_success():
    with responses.RequestsMock() as rsps:
        result = {"name": "testns/testrepo", "tags": ["2019", "2020", "2021"]}
        rsps.add(rsps.GET, "https://registry.example.com:5000/v2/testns/testrepo/tags/list", json=result)

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        assert client.get_repository_tags("testns/testrepo") == result


def test_get_repository_tags_failure():
    with responses.RequestsMock() as rsps:
        rsps.add(rsps.GET, "https://registry.example.com:5000/v2/testns/testrepo/tags/list", status=404)

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        try:
            client.get_repository_tags("testns/testrepo")
        except requests.HTTPError as exc:
            assert exc.response.status_code == 404
        else:
            pytest.fail("Client.get_repository_tags() did not throw an exception for HTTP 404 as expected.")

    with responses.RequestsMock() as rsps:
        rsps.add(rsps.GET, "https://registry.example.com:5000/v2/testns/testrepo/tags/list", body="{'abc'}")

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        with pytest.raises(ValueError):
            client.get_repository_tags("testns/testrepo")


def test_get_manifest_success(manifest_v1):
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.GET,
            "https://registry.example.com:5000/v2/testns/testrepo/manifests/abcdef",
            json=manifest_v1,
            content_type="application/vnd.docker.distribution.manifest+v1+prettyjws",
            headers={
                "docker-content-digest": "sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667",
            },
        )
        rsps.add(
            rsps.GET,
            "https://registry.example.com:5000/v2/testns/testrepo/manifests/sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667",
            json=manifest_v1,
            content_type="application/vnd.docker.distribution.manifest+v1+prettyjws",
            headers={
                "docker-content-digest": "sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667",
            },
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")

        manifest1 = client.get_manifest("testns/testrepo", "abcdef")
        assert manifest1.digest == "sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667"
        assert manifest1.content_type == "application/vnd.docker.distribution.manifest+v1+prettyjws"
        assert manifest1.content == manifest_v1

        manifest2 = client.get_manifest("testns/testrepo", "sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667")
        assert manifest2.digest == manifest1.digest
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
        try:
            client.get_manifest("testns/testrepo", "abcdef")
        except requests.HTTPError as exc:
            assert exc.response.status_code == 404
        else:
            pytest.fail("Client.get_manifest() did not throw an exception for HTTP 404 as expected.")

    with responses.RequestsMock() as rsps:
        rsps.add(rsps.GET, "https://registry.example.com:5000/v2/testns/testrepo/manifests/abcdef", body="{'abc'}")

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        with pytest.raises(ValueError):
            client.get_manifest("testns/testrepo", "abcdef")


def test_delete_manifest_success():
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.DELETE,
            "https://registry.example.com:5000/v2/testns/testrepo/manifests/sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667",
            status=202,
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        response = client.delete_manifest("testns/testrepo", "sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667")
        assert response.status_code == 202


def test_delete_manifest_failure():
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.DELETE,
            "https://registry.example.com:5000/v2/testns/testrepo/manifests/sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667",
            status=404,
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        try:
            client.delete_manifest("testns/testrepo", "sha256:1a067fa67b5bf1044c411ad73ac82cecd3d4dd2dabe7bc4d4b6dbbd55963b667")
        except requests.HTTPError as exc:
            assert exc.response.status_code == 404
        else:
            pytest.fail("Client.delete_manifest() did not throw an exception for HTTP 404 as expected.")


def test_get_blob_success(blob_container_image_v1):
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.GET,
            "https://registry.example.com:5000/v2/testns/testrepo/blobs/sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667",
            json=blob_container_image_v1,
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        response = client.get_blob("testns/testrepo", "sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667")
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
        try:
            client.get_blob("testns/testrepo", "sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667")
        except requests.HTTPError as exc:
            assert exc.response.status_code == 404
        else:
            pytest.fail("Client.get_blob() did not throw an exception for HTTP 404 as expected.")

    with responses.RequestsMock() as rsps:
        rsps.add(rsps.GET, "https://registry.example.com:5000/v2/testns/testrepo/blobs/sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667", body="{'abc'}")

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        response = client.get_blob("testns/testrepo", "sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667")
        with pytest.raises(ValueError):
            response.json()


def test_delete_blob_success():
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.DELETE,
            "https://registry.example.com:5000/v2/testns/testrepo/blobs/sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667",
            status=202,
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        response = client.delete_blob("testns/testrepo", "sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667")
        assert response.status_code == 202


def test_delete_blob_failure():
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.DELETE,
            "https://registry.example.com:5000/v2/testns/testrepo/blobs/sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667",
            status=404,
        )

        client = Client.build_with_session("https://registry.example.com:5000/v2/")
        try:
            client.delete_blob("testns/testrepo", "sha256:1a067abcdef121044c411ad73ac82cecd098762dabe7bc4d4b6dbbd55963b667")
        except requests.HTTPError as exc:
            assert exc.response.status_code == 404
        else:
            pytest.fail("Client.delete_blob() did not throw an exception for HTTP 404 as expected.")
