from dreg_client.client import Client
from dreg_client.repository import Repository

from .drc_test_utils.mock_registry import TEST_NAMESPACE, TEST_REPO, mock_registry


def test_name_with_namespace():
    url = mock_registry()
    repo = Repository(Client(url), TEST_REPO, TEST_NAMESPACE)
    assert repo.name == "mynamespace/myrepo"


def test_name_without_namespace():
    url = mock_registry()
    repo = Repository(Client(url), TEST_REPO)
    assert repo.name == "myrepo"


def test_repr():
    url = mock_registry()
    repo = Repository(Client(url), TEST_REPO, TEST_NAMESPACE)
    assert repr(repo) == "Repository(mynamespace/myrepo)"
