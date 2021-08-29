from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Sequence

from .client import Client
from .manifest import ManifestParseOutput


if TYPE_CHECKING:
    from requests import Response


class Repository:
    def __init__(self, client: Client, repository: str, namespace: Optional[str] = None):
        self._client: Client = client
        self.repository: str = repository
        self.namespace: Optional[str] = namespace

        self._tags = None

    @property
    def name(self) -> str:
        if self.namespace:
            return f"{self.namespace}/{self.repository}"
        return self.repository

    def tags(self) -> Sequence[str]:
        if self._tags is None:
            self.refresh()

        return self._tags

    def check_manifest(self, reference: str) -> Optional[str]:
        return self._client.check_manifest(self.name, reference)

    def get_manifest(self, reference: str) -> ManifestParseOutput:
        """
        Return a manifest for a given reference (a tag or a digest)
        """
        return self._client.get_manifest(self.name, reference)

    def delete_manifest(self, digest: str) -> Response:
        return self._client.delete_manifest(self.name, digest)

    def get_blob(self, digest: str) -> Response:
        return self._client.get_blob(self.name, digest)

    def delete_blob(self, digest: str) -> Response:
        return self._client.delete_blob(self.name, digest)

    def refresh(self) -> None:
        response = self._client.get_repository_tags(self.name)
        self._tags = tuple(response["tags"])

    def __repr__(self):
        return f"Repository({self.name})"


__all__ = ("Repository",)
