from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Sequence, Union

from .client import Client
from .image import Image
from .manifest import LegacyManifest, ManifestList, ManifestParseOutput, ManifestRef
from .schemas import schema_2_list


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

    def get_image(self, tag: str) -> Union[Image, LegacyManifest]:
        manifest = self.get_manifest(tag)
        if isinstance(manifest, LegacyManifest):
            return manifest
        if isinstance(manifest, ManifestList):
            return Image(self._client, self.name, tag, manifest)

        # Synthesise a manifest list
        image_config = self._client.get_image_config_blob(self.name, manifest.config.digest)

        import json
        from collections import OrderedDict
        from hashlib import sha256

        manifest_ref_platform = OrderedDict()
        manifest_ref_platform["architecture"] = image_config.platform.architecture
        manifest_ref_platform["os"] = image_config.platform.os
        if image_config.platform.variant:
            manifest_ref_platform["manifests"] = image_config.platform.variant

        manifest_ref_data = OrderedDict()
        manifest_ref_data["mediaType"] = manifest.content_type
        manifest_ref_data["digest"] = manifest.digest
        manifest_ref_data["size"] = manifest.content_length
        manifest_ref_data["platform"] = manifest_ref_platform

        manifest_list_data = OrderedDict()
        manifest_list_data["mediaType"] = schema_2_list
        manifest_list_data["schemaVersion"] = 2
        manifest_list_data["manifests"] = [manifest_ref_data]

        manifest_list_json = json.dumps(manifest_list_data, indent=3)
        digest_hash = sha256()
        digest_hash.update(manifest_list_json)
        digest = digest_hash.hexdigest()
        content_length = len(manifest_list_json)

        manifest_ref = ManifestRef(
            digest=manifest.digest,
            content_type=manifest.content_type,
            size=manifest.content_length,
            platform=image_config.platform,
        )
        manifest_list = ManifestList(
            digest=digest,
            content_type=schema_2_list,
            content_length=content_length,
            manifests={manifest_ref},
        )

        return Image(self._client, self.name, tag, manifest_list)

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
