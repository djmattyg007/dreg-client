import time

import docker
import pytest
import requests
from requests import exceptions


@pytest.fixture(scope="session")
def docker_client():
    return docker.from_env()


def wait_till_up(url, attempts):
    for i in range(attempts - 1):
        try:
            requests.get(url)
            return
        except exceptions.ConnectionError:
            time.sleep(0.1 * 2 ** i)
    else:
        requests.get(url)


@pytest.fixture
def registry(docker_client):
    cli = docker_client
    cli.pull("registry", "2")
    cont = cli.create_container(
        "registry:2",
        ports=[5000],
        host_config=cli.create_host_config(
            port_bindings={
                5000: 5000,
            },
        ),
    )
    try:
        cli.start(cont)
        wait_till_up("http://localhost:5000", 3)
        try:
            yield
        finally:
            cli.stop(cont)
    finally:
        cli.remove_container(cont, v=True, force=True)
