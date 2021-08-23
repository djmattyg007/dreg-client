import time

import pytest
import requests
from docker import DockerClient, from_env
from docker.models.containers import Container
from requests import exceptions


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
    cli = docker_client
    cli.images.pull("registry", "2")
    container: Container = cli.containers.create(
        "registry:2",
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
