import pytest

from docker_registry_client import DockerRegistryClient
from docker_registry_client.Repository import BaseRepository

from .drc_test_utils.mock_registry import (
    TEST_NAME,
    TEST_NAMESPACE,
    TEST_REPO,
    TEST_TAG,
    mock_v2_registry,
)


class TestDockerRegistryClient(object):
    def test_namespaces(self):
        url = mock_v2_registry()
        client = DockerRegistryClient(url)
        assert client.namespaces() == [TEST_NAMESPACE]

    @pytest.mark.parametrize(
        ("repository", "namespace"),
        [
            (TEST_REPO, None),
            (TEST_REPO, TEST_NAMESPACE),
            ("{0}/{1}".format(TEST_NAMESPACE, TEST_REPO), None),
        ],
    )
    def test_repository(self, repository, namespace):
        url = mock_v2_registry()
        client = DockerRegistryClient(url)
        repository = client.repository(repository, namespace=namespace)
        assert isinstance(repository, BaseRepository)

    def test_repository_namespace_incorrect(self):
        url = mock_v2_registry()
        client = DockerRegistryClient(url)
        with pytest.raises(RuntimeError):
            client.repository("{0}/{1}".format(TEST_NAMESPACE, TEST_REPO), namespace=TEST_NAMESPACE)

    @pytest.mark.parametrize("namespace", [TEST_NAMESPACE, None])
    def test_repositories(self, namespace):
        url = mock_v2_registry()
        client = DockerRegistryClient(url)
        repositories = client.repositories(TEST_NAMESPACE)
        assert len(repositories) == 1
        assert TEST_NAME in repositories
        repository = repositories[TEST_NAME]
        assert repository.name == "%s/%s" % (TEST_NAMESPACE, TEST_REPO)

    def test_repository_tags(self):
        url = mock_v2_registry()
        client = DockerRegistryClient(url)
        repositories = client.repositories(TEST_NAMESPACE)
        assert TEST_NAME in repositories
        repository = repositories[TEST_NAME]
        tags = repository.tags()
        assert len(tags) == 1
        assert TEST_TAG in tags

    def test_repository_manifest(self):
        url = mock_v2_registry()
        client = DockerRegistryClient(url)
        repository = client.repositories()[TEST_NAME]
        digest, manifest = repository.manifest(TEST_TAG)
        repository.delete_manifest(digest)
