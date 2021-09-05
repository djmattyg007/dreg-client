from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, AbstractSet, Iterable, Optional, Sequence

from .manifest import (
    DigestMixin,
    ImageConfig,
    ImageLayerRef,
    Manifest,
    ManifestList,
    ManifestRef,
    Platform,
)


if TYPE_CHECKING:
    from .client import Client


class UnavailableImagePlatformError(Exception):
    def __init__(self, platform: Platform, message: str):
        super().__init__(message)
        self.platform = platform


class UnexpectedImageManifestError(Exception):
    def __init__(self, digest: str, message: str):
        super().__init__(message)
        self.digest = digest


@dataclasses.dataclass(frozen=True)
class PlatformImage(DigestMixin):
    digest: str
    config: ImageConfig = dataclasses.field(compare=False, repr=False)
    layers: Sequence[ImageLayerRef] = dataclasses.field(compare=False, repr=False)

    @property
    def platform_name(self) -> str:
        return self.config.platform_name

    @property
    def image_size(self) -> int:
        return sum(map(lambda layer: layer.size, self.layers))


class Image:
    def __init__(self, client: Client, repo: str, tag: str, manifest_list: ManifestList):
        self._client: Client = client
        self._repo: str = repo
        self._tag: str = tag
        self._manifest_list: ManifestList = manifest_list

    @property
    def repo(self) -> str:
        return self._repo

    @property
    def tag(self) -> str:
        return self._tag

    @property
    def manifest_list(self) -> ManifestList:
        return self._manifest_list

    @property
    def platforms(self) -> AbstractSet[Platform]:
        return frozenset(
            map(
                lambda manifest_ref: manifest_ref.platform,
                self._manifest_list.manifests,
            )
        )

    def get_platform_image(self, platform: Platform, /) -> PlatformImage:
        manifest = self.fetch_manifest_by_platform(platform)
        config = self._client.get_image_config_blob(self._repo, manifest.config.digest)
        return PlatformImage(
            digest=manifest.digest,
            config=config,
            layers=manifest.layers,
        )

    def get_platform_images(self) -> Iterable[PlatformImage]:
        for platform in self.platforms:
            yield self.get_platform_image(platform)

    def _fetch_manifest(self, digest: str, errmsg: str) -> Manifest:
        manifest = self._client.get_manifest(self._repo, digest)
        if not isinstance(manifest, Manifest):
            raise UnexpectedImageManifestError(digest, errmsg)

        return manifest

    def fetch_manifest_by_platform_name(self, platform_name: str, /) -> Manifest:
        matching_manifest_ref: Optional[ManifestRef] = None
        for manifest_ref in self._manifest_list.manifests:
            if manifest_ref.platform_name == platform_name:
                matching_manifest_ref = manifest_ref
                break

        if matching_manifest_ref is None:
            raise UnavailableImagePlatformError(
                Platform.from_name(platform_name),
                "No manifest available for the selected platform in this image.",
            )

        return self._fetch_manifest(
            matching_manifest_ref.digest,
            "The digest matched by the selected platform did not represent a single platform manifest.",
        )

    def fetch_manifest_by_platform(self, platform: Platform, /) -> Manifest:
        matching_manifest_ref: Optional[ManifestRef] = None
        for manifest_ref in self._manifest_list.manifests:
            if manifest_ref.platform == platform:
                matching_manifest_ref = manifest_ref
                break

        if matching_manifest_ref is None:
            raise UnavailableImagePlatformError(
                platform,
                "No manifest available for the selected platform in this image.",
            )

        return self._fetch_manifest(
            matching_manifest_ref.digest,
            "The digest matched by the selected platform did not represent a single platform manifest.",
        )

    def fetch_manifest_by_digest(self, digest: str, /) -> Manifest:
        return self._fetch_manifest(
            digest, "The specified digest did not represent a single platform manifest."
        )


__all__ = (
    "Image",
    "PlatformImage",
    "UnavailableImagePlatformError",
    "UnexpectedImageManifestError",
)
