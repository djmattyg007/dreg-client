import json
import re
from datetime import datetime, timedelta
from typing import Any, Callable, Mapping, Tuple
from uuid import uuid4

import pytest
import responses
from freezegun import freeze_time

from dreg_client.auth_service import (
    AuthService,
    AuthServiceFailure,
    AuthToken,
    DockerTokenAuthService,
    make_expires_at,
)


# TODO: This should be importable directly from the responses package
CallbackResponseReturn = Tuple[int, Mapping[str, str], str]


def cbreq(cb: Callable[[], Mapping[str, Any]]) -> Callable[..., CallbackResponseReturn]:
    def inner(*args) -> CallbackResponseReturn:
        result = cb()
        return 200, {"Content-Type": "application/json"}, json.dumps(result)

    return inner


@pytest.fixture
def auth_service() -> DockerTokenAuthService:
    service = DockerTokenAuthService.build_with_session(
        "https://auth.example.com:5000/token",
        "registry.example.com",
    )
    assert isinstance(service, DockerTokenAuthService)
    assert isinstance(service, AuthService)
    return service


@pytest.mark.parametrize(
    ("validity_duration", "expires_at"),
    (
        (-56, 1630644331),
        (-55, 1630644331),
        (-54, 1630644331),
        (-1, 1630644331),
        (0, 1630644331),
        (1, 1630644331),
        (4, 1630644331),
        (5, 1630644331),
        (6, 1630644331),
        (42, 1630644331),
        (50, 1630644331),
        (53, 1630644331),
        (54, 1630644331),
        (55, 1630644331),
        (56, 1630644331),
        (59, 1630644331),
        (60, 1630644331),
        (61, 1630644332),
        (62, 1630644333),
        (90, 1630644361),
        (120, 1630644391),
        (300, 1630644571),
    ),
)
def test_make_expires_at(validity_duration: int, expires_at: int):
    time_dest = datetime.utcfromtimestamp(1630644276)
    with freeze_time(time_dest):
        actual = make_expires_at(validity_duration)
        assert actual == expires_at


@pytest.mark.parametrize(
    ("validity_duration", "time_to_pass", "expired"),
    (
        (1, 1, False),
        (1, 2, False),
        (1, 24, False),
        (1, 54, False),
        (1, 55, True),
        (1, 56, True),
        (1, 59, True),
        (1, 60, True),
        (1, 61, True),
        (2, 1, False),
        (2, 2, False),
        (2, 35, False),
        (2, 54, False),
        (2, 55, True),
        (2, 56, True),
        (2, 60, True),
        (2, 61, True),
        (4, 1, False),
        (4, 4, False),
        (4, 5, False),
        (4, 54, False),
        (4, 55, True),
        (4, 56, True),
        (4, 60, True),
        (5, 2, False),
        (5, 4, False),
        (5, 5, False),
        (5, 6, False),
        (5, 54, False),
        (5, 55, True),
        (5, 56, True),
        (5, 60, True),
        (30, 31, False),
        (55, 20, False),
        (55, 54, False),
        (55, 55, True),
        (55, 59, True),
        (55, 60, True),
        (55, 61, True),
        (60, 14, False),
        (60, 54, False),
        (60, 55, True),
        (60, 59, True),
        (60, 60, True),
        (60, 61, True),
        (61, 54, False),
        (61, 55, False),
        (61, 56, True),
        (61, 60, True),
        (61, 61, True),
        (61, 62, True),
        (64, 54, False),
        (64, 55, False),
        (64, 56, False),
        (64, 58, False),
        (64, 59, True),
        (64, 60, True),
        (64, 61, True),
        (64, 62, True),
        (64, 64, True),
        (64, 65, True),
        (65, 54, False),
        (65, 55, False),
        (65, 56, False),
        (65, 58, False),
        (65, 59, False),
        (65, 60, True),
        (65, 61, True),
        (65, 62, True),
        (65, 65, True),
        (65, 66, True),
        (66, 54, False),
        (66, 55, False),
        (66, 56, False),
        (66, 58, False),
        (66, 59, False),
        (66, 60, False),
        (66, 61, True),
        (66, 62, True),
        (66, 65, True),
        (66, 66, True),
        (66, 67, True),
        (90, 30, False),
        (90, 54, False),
        (90, 55, False),
        (90, 56, False),
        (90, 60, False),
        (90, 90, True),
    ),
)
def test_has_auth_token_expired(validity_duration: int, time_to_pass: int, expired: bool):
    time_dest = datetime.utcfromtimestamp(1662114792)
    with freeze_time(time_dest) as frozen_datetime:
        token = AuthToken(
            token=str(uuid4()),
            validity_duration=validity_duration,
            expires_at=make_expires_at(validity_duration),
        )

        frozen_datetime.tick(timedelta(seconds=time_to_pass))

        assert token.has_expired == expired


def test_build_auth_service_with_session():
    service = DockerTokenAuthService.build_with_session(
        "https://auth.example.com:5000/token",
        "registry.example.com",
    )
    assert isinstance(service, DockerTokenAuthService)
    assert isinstance(service, AuthService)


