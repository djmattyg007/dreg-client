from dreg_client.client import Client

from .drc_test_utils.mock_registry import TEST_NAME, TEST_TAG, mock_registry


def test_check_status():
    url = mock_registry()
    Client(url).check_status()


def test_get_manifest_and_digest():
    url = mock_registry()
    manifest = Client(url).get_manifest(TEST_NAME, TEST_TAG)
    assert manifest.digest == "sha256:6c3c624b58dbbcd3c0dd82b4c53f04194d1247c6eebdaab7c610cf7d66709b3b"
    assert isinstance(manifest.content, dict)
