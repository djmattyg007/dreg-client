from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict, Optional, Sequence, TypedDict

from requests import HTTPError, RequestException
from requests_toolbelt.sessions import BaseUrlSession

from .manifest import Manifest


if TYPE_CHECKING:
    from requests import Response

    from ._types import RequestsAuth
    from .auth_service import AuthService


logger = logging.getLogger(__name__)


HEADERS = Dict[str, str]

BASE_CONTENT_TYPE = "application/vnd.docker.distribution.manifest"

schema_1_signed = BASE_CONTENT_TYPE + ".v1+prettyjws"
schema_1 = BASE_CONTENT_TYPE + ".v1+json"
schema_2 = BASE_CONTENT_TYPE + ".v2+json"

scope_catalog = "registry:catalog:*"
scope_repo = lambda repo: f"repository:{repo}:*"


class CatalogResponse(TypedDict):
    repositories: Sequence[str]


class TagsResponse(TypedDict):
    name: str
    tags: Optional[Sequence[str]]


class Client:
    def __init__(
        self, session: BaseUrlSession, *, auth_service: Optional[AuthService] = None
    ) -> None:
        if session.auth and auth_service:
            raise ValueError("Cannot supply session.auth and auth_service together.")

        self._session = session
        self._auth_service = auth_service

    @classmethod
    def build_with_session(
        cls, base_url: str, *, auth: RequestsAuth = None, auth_service: Optional[AuthService] = None
    ) -> Client:
        if auth and auth_service:
            raise ValueError("Cannot supply auth and auth_service together.")

        session = BaseUrlSession(base_url)
        if auth:
            session.auth = auth
        return Client(session, auth_service=auth_service)

    def _head(self, url_path: str, scope: str, headers: Optional[HEADERS] = None) -> Response:
        if not headers:
            headers = {}

        if self._auth_service:
            token = self._auth_service.request_token(scope)
            headers["Authorization"] = f"Bearer {token}"

        response = self._session.head(url_path, headers=headers)
        response.raise_for_status()
        return response

    def _get(self, url_path: str, scope: str, headers: Optional[HEADERS] = None) -> Response:
        if not headers:
            headers = {}

        if self._auth_service:
            token = self._auth_service.request_token(scope)
            headers["Authorization"] = f"Bearer {token}"

        response = self._session.get(url_path, headers=headers)
        response.raise_for_status()
        return response

    def _delete(self, url_path: str, scope: str, headers: Optional[HEADERS] = None) -> Response:
        if not headers:
            headers = {}

        if self._auth_service:
            token = self._auth_service.request_token(scope)
            headers["Authorization"] = f"Bearer {token}"

        response = self._session.delete(url_path, headers=headers)
        response.raise_for_status()
        return response

    def check_status(self) -> bool:
        try:
            response = self._get("", scope_catalog)
            response.json()
        except (ValueError, RequestException):
            return False
        else:
            return True

    def catalog(self) -> CatalogResponse:
        response = self._get("_catalog", scope_catalog)
        return response.json()

    def get_repository_tags(self, name: str) -> TagsResponse:
        response = self._get(f"{name}/tags/list", scope_repo(name))
        return response.json()

    def check_manifest(self, name: str, reference: str) -> Optional[str]:
        headers: HEADERS = {
            "Accept": ",".join((schema_1_signed, schema_1)),
        }
        try:
            response = self._head(f"{name}/manifests/{reference}", scope_repo(name), headers=headers)
        except HTTPError as exc:
            if exc.response.status_code == 404:
                return None
            raise

        return response.headers.get("Docker-Content-Digest", None)

    def get_manifest(self, name: str, reference: str) -> Manifest:
        headers: HEADERS = {
            "Accept": ",".join((schema_1_signed, schema_1)),
        }
        response = self._get(f"{name}/manifests/{reference}", scope_repo(name), headers=headers)

        data = response.json()
        return Manifest(
            digest=response.headers["Docker-Content-Digest"],
            content_type=response.headers.get("Content-Type", "application/json"),
            content=data,
        )

    def delete_manifest(self, name: str, digest: str) -> Response:
        response = self._delete(f"{name}/manifests/{digest}", scope_repo(name))
        return response

    def get_blob(self, name: str, digest: str) -> Response:
        response = self._get(f"{name}/blobs/{digest}", scope_repo(name))
        return response

    def delete_blob(self, name: str, digest: str) -> Response:
        response = self._delete(f"{name}/blobs/{digest}", scope_repo(name))
        return response


__all__ = ("Client",)
