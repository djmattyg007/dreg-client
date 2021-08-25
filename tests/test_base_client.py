from dreg_client._BaseClient import BaseClient

from .drc_test_utils.mock_registry import TEST_NAME, TEST_TAG, mock_registry


def test_check_status():
    url = mock_registry()
    BaseClient(url).check_status()


def test_get_manifest_and_digest():
    url = mock_registry()
    # TODO: Assert what the digest and manifest are
    digest, manifest = BaseClient(url).get_digest_and_manifest(TEST_NAME, TEST_TAG)
