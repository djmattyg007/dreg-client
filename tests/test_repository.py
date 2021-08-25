from dreg_client._BaseClient import BaseClient
from dreg_client.repository import Repository

from .drc_test_utils.mock_registry import TEST_NAME, mock_registry


def test_init():
    url = mock_registry()
    Repository(BaseClient(url), TEST_NAME)
