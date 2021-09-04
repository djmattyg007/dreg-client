import re

import pytest

from dreg_client.manifest import InvalidPlatformNameError, Platform


def test_extract_no_variant():
    platform = Platform.extract(
        {
            "os": "linux",
            "architecture": "amd64",
        }
    )
    assert platform.os == "linux"
    assert platform.architecture == "amd64"
    assert platform.variant is None
    assert platform.name == "linux/amd64"
    assert str(platform) == "linux/amd64"
    assert repr(platform) == "Platform(linux/amd64)"


def test_extract_with_variant():
    platform = Platform.extract(
        {
            "os": "linux",
            "architecture": "arm",
            "variant": "v7",
        }
    )
    assert platform.os == "linux"
    assert platform.architecture == "arm"
    assert platform.variant == "v7"
    assert platform.name == "linux/arm/v7"
    assert str(platform) == "linux/arm/v7"
    assert repr(platform) == "Platform(linux/arm/v7)"


def test_from_short_name():
    platform = Platform.from_name("darwin/arm64")
    assert platform.os == "darwin"
    assert platform.architecture == "arm64"
    assert platform.variant is None
    assert platform.name == "darwin/arm64"
    assert str(platform) == "darwin/arm64"
    assert repr(platform) == "Platform(darwin/arm64)"


def test_from_too_short_name():
    errmsg = "^" + re.escape("Invalid platform name 'linux' supplied.") + "$"
    with pytest.raises(InvalidPlatformNameError, match=errmsg):
        Platform.from_name("linux")


def test_from_long_name():
    platform = Platform.from_name("linux/arm/v7")
    assert platform.os == "linux"
    assert platform.architecture == "arm"
    assert platform.variant == "v7"
    assert platform.name == "linux/arm/v7"
    assert str(platform) == "linux/arm/v7"
    assert repr(platform) == "Platform(linux/arm/v7)"


def test_from_too_long_name():
    errmsg = "^" + re.escape("Invalid platform name 'linux/arm/v/7' supplied.") + "$"
    with pytest.raises(InvalidPlatformNameError, match=errmsg):
        Platform.from_name("linux/arm/v/7")


def test_from_names():
    platforms = Platform.from_names(
        (
            "linux/amd64",
            "linux/arm64",
            "darwin/arm64",
            "linux/arm/v7",
        )
    )
    assert len(platforms) == 4
    assert Platform(os="linux", architecture="amd64") in platforms
    assert Platform(os="linux", architecture="arm64") in platforms
    assert Platform(os="darwin", architecture="arm64") in platforms
    assert Platform(os="linux", architecture="arm", variant="v7") in platforms
