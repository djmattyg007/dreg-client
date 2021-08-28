from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .client import Client
from .repository import Repository


if TYPE_CHECKING:
    from requests_toolbelt.sessions import BaseUrlSession

    from ._types import RequestsAuth
    from .auth_service import AuthService


class Registry:
    def __init__(self, client: Client) -> None:
        self._client = client
        self._repositories = {}
        self._repositories_by_namespace = {}

    @classmethod
    def build_with_client(
        cls,
        session: BaseUrlSession,
        *,
        auth_service: Optional[AuthService] = None,
    ) -> Registry:
        return cls(Client(session, auth_service=auth_service))

    @classmethod
    def build_with_manual_client(
        cls, base_url: str, *, auth: RequestsAuth = None, auth_service: Optional[AuthService] = None
    ) -> Registry:
        return cls(Client.build_with_session(base_url, auth=auth, auth_service=auth_service))

    def namespaces(self):
        if not self._repositories:
            self.refresh()

        return list(self._repositories_by_namespace.keys())

    def repository(self, repository: str, namespace: Optional[str] = None) -> Repository:
        if "/" in repository:
            if namespace is not None:
                raise RuntimeError("Cannot specify namespace twice.")
            namespace, repository = repository.split("/", 1)

        return Repository(self._client, repository, namespace=namespace)

    def repositories(self, namespace=None):
        if not self._repositories:
            self.refresh()

        if namespace:
            return self._repositories_by_namespace[namespace]

        return self._repositories

    def refresh(self) -> None:
        repositories = self._client.catalog()["repositories"]
        for name in repositories:
            try:
                ns, repo = name.split("/", 1)
            except ValueError:
                ns = None
                repo = name

            r = Repository(self._client, repo, namespace=ns)

            if ns is None:
                ns = "library"

            self._repositories_by_namespace.setdefault(ns, {})
            self._repositories_by_namespace[ns][name] = r
            self._repositories[name] = r


__all__ = ("Registry",)
