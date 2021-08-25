from dreg_client.client import Client

from .drc_test_utils.mock_registry import TEST_NAME, TEST_TAG, mock_registry


def test_check_status():
    url = mock_registry()
    Client(url).check_status()


def test_get_manifest_and_digest():
    url = mock_registry()
    # TODO: Assert what the digest and manifest are
    digest, manifest = Client(url).get_digest_and_manifest(TEST_NAME, TEST_TAG)
