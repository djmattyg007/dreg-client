from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pytest
from docker import DockerClient

from dreg_client import Client, Manifest


@pytest.mark.usefixtures("registry")
def test_client():
    client = Client.build_with_session("http://localhost:5000/v2/")
    assert client.catalog() == {"repositories": []}


@pytest.mark.usefixtures("registry")
def test_client_manifest_interactions(docker_client: DockerClient, fixtures_dir: Path):
    client = Client.build_with_session("http://localhost:5000/v2/")

    docker_client.images.build(
        path=str(fixtures_dir / "base"),
        tag="localhost:5000/x-dreg-example:x-dreg-test",
    )

    docker_client.images.push(
        repository="localhost:5000/x-dreg-example",
        tag="x-dreg-test",
    )

    tags_response = client.get_repository_tags("x-dreg-example")
    assert tags_response["name"] == "x-dreg-example"
    assert isinstance(tags_response["tags"], Sequence)
    assert sorted(tags_response["tags"]) == ["x-dreg-test"]

    manifest = client.get_manifest("x-dreg-example", "x-dreg-test")
    assert isinstance(manifest, Manifest)
    assert manifest.content_type == "application/vnd.docker.distribution.manifest.v2+json"
    assert manifest.config.content_type == "application/vnd.docker.container.image.v1+json"

    config_response = client.get_blob("x-dreg-example", manifest.config.digest)
    assert config_response.headers["Docker-Content-Digest"] == manifest.config.digest
    config_data = config_response.json()
    assert isinstance(config_data, dict)

    pull = docker_client.api.pull(
        repository="localhost:5000/x-dreg-example",
        tag="x-dreg-test",
        stream=True,
        decode=True,
    )
    pull_output = list(pull)

    tag = "localhost:5000/x-dreg-example:x-dreg-test"
    expected_statuses = {
        "Status: Downloaded newer image for " + tag,
        "Status: Image is up to date for " + tag,
    }

    errors = [evt for evt in pull_output if "error" in evt]
    assert errors == []

    assert {evt.get("status") for evt in pull_output} & expected_statuses
