import re
from unittest.mock import Mock

import pytest

from dreg_client.image import Image, UnavailableImagePlatformError
from dreg_client.manifest import ManifestList, ManifestRef, Platform
from dreg_client.schemas import schema_2, schema_2_list


def test_fetch_manifest_by_platform_name_no_refs():
    image = Image(
        Mock(),
        "testns/testrepo",
        "latest",
        ManifestList("test", schema_2_list, 42, frozenset()),
    )

    errmsg = "^" + re.escape("No manifest available for the selected platform in this image.") + "$"
    with pytest.raises(UnavailableImagePlatformError, match=errmsg):
        image.fetch_manifest_by_platform_name("linux/amd64")


def test_fetch_manifest_by_unknown_platform_name():
    image = Image(
        Mock(),
        "testns/testrepo",
        "latest",
        ManifestList(
            "test",
            schema_2_list,
            42,
            frozenset(
                {
                    ManifestRef("testref", schema_2, 52, Platform.from_name("linux/arm64")),
                }
            ),
        ),
    )

    errmsg = "^" + re.escape("No manifest available for the selected platform in this image.") + "$"
    with pytest.raises(UnavailableImagePlatformError, match=errmsg):
        image.fetch_manifest_by_platform_name("linux/amd64")


def test_fetch_manifest_by_platform_no_refs():
    image = Image(
        Mock(),
        "testns/testrepo",
        "latest",
        ManifestList("test", schema_2_list, 42, frozenset()),
    )

    errmsg = "^" + re.escape("No manifest available for the selected platform in this image.") + "$"
    with pytest.raises(UnavailableImagePlatformError, match=errmsg):
        image.fetch_manifest_by_platform(Platform.from_name("linux/amd64"))


def test_fetch_manifest_by_unknown_platform():
    image = Image(
        Mock(),
        "testns/testrepo",
        "latest",
        ManifestList(
            "test",
            schema_2_list,
            42,
            frozenset(
                {
                    ManifestRef("testref", schema_2, 52, Platform.from_name("linux/arm64")),
                }
            ),
        ),
    )

    errmsg = "^" + re.escape("No manifest available for the selected platform in this image.") + "$"
    with pytest.raises(UnavailableImagePlatformError, match=errmsg):
        image.fetch_manifest_by_platform(Platform.from_name("linux/amd64"))
