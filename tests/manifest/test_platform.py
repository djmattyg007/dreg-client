from dreg_client.manifest import Platform


def test_from_short_name():
    platform = Platform.from_name("darwin/arm64")
    assert platform.os == "darwin"
    assert platform.architecture == "arm64"
    assert platform.variant is None
    assert platform.name == "darwin/arm64"


def test_from_long_name():
    platform = Platform.from_name("linux/arm/v7")
    assert platform.os == "linux"
    assert platform.architecture == "arm"
    assert platform.variant == "v7"
    assert platform.name == "linux/arm/v7"


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
