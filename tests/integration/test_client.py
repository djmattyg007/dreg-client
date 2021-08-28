from pathlib import Path

from dreg_client import Client


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_base_client(registry):
    client = Client.build_with_session("http://localhost:5000/v2/")
    assert client.catalog() == {"repositories": []}


def test_base_client_edit_manifest(docker_client, registry):
    client = Client.build_with_session("http://localhost:5000/v2/")

    docker_client.images.build(
        path=str(FIXTURES_DIR / "base"),
        tag="localhost:5000/x-dreg-example:x-dreg-test",
    )

    docker_client.images.push(
        repository="localhost:5000/x-dreg-example",
        tag="x-dreg-test",
    )

    tags_response = client.get_repository_tags("x-dreg-example")
    assert tags_response["name"] == "x-dreg-example"
    assert sorted(tags_response["tags"]) == ["x-dreg-test"]

    manifest = client.get_manifest("x-dreg-example", "x-dreg-test")
    assert manifest.content["name"] == "x-dreg-example"
    assert manifest.content["tag"] == "x-dreg-test"

    pull = docker_client.api.pull(
        repository="localhost:5000/x-dreg-example",
        tag="x-dreg-test",
        stream=True,
        decode=True,
    )

    pull = list(pull)
    tag = "localhost:5000/x-dreg-example:x-dreg-test"

    expected_statuses = {
        "Status: Downloaded newer image for " + tag,
        "Status: Image is up to date for " + tag,
    }

    errors = [evt for evt in pull if "error" in evt]
    assert errors == []

    assert {evt.get("status") for evt in pull} & expected_statuses
