from typing import Optional

from .client import Client
from .repository import Repository


class Registry:
    def __init__(self, client: Client):
        self._client = client
        self._repositories = {}
        self._repositories_by_namespace = {}

    @classmethod
    def build_with_client(
        cls,
        host: str,
        verify_ssl: Optional[bool] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        api_timeout: Optional[int] = None,
        auth_service_url: str = "",
    ):
        return cls(
            Client(
                host=host,
                verify_ssl=verify_ssl,
                username=username,
                password=password,
                api_timeout=api_timeout,
                auth_service_url=auth_service_url,
            )
        )

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
