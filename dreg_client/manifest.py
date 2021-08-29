from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Mapping, Optional, Sequence, Union

from dataclasses import dataclass, field

from .schemas import known_manifest_content_types, legacy_manifest_content_types, schema_2, schema_2_list


if TYPE_CHECKING:
    from requests import Response


@dataclass(frozen=True)
class Platform:
    os: str
    architecture: str
    variant: Optional[str]

    @property
    def name(self) -> str:
        return "/".join(filter(None, (self.os, self.architecture, self.variant)))

    @classmethod
    def extract(cls, data: Mapping[str, Any]) -> Platform:
        return Platform(
            os=data["os"],
            architecture=data["architecture"],
            variant=data.get("variant"),
        )


@dataclass(frozen=True)
class ImageHistoryItem:
    created_at: str
    created_by: str = field(repr=False)
    empty_layer: bool = field(compare=False)
    comment: str = field(compare=False, repr=False)


@dataclass(frozen=True)
class ImageConfig:
    digest: str
    created_at: str = field(compare=False)
    config: Mapping[str, Any] = field(compare=False, repr=False)
    history: Sequence[ImageHistoryItem] = field(compare=False, repr=False)
    rootfs: Mapping[str, Any] = field(compare=False, repr=False)
    platform: Platform = field(compare=False)

    @property
    def platform_name(self) -> str:
        return self.platform.name


class UnusableImageConfigBlobResponseError(Exception):
    def __init__(self, response: Response, message: str):
        super().__init__(message)
        self.response = response


class UnusableImageConfigBlobPayloadError(Exception):
    def __init__(self, response: Response, payload: Any, message: str):
        super().__init__(message)
        self.response = response
        self.payload = payload


def parse_image_config_blob_response(response: Response) -> ImageConfig:
    digest = response.headers.get("Docker-Content-Digest")
    if not digest:
        raise UnusableImageConfigBlobResponseError(response, "No digest specified in response headers.")

    data = response.json()
    if not isinstance(data, dict):
        raise UnusableImageConfigBlobPayloadError(response, data, "Non-dictionary payload returned.")

    history_items: List[ImageHistoryItem] = []
    for history_item_data in data["history"]:
        empty_layer = history_item_data.get("empty_layer", False)
        comment = history_item_data.get("comment", "")

        history_items.append(ImageHistoryItem(
            created_at=history_item_data["created"],
            created_by=history_item_data["created_by"],
            empty_layer=empty_layer,
            comment=comment,
        ))

    return ImageConfig(
        digest=digest,
        created_at=data["created"],
        config=data["config"],
        history=tuple(history_items),
        rootfs=data["rootfs"],
        platform=Platform.extract(data),
    )


@dataclass(frozen=True)
class ImageLayerRef:
    digest: str
    content_type: str
    size: int


@dataclass(frozen=True)
class ImageConfigRef:
    digest: str
    content_type: str
    size: int


@dataclass(frozen=True)
class Manifest:
    digest: str
    content_type: str
    config: ImageConfigRef = field(compare=False, repr=False)
    layers: Sequence[ImageLayerRef] = field(compare=False, repr=False)


@dataclass(frozen=True)
class ManifestRef:
    digest: str
    content_type: str
    size: int
    platform: Platform

    @property
    def platform_name(self) -> str:
        return self.platform.name


@dataclass(frozen=True)
class ManifestList:
    digest: str
    content_type: str
    manifests: Sequence[ManifestRef] = field(compare=False, repr=False)


@dataclass(frozen=True)
class LegacyManifest:
    digest: str
    content_type: str
    content: Mapping = field(compare=False, repr=False)


class UnusableManifestResponseError(Exception):
    def __init__(self, response: Response, message: str):
        super().__init__(message)
        self.response = response


class UnusableManifestPayloadError(Exception):
    def __init__(self, response: Response, payload: Any, message: str):
        super().__init__(message)
        self.response = response
        self.payload = payload


ManifestParseOutput = Union[ManifestList, Manifest, LegacyManifest]


def parse_manifest_response(response: Response) -> ManifestParseOutput:
    content_type = response.headers.get("Content-Type")
    if content_type not in known_manifest_content_types:
        raise UnusableManifestResponseError(response, "Unknown Content-Type header in response.")
    digest = response.headers.get("Docker-Content-Digest")
    if not digest:
        raise UnusableManifestResponseError(response, "No digest specified in response headers")

    data = response.json()
    if not isinstance(data, dict):
        raise UnusableManifestPayloadError(response, data, "Non-dictionary payload returned.")

    if content_type in legacy_manifest_content_types:
        return LegacyManifest(
            digest=digest,
            content_type=content_type,
            content=data,
        )

    if data.get("schemaVersion") != 2:
        raise UnusableManifestPayloadError(response, data, "Unknown schema version in payload.")

    if content_type == schema_2:
        if data.get("mediaType") != content_type:
            raise UnusableManifestPayloadError(response, data, "Mismatched media type between headers and payload.")

        config_data = data["config"]
        layers_data = data["layers"]

        config = ImageConfigRef(
            digest=config_data["digest"],
            content_type=config_data["mediaType"],
            size=config_data["size"],
        )

        layers: List[ImageLayerRef] = []
        for layer_data in layers_data:
            layers.append(ImageLayerRef(
                digest=layer_data["digest"],
                content_type=layer_data["mediaType"],
                size=layer_data["size"],
            ))

        return Manifest(
            digest=digest,
            content_type=content_type,
            config=config,
            layers=tuple(layers),
        )

    if content_type == schema_2_list:
        if data.get("mediaType") != content_type:
            raise UnusableManifestPayloadError(response, data, "Mismatched media type between headers and payload.")

        manifests_data = data["manifests"]

        manifests: List[ManifestRef] = []
        for manifest_data in manifests_data:
            manifests.append(ManifestRef(
                digest=manifest_data["digest"],
                content_type=manifest_data["mediaType"],
                size=manifest_data["size"],
                platform=Platform.extract(manifest_data["platform"]),
            ))

        return ManifestList(
            digest=digest,
            content_type=content_type,
            manifests=tuple(manifests),
        )

    raise UnusableManifestResponseError(response, "Unknown Content-Type header in response.")


__all__ = (
    "ImageConfig",
    "ImageConfigRef",
    "ImageHistoryItem",
    "ImageLayerRef",
    "LegacyManifest",
    "Manifest",
    "ManifestList",
    "ManifestRef",
    "Platform",
    "UnusableManifestPayloadError",
    "UnusableManifestResponseError",
    "parse_manifest_response",
)
