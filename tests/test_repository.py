from docker_registry_client.Repository import Repository
from docker_registry_client._BaseClient import BaseClientV2
from .drc_test_utils.mock_registry import (
    mock_v2_registry, TEST_NAME,
)


def test_initv2():
    url = mock_v2_registry()
    Repository(BaseClientV2(url), TEST_NAME)
