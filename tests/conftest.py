from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, cast

import pytest
import requests
from docker import DockerClient, from_env
from docker.models.containers import Container
from requests import exceptions


DockerJsonBlob = Dict[str, Any]


@pytest.fixture(scope="session")
def tests_dir() -> Path:
    return Path(__file__).parent


@pytest.fixture(scope="session")
def fixtures_dir(tests_dir: Path) -> Path:
    return tests_dir / "fixtures"


@pytest.fixture
def manifest_v1(fixtures_dir: Path) -> DockerJsonBlob:
    fixture_file = fixtures_dir / "manifest-v1.json"
    data = json.loads(fixture_file.read_text(encoding="utf-8"))
    return cast(DockerJsonBlob, data)


@pytest.fixture
def blob_container_image_v1(fixtures_dir: Path) -> DockerJsonBlob:
    fixture_file = fixtures_dir / "blob-container-image-v1.json"
    data = json.loads(fixture_file.read_text(encoding="utf-8"))
    return cast(DockerJsonBlob, data)


@pytest.fixture(scope="session")
def docker_client() -> DockerClient:
    return from_env()


def wait_till_up(url: str, attempts: int) -> None:
    for i in range(attempts):
        try:
            requests.get(url)
            return
        except exceptions.ConnectionError:
            time.sleep(0.1 * 2 ** i)
    else:
        requests.get(url)


@pytest.fixture
def registry(docker_client: DockerClient):
    docker_client.images.pull("registry", "2.7")
    container: Container = docker_client.containers.create(
        "registry:2.7",
        ports={
            5000: 5000,
        },
    )
    try:
        container.start()
        wait_till_up("http://localhost:5000", 3)
        try:
            yield
        finally:
            container.stop()
    finally:
        container.remove(v=True, force=True)
