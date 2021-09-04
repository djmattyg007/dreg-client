from __future__ import annotations

import dataclasses
import logging
import time
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from requests_toolbelt.sessions import BaseUrlSession


if TYPE_CHECKING:
    from typing import Dict

    from ._types import RequestsAuth


logger = logging.getLogger(__name__)


def make_expires_at(validity_duration: int) -> int:
    return int(time.time()) + max(validity_duration - 5, 55)


@dataclasses.dataclass(frozen=True, eq=False)
class AuthToken:
    token: str
    validity_duration: int
    expires_at: int

    @property
    def has_expired(self) -> bool:
        return time.time() >= self.expires_at


class AuthServiceFailure(Exception):  # noqa: N818
    pass


@runtime_checkable
class AuthService(Protocol):
    def request_token(self, scope: str) -> str:
        ...


class DockerTokenAuthService(AuthService):
    def __init__(self, session: BaseUrlSession, /):
        self._session: BaseUrlSession = session
        self._saved_tokens: Dict[str, AuthToken] = {}

    @classmethod
    def build_with_session(
        cls, base_url: str, service: str, /, *, auth: RequestsAuth = None
    ) -> DockerTokenAuthService:
        session = BaseUrlSession(base_url)
        session.params["service"] = service
        session.auth = auth
        return DockerTokenAuthService(session)

    def request_token(self, scope: str, /) -> str:
        saved_token = self._saved_tokens.get(scope)
        if saved_token:
            if saved_token.has_expired:
                self._saved_tokens.pop(scope, None)
            else:
                return saved_token.token

        response = self._session.get("", params={"scope": scope})
        try:
            response.raise_for_status()
        except Exception as exc:
            raise AuthServiceFailure("Failed to retrieve valid auth token.") from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise AuthServiceFailure("Failed to retrieve valid auth token.") from exc

        token_value = data.get("token", data.get("access_token"))
        if not token_value:
            raise AuthServiceFailure("Failed to retrieve valid auth token.")

        validity_duration = data.get("expires_in", 60)

        token = AuthToken(
            token=token_value,
            validity_duration=validity_duration,
            expires_at=make_expires_at(validity_duration),
        )
        self._saved_tokens[scope] = token
        return token.token


__all__ = ("AuthService", "AuthServiceFailure", "DockerTokenAuthService")
