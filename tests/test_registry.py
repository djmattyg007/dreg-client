from __future__ import annotations

import re
from unittest.mock import Mock

import pytest

from dreg_client.registry import Registry
from dreg_client.repository import Repository


@pytest.fixture
def client():
    client = Mock()
    client.catalog.return_value = {
        "repositories": [
            "debian",
            "testns1/testrepo1",
            "testns2/testrepo2",
            "testns1/testrepo3",
            "bitnami/redis",
        ],
    }
    return client


def test_namespaces(client):
    registry = Registry(client)
    namespaces = registry.namespaces()
    assert sorted(namespaces) == [
        "bitnami",
        "library",
        "testns1",
        "testns2",
    ]


def test_namespaces_refreshes_once(client):
    registry = Registry(client)
    for _ in range(5):
        registry.namespaces()
        client.catalog.assert_called_once_with()


def test_repository_splits_repo():
    client = Mock()
    registry = Registry(client)
    repo = registry.repository("testns/testrepo")
    assert repo.name == "testns/testrepo"
    assert repo.namespace == "testns"
    assert repo.repository == "testrepo"


def test_repository_rejects_both_split_repo_and_specific_namespace_together():
    client = Mock()
    registry = Registry(client)

    errmsg = "^" + re.escape("Cannot specify namespace twice.") + "$"
    with pytest.raises(ValueError, match=errmsg):
        registry.repository("testns/testrepo", "testns")


def test_repository_separate_repo_and_namespace():
    client = Mock()
    registry = Registry(client)

    repo = registry.repository("testrepo", "testns")
    assert repo.name == "testns/testrepo"
    assert repo.namespace == "testns"
    assert repo.repository == "testrepo"


def test_retrieve_specific_repositories(client):
    registry = Registry(client)

    repos_testns1 = registry.repositories("testns1")
    assert len(repos_testns1) == 2
    assert all(isinstance(repo, Repository) for repo in repos_testns1.values())

    repos_testns2 = registry.repositories("testns2")
    assert len(repos_testns2) == 1
    assert all(isinstance(repo, Repository) for repo in repos_testns2.values())

    repos_library = registry.repositories("library")
    assert len(repos_library) == 1
    assert all(isinstance(repo, Repository) for repo in repos_library.values())

    client.catalog.assert_called_once_with()


def test_retrieve_all_repositories(client):
    registry = Registry(client)

    repos = registry.repositories()
    assert len(repos) == 5
    assert all(isinstance(repo, Repository) for repo in repos.values())


def test_retrieve_all_repositories_refreshes_once(client):
    registry = Registry(client)

    for _ in range(5):
        registry.repositories()
        client.catalog.assert_called_once_with()


def test_manual_refresh(client):
    registry = Registry(client)
    registry.refresh()
    client.catalog.assert_called_once_with()

    client.catalog.reset_mock()
    registry.refresh()
    client.catalog.assert_called_once_with()


def test_manual_refresh_after_namespaces_retrieval(client):
    registry = Registry(client)
    for _ in range(5):
        registry.namespaces()
    client.catalog.assert_called_once_with()

    client.catalog.reset_mock()
    registry.refresh()
    client.catalog.assert_called_once_with()

    client.catalog.reset_mock()
    registry.namespaces()
    client.catalog.assert_not_called()


def test_manual_refresh_after_repositories_retrieval(client):
    registry = Registry(client)
    for _ in range(5):
        registry.repositories()
    client.catalog.assert_called_once_with()

    client.catalog.reset_mock()
    registry.refresh()
    client.catalog.assert_called_once_with()

    client.catalog.reset_mock()
    registry.repositories()
    client.catalog.assert_not_called()
