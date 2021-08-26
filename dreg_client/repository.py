from typing import Optional

from .client import Client
from .manifest import Manifest


class Repository:
    def __init__(self, client: Client, repository: str, namespace: Optional[str] = None):
        self._client: Client = client
        self.repository: str = repository
        self.namespace: Optional[str] = namespace

        self._tags = None

    @property
    def name(self):
        if self.namespace:
            return f"{self.namespace}/{self.repository}"
        return self.repository

    def tags(self):
        if self._tags is None:
            self.refresh()

        return self._tags

    def manifest(self, reference: str) -> Manifest:
        """
        Return a manifest for a given reference (a tag or a digest)
        """
        return self._client.get_manifest(self.name, reference)

    def delete_manifest(self, digest):
        return self._client.delete_manifest(self.name, digest)

    def refresh(self):
        response = self._client.get_repository_tags(self.name)
        self._tags = response["tags"]

    def __repr__(self):
        return "Repository({name})".format(name=self.name)


__all__ = ("Repository",)
