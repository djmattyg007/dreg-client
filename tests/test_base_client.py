from dreg_client._BaseClient import BaseClientV2

from .drc_test_utils.mock_registry import TEST_NAME, TEST_TAG, mock_v2_registry


def test_check_status():
    url = mock_v2_registry()
    BaseClientV2(url).check_status()


def test_get_manifest_and_digest():
    url = mock_v2_registry()
    # TODO: Assert what the digest and manifest are
    digest, manifest = BaseClientV2(url).get_digest_and_manifest(TEST_NAME, TEST_TAG)
