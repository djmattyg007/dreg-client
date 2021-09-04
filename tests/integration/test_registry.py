import re
from pathlib import Path
from uuid import uuid4

import pytest
from docker import DockerClient
from requests import HTTPError

import dreg_client.repository as _repository
from dreg_client import Image, Manifest, Platform, PlatformImage, Registry

from ..util import spy


@pytest.mark.usefixtures("registry")
def test_client_image_interactions_single_arch(docker_client: DockerClient, fixtures_dir: Path):
    registry = Registry.build_with_manual_client("http://localhost:5000/v2/")

    docker_client.images.build(
        path=str(fixtures_dir / "base"),
        tag="localhost:5000/x-dreg/x-dreg-example:x-dreg-test",
    )

    docker_client.images.push(
        repository="localhost:5000/x-dreg/x-dreg-example",
        tag="x-dreg-test",
    )

    namespaces = registry.namespaces()
    assert namespaces == ("x-dreg",)

    all_repos = tuple(registry.repositories())
    assert all_repos == ("x-dreg/x-dreg-example",)

    ns_repos = tuple(registry.repositories("x-dreg"))
    assert ns_repos == ("x-dreg/x-dreg-example",)

    with pytest.raises(KeyError):
        registry.repositories(str(uuid4()))

    repo = registry.repository("x-dreg-example", "x-dreg")
    split_repo = registry.repository("x-dreg/x-dreg-example")
    assert split_repo is repo

    manifest = repo.get_manifest("x-dreg-test")
    assert isinstance(manifest, Manifest)

    with spy(_repository, "synth_manifest_list_from_manifest") as synth_spy:
        image = repo.get_image("x-dreg-test")
    assert isinstance(image, Image)
    synth_spy.assert_called_once()
    assert image.manifest_list is synth_spy.spy_return

    assert image.repo == "x-dreg/x-dreg-example"
    assert image.tag == "x-dreg-test"
    assert len(image.manifest_list.manifests) == 1
    assert len(image.platforms) == 1

    platform = next(iter(image.platforms))
    assert isinstance(platform, Platform)

    manifest_by_platform = image.fetch_manifest_by_platform(platform)
    assert manifest_by_platform == manifest
    manifest_by_platform_name = image.fetch_manifest_by_platform_name(platform.name)
    assert manifest_by_platform_name == manifest

    single_manifest_ref = next(iter(image.manifest_list.manifests))
    assert single_manifest_ref.platform == platform

    manifest_by_digest = image.fetch_manifest_by_digest(single_manifest_ref.digest)
    assert manifest_by_digest == manifest

    platform_image = image.get_platform_image(platform)
    assert isinstance(platform_image, PlatformImage)
    assert platform_image.digest == manifest.digest
    assert platform_image.platform_name == platform.name

    platform_images = tuple(image.get_platform_images())
    assert len(platform_images) == 1
    assert platform_images[0] == platform_image

    # The manifest list was synthesised, so it shouldn't exist if we attempt to retrieve it from the registry.
    errmsg = re.escape("404 Client Error")
    with pytest.raises(HTTPError, match=errmsg) as exc_info:
        repo.get_manifest(image.manifest_list.digest)
    assert exc_info.value.response.status_code == 404
