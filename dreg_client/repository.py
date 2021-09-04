from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Sequence, Union

from ._synth import synth_manifest_list_from_manifest
from .client import Client
from .image import Image
from .manifest import LegacyManifest, ManifestList, ManifestParseOutput


if TYPE_CHECKING:
    from requests import Response


class LegacyImageRequestError(Exception):
    pass


class Repository:
    def __init__(self, client: Client, repository: str, namespace: Optional[str] = None):
        self._client: Client = client
        self.repository: str = repository
        self.namespace: Optional[str] = namespace

        self._tags: Optional[Sequence[str]] = None

    @property
    def name(self) -> str:
        if self.namespace:
            return f"{self.namespace}/{self.repository}"
        return self.repository

    def tags(self) -> Sequence[str]:
        if self._tags is None:
            self.refresh()

        if self._tags is None:  # pragma: no cover
            raise TypeError("Loading repository tags failed.")

        return self._tags

    def get_image(
        self, tag: str, /, *, raise_on_legacy: bool = True
    ) -> Union[Image, LegacyManifest]:
        manifest = self.get_manifest(tag)
        if isinstance(manifest, LegacyManifest):
            if raise_on_legacy:
                raise LegacyImageRequestError()
            return manifest
        if isinstance(manifest, ManifestList):
            return Image(self._client, self.name, tag, manifest)

        # We need to synthesise a manifest list for this image
        image_config = self._client.get_image_config_blob(self.name, manifest.config.digest)

        manifest_list = synth_manifest_list_from_manifest(manifest, image_config)

        return Image(self._client, self.name, tag, manifest_list)

    def check_manifest(self, reference: str, /) -> Optional[str]:
        return self._client.check_manifest(self.name, reference)

    def get_manifest(self, reference: str) -> ManifestParseOutput:
        """
        Return a manifest for a given reference (a tag or a digest)
        """
        return self._client.get_manifest(self.name, reference)

    def delete_manifest(self, digest: str, /) -> Response:
        return self._client.delete_manifest(self.name, digest)

    def get_blob(self, digest: str, /) -> Response:
        return self._client.get_blob(self.name, digest)

    def delete_blob(self, digest: str, /) -> Response:
        return self._client.delete_blob(self.name, digest)

    def refresh(self) -> None:
        response = self._client.get_repository_tags(self.name)
        if response["tags"] is None:
            self._tags = ()
        else:
            self._tags = tuple(response["tags"])

    def __repr__(self) -> str:
        return f"Repository({self.name})"


__all__ = (
    "LegacyImageRequestError",
    "Repository",
)
