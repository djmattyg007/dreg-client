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
        tag="localhost:5000/x-drc-example:x-drc-test",
    )

    docker_client.images.push(
        repository="localhost:5000/x-drc-example",
        tag="x-drc-test",
    )

    tags_response = client.get_repository_tags("x-drc-example")
    assert tags_response["name"] == "x-drc-example"
    assert sorted(tags_response["tags"]) == ["x-drc-test"]

    manifest = client.get_manifest("x-drc-example", "x-drc-test")
    assert manifest.content["name"] == "x-drc-example"
    assert manifest.content["tag"] == "x-drc-test"

    pull = docker_client.api.pull(
        repository="localhost:5000/x-drc-example",
        tag="x-drc-test",
        stream=True,
        decode=True,
    )

    pull = list(pull)
    tag = "localhost:5000/x-drc-example:x-drc-test"

    expected_statuses = {
        "Status: Downloaded newer image for " + tag,
        "Status: Image is up to date for " + tag,
    }

    errors = [evt for evt in pull if "error" in evt]
    assert errors == []

    assert {evt.get("status") for evt in pull} & expected_statuses
