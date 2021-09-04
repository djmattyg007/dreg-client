from __future__ import annotations

import json
from unittest.mock import Mock

import pytest

from dreg_client.manifest import LegacyManifest
from dreg_client.repository import LegacyImageRequestError, Repository

from .conftest import DockerJsonBlob


@pytest.fixture
def tags_client():
    client = Mock()
    client.get_repository_tags.return_value = {
        "name": "testns/testrepo",
        "tags": ["2019", "2020", "2021"],
    }
    return client


@pytest.fixture
def tags_missing_client():
    client = Mock()
    client.get_repository_tags.return_value = {
        "name": "testns/testrepo",
        "tags": None,
    }
    return client


@pytest.fixture
def manifest_client(manifest_v1: DockerJsonBlob):
    # TODO: Clean this up once this PR is released: https://github.com/getsentry/responses/pull/398
    content_length = len(json.dumps(manifest_v1))

    client = Mock()
    client.check_manifest.return_value = (
        "sha256:fc7187188888f5192efdc08682d7fa260820a41f2bdd09b7f5f9cdcb53c9fbc0"
    )
    client.get_manifest.return_value = LegacyManifest(
        digest="sha256:fc7187188888f5192efdc08682d7fa260820a41f2bdd09b7f5f9cdcb53c9fbc0",
        content_type="application/vnd.docker.distribution.manifest.v1+json",
        content_length=content_length,
        content=manifest_v1,
    )
    return client


def test_name_with_namespace():
    repo = Repository(Mock(), "testrepo", "testns")
    assert repo.name == "testns/testrepo"


def test_name_without_namespace():
    repo = Repository(Mock(), "testrepo", None)
    assert repo.name == "testrepo"


def test_tags(tags_client):
    repo = Repository(tags_client, "testrepo", "testns")
    tags = repo.tags()
    assert sorted(tags) == ["2019", "2020", "2021"]


def test_missing_tags(tags_missing_client):
    repo = Repository(tags_missing_client, "testrepo", "testns")
    tags = repo.tags()
    assert tags == ()


def test_tags_refreshes_once(tags_client):
    repo = Repository(tags_client, "testrepo", "testns")
    for _ in range(5):
        repo.tags()
        tags_client.get_repository_tags.assert_called_once_with("testns/testrepo")


def test_get_image_legacy_manifest(manifest_client):
    repo = Repository(manifest_client, "testrepo", "testns")
    image = repo.get_image("2021", raise_on_legacy=False)
    assert isinstance(image, LegacyManifest)
    assert image.digest == "sha256:fc7187188888f5192efdc08682d7fa260820a41f2bdd09b7f5f9cdcb53c9fbc0"
    assert image.short_digest == "fc7187188888"
    manifest_client.get_manifest.assert_called_once_with("testns/testrepo", "2021")
    manifest_client.check_manifest.assert_not_called()


def test_get_image_legacy_manifest_raises(manifest_client):
    repo = Repository(manifest_client, "testrepo", "testns")
    with pytest.raises(LegacyImageRequestError):
        repo.get_image("2021")

    manifest_client.get_manifest.assert_called_once_with("testns/testrepo", "2021")
    manifest_client.check_manifest.assert_not_called()


def test_check_manifest_by_tag(manifest_client):
    repo = Repository(manifest_client, "testrepo", "testns")
    digest = repo.check_manifest("2021")
    assert digest == "sha256:fc7187188888f5192efdc08682d7fa260820a41f2bdd09b7f5f9cdcb53c9fbc0"
    manifest_client.check_manifest.assert_called_once_with("testns/testrepo", "2021")
    manifest_client.get_manifest.assert_not_called()


def test_check_manifest_by_digest(manifest_client):
    repo = Repository(manifest_client, "testrepo", "testns")
    digest = repo.check_manifest(
        "sha256:fc7187188888f5192efdc08682d7fa260820a41f2bdd09b7f5f9cdcb53c9fbc0"
    )
    assert digest == "sha256:fc7187188888f5192efdc08682d7fa260820a41f2bdd09b7f5f9cdcb53c9fbc0"
    manifest_client.check_manifest.assert_called_once_with(
        "testns/testrepo", "sha256:fc7187188888f5192efdc08682d7fa260820a41f2bdd09b7f5f9cdcb53c9fbc0"
    )
    manifest_client.get_manifest.assert_not_called()


