from docker_registry_client._BaseClient import BaseClientV2
from docker_registry_client.Repository import Repository

from .drc_test_utils.mock_registry import TEST_NAME, mock_v2_registry


def test_initv2():
    url = mock_v2_registry()
    Repository(BaseClientV2(url), TEST_NAME)