@pytest.mark.parametrize("token_field", ("token", "access_token"))
@pytest.mark.parametrize("scope", ("registry:catalog:*", "repository:debian:*"))
def test_request_token_success(auth_service: DockerTokenAuthService, token_field: str, scope: str):
    with responses.RequestsMock() as rsps:
        token = str(uuid4())
        result = {token_field: token, "expires_in": 60}

        rsps.add(
            rsps.GET,
            f"https://auth.example.com:5000/token?scope={scope}&service=registry.example.com",
            json=result,
            match_querystring=True,
        )

        requested_token = auth_service.request_token(scope)
        assert requested_token == token


@pytest.mark.parametrize("token_field", ("token", "access_token"))
@pytest.mark.parametrize("scope", ("registry:catalog:*", "repository:debian:*"))
def test_repeat_request_token(auth_service: DockerTokenAuthService, token_field: str, scope: str):
    with responses.RequestsMock() as rsps:
        tokens = [
            str(uuid4()),
            str(uuid4()),
        ]

        def mkbody() -> Mapping[str, Any]:
            token = tokens.pop(0)
            return {token_field: token, "expires_in": 60}

        rsps.add_callback(
            rsps.GET,
            f"https://auth.example.com:5000/token?scope={scope}&service=registry.example.com",
            callback=cbreq(mkbody),
            match_querystring=True,
        )

        with freeze_time() as frozen_datetime:
            orig_token = auth_service.request_token(scope)

            tick_length = timedelta(seconds=5)
            for _ in range(11):
                re_token = auth_service.request_token(scope)
                assert re_token == orig_token
                frozen_datetime.tick(tick_length)

            next_token = auth_service.request_token(scope)
            assert next_token != orig_token

            frozen_datetime.tick(timedelta(seconds=10))
            re_next_token = auth_service.request_token(scope)
            assert re_next_token == next_token

        assert len(tokens) == 0
        assert len(rsps.calls) == 2


@pytest.mark.parametrize("token_field", ("token", "access_token"))
def test_repeat_request_token_different_scope(
    auth_service: DockerTokenAuthService, token_field: str
):
    with responses.RequestsMock() as rsps:
        catalog_token = str(uuid4())
        catalog_scope = "registry:catalog:*"
        repo_token = str(uuid4())
        repo_scope = "repository:debian:*"

        rsps.add(
            rsps.GET,
            f"https://auth.example.com:5000/token?scope={catalog_scope}&service=registry.example.com",
            json={token_field: catalog_token},
            match_querystring=True,
        )
        rsps.add(
            rsps.GET,
            f"https://auth.example.com:5000/token?scope={repo_scope}&service=registry.example.com",
            json={token_field: repo_token},
            match_querystring=True,
        )

        with freeze_time() as frozen_datetime:
            requested_catalog_token = auth_service.request_token(catalog_scope)
            assert requested_catalog_token == catalog_token

            requested_repo_token = auth_service.request_token(repo_scope)
            assert requested_repo_token == repo_token

            tick_length = timedelta(seconds=5)
            for _ in range(10):
                frozen_datetime.tick(tick_length)
                re_requested_catalog_token = auth_service.request_token(catalog_scope)
                assert re_requested_catalog_token == catalog_token

                re_requested_repo_token = auth_service.request_token(repo_scope)
                assert re_requested_repo_token == repo_token

        assert len(rsps.calls) == 2


def test_auth_failure(auth_service: DockerTokenAuthService):
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.GET,
            "https://auth.example.com:5000/token?scope=registry:catalog:*&service=registry.example.com",
            status=401,
            headers={
                "Www-Authenticate": 'Bearer realm="https://auth.example.com:5000/token",service="registry.example.com",scope="registry:catalog:*"',
            },
        )

        errmsg = "^" + re.escape("Failed to retrieve valid auth token.") + "$"
        with pytest.raises(AuthServiceFailure, match=errmsg) as exc_info:
            auth_service.request_token("registry:catalog:*")

        assert isinstance(exc_info.value.__cause__, Exception) is True


def test_invalid_json(auth_service: DockerTokenAuthService):
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.GET,
            "https://auth.example.com:5000/token?scope=registry:catalog:*&service=registry.example.com",
            body='{"test"}',
            headers={
                "Content-Type": "application/json",
            },
        )

        errmsg = "^" + re.escape("Failed to retrieve valid auth token.") + "$"
        with pytest.raises(AuthServiceFailure, match=errmsg) as exc_info:
            auth_service.request_token("registry:catalog:*")

        assert isinstance(exc_info.value.__cause__, ValueError) is True


def test_missing_token(auth_service: DockerTokenAuthService):
    with responses.RequestsMock() as rsps:
        rsps.add(
            rsps.GET,
            "https://auth.example.com:5000/token?scope=registry:catalog:*&service=registry.example.com",
            json={"toke": str(uuid4())},
        )

        errmsg = "^" + re.escape("Failed to retrieve valid auth token.") + "$"
        with pytest.raises(AuthServiceFailure, match=errmsg) as exc_info:
            auth_service.request_token("registry:catalog:*")

        assert exc_info.value.__cause__ is None