def test_get_manifest_by_tag(manifest_client):
    repo = Repository(manifest_client, "testrepo", "testns")
    manifest = repo.get_manifest("2021")
    assert isinstance(manifest, LegacyManifest)
    assert (
        manifest.digest == "sha256:fc7187188888f5192efdc08682d7fa260820a41f2bdd09b7f5f9cdcb53c9fbc0"
    )
    assert manifest.short_digest == "fc7187188888"
    manifest_client.get_manifest.assert_called_once_with("testns/testrepo", "2021")
    manifest_client.check_manifest.assert_not_called()


def test_get_manifest_by_digest(manifest_client):
    repo = Repository(manifest_client, "testrepo", "testns")
    manifest = repo.get_manifest(
        "sha256:fc7187188888f5192efdc08682d7fa260820a41f2bdd09b7f5f9cdcb53c9fbc0"
    )
    assert isinstance(manifest, LegacyManifest)
    assert (
        manifest.digest == "sha256:fc7187188888f5192efdc08682d7fa260820a41f2bdd09b7f5f9cdcb53c9fbc0"
    )
    assert manifest.short_digest == "fc7187188888"
    manifest_client.get_manifest.assert_called_once_with(
        "testns/testrepo", "sha256:fc7187188888f5192efdc08682d7fa260820a41f2bdd09b7f5f9cdcb53c9fbc0"
    )
    manifest_client.check_manifest.assert_not_called()


def test_delete_manifest():
    client = Mock()
    repo = Repository(client, "testrepo")
    repo.delete_manifest("sha256:4ef2dcae68b6a303c47800a752a324c24558c5b79b90cc5dc976cefcef11804b")
    client.delete_manifest.assert_called_once_with(
        "testrepo", "sha256:4ef2dcae68b6a303c47800a752a324c24558c5b79b90cc5dc976cefcef11804b"
    )


def test_get_blob():
    client = Mock()
    repo = Repository(client, "testrepo")
    repo.get_blob("sha256:ec53626738d81855711ed61cdf96b139eb3d35ec34c21e01b7d2ca5386be8462")
    client.get_blob.assert_called_once_with(
        "testrepo", "sha256:ec53626738d81855711ed61cdf96b139eb3d35ec34c21e01b7d2ca5386be8462"
    )


def test_delete_blob():
    client = Mock()
    repo = Repository(client, "testrepo", "testns")
    repo.delete_blob("sha256:5622e1b34662c8a1136e250aa433274c47808c38625918a219a586fd39c59047")
    client.delete_blob.assert_called_once_with(
        "testns/testrepo", "sha256:5622e1b34662c8a1136e250aa433274c47808c38625918a219a586fd39c59047"
    )


def test_manual_refresh(tags_client):
    repo = Repository(tags_client, "testrepo", "testns")
    repo.refresh()
    tags_client.get_repository_tags.assert_called_once_with("testns/testrepo")

    tags_client.get_repository_tags.reset_mock()
    repo.refresh()
    tags_client.get_repository_tags.assert_called_once_with("testns/testrepo")


def test_manual_refresh_after_tag_retrieval(tags_client):
    repo = Repository(tags_client, "testrepo")
    for _ in range(5):
        repo.tags()
    tags_client.get_repository_tags.assert_called_once_with("testrepo")

    tags_client.get_repository_tags.reset_mock()
    repo.refresh()
    tags_client.get_repository_tags.assert_called_once_with("testrepo")

    tags_client.get_repository_tags.reset_mock()
    repo.tags()
    tags_client.get_repository_tags.assert_not_called()


def test_repr_with_namespace():
    repo = Repository(Mock(), "testrepo", "testns")
    assert repr(repo) == "Repository(testns/testrepo)"


def test_repr_without_namespace():
    repo = Repository(Mock(), "testrepo")
    assert repr(repo) == "Repository(testrepo)"
