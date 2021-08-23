from docker_registry_client._BaseClient import BaseClientV2
from .drc_test_utils.mock_registry import (
    mock_v2_registry, TEST_NAME, TEST_TAG,
)


def test_check_status():
    url = mock_v2_registry()
    BaseClientV2(url).check_status()


def test_get_manifest_and_digest():
    url = mock_v2_registry()
    # TODO: Assert what the digest and manifest are
    manifest, digest = BaseClientV2(url).get_manifest_and_digest(TEST_NAME, TEST_TAG)
