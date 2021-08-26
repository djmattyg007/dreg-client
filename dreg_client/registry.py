from typing import Optional

from .client import Client
from .repository import Repository


class Registry:
    def __init__(
        self,
        host,
        verify_ssl=None,
        username=None,
        password=None,
        auth_service_url="",
        api_timeout=None,
    ):
        """
        :param host: str, registry URL including scheme
        :param verify_ssl: bool, whether to verify SSL certificate
        :param username: username to use for basic authentication when
          connecting to the registry
        :param password: password to use for basic authentication
        :param auth_service_url: authorization service URL (including scheme)
        :param api_timeout: timeout for external request
        """

        self._base_client = Client(
            host,
            verify_ssl=verify_ssl,
            username=username,
            password=password,
            auth_service_url=auth_service_url,
            api_timeout=api_timeout,
        )
        self._repositories = {}
        self._repositories_by_namespace = {}

    def namespaces(self):
        if not self._repositories:
            self.refresh()

        return list(self._repositories_by_namespace.keys())

    def repository(self, repository: str, namespace: Optional[str] = None) -> Repository:
        if "/" in repository:
            if namespace is not None:
                raise RuntimeError("Cannot specify namespace twice.")
            namespace, repository = repository.split("/", 1)

        return Repository(self._base_client, repository, namespace=namespace)

    def repositories(self, namespace=None):
        if not self._repositories:
            self.refresh()

        if namespace:
            return self._repositories_by_namespace[namespace]

        return self._repositories

    def refresh(self) -> None:
        repositories = self._base_client.catalog()["repositories"]
        for name in repositories:
            try:
                ns, repo = name.split("/", 1)
            except ValueError:
                ns = None
                repo = name

            r = Repository(self._base_client, repo, namespace=ns)

            if ns is None:
                ns = "library"

            self._repositories_by_namespace.setdefault(ns, {})
            self._repositories_by_namespace[ns][name] = r
            self._repositories[name] = r


__all__ = ("Registry",)
