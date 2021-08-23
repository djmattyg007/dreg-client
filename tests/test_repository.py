from dreg_client._BaseClient import BaseClientV2
from dreg_client.Repository import Repository

from .drc_test_utils.mock_registry import TEST_NAME, mock_registry


def test_initv2():
    url = mock_registry()
    Repository(BaseClientV2(url), TEST_NAME)
