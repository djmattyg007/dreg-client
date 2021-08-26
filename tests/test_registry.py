import re

import pytest

from dreg_client.registry import Registry
from dreg_client.repository import Repository

from .drc_test_utils.mock_registry import (
    TEST_NAME,
    TEST_NAMESPACE,
    TEST_REPO,
    TEST_TAG,
    mock_registry,
)


def test_namespaces():
    url = mock_registry()
    client = Registry.build_with_client(url)
    assert client.namespaces() == [TEST_NAMESPACE]


@pytest.mark.parametrize(
    ("repository", "namespace"),
    (
        (TEST_REPO, None),
        (TEST_REPO, TEST_NAMESPACE),
        ("{0}/{1}".format(TEST_NAMESPACE, TEST_REPO), None),
    ),
)
def test_repository(repository, namespace):
    url = mock_registry()
    client = Registry.build_with_client(url)
    repository = client.repository(repository, namespace=namespace)
    assert isinstance(repository, Repository)


def test_repository_namespace_incorrect():
    url = mock_registry()
    client = Registry.build_with_client(url)

    errmsg = "^" + re.escape("Cannot specify namespace twice.") + "$"
    with pytest.raises(RuntimeError, match=errmsg):
        client.repository("{0}/{1}".format(TEST_NAMESPACE, TEST_REPO), namespace=TEST_NAMESPACE)


@pytest.mark.parametrize("namespace", (TEST_NAMESPACE, None))
def test_repositories(namespace):
    url = mock_registry()
    client = Registry.build_with_client(url)
    repositories = client.repositories(TEST_NAMESPACE)
    assert len(repositories) == 1
    assert TEST_NAME in repositories
    repository = repositories[TEST_NAME]
    assert repository.name == f"{TEST_NAMESPACE}/{TEST_REPO}"


def test_repository_tags():
    url = mock_registry()
    client = Registry.build_with_client(url)
    repositories = client.repositories(TEST_NAMESPACE)
    assert TEST_NAME in repositories
    repository = repositories[TEST_NAME]
    tags = repository.tags()
    assert len(tags) == 1
    assert TEST_TAG in tags


def test_repository_manifest():
    url = mock_registry()
    client = Registry.build_with_client(url)
    repository = client.repositories()[TEST_NAME]
    manifest = repository.manifest(TEST_TAG)
    repository.delete_manifest(manifest.digest)
