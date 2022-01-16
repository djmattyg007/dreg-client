from __future__ import annotations

from .auth_service import AuthService, AuthServiceFailure, DockerTokenAuthService
from .client import Client
from .image import Image, PlatformImage, UnavailableImagePlatformError, UnexpectedImageManifestError
from .manifest import (
    ImageConfig,
    ImageHistoryItem,
    InvalidPlatformNameError,
    LegacyManifest,
    Manifest,
    ManifestList,
    Platform,
    UnusableImageConfigBlobPayloadError,
    UnusableImageConfigBlobResponseError,
    UnusableManifestPayloadError,
    UnusableManifestResponseError,
)
from .registry import Registry
from .repository import LegacyImageRequestError, Repository


__version__ = "1.2.0"


__all__ = (
    "AuthService",
    "AuthServiceFailure",
    "Client",
    "DockerTokenAuthService",
    "Image",
    "ImageConfig",
    "ImageHistoryItem",
    "InvalidPlatformNameError",
    "LegacyManifest",
    "LegacyImageRequestError",
    "Manifest",
    "ManifestList",
    "Platform",
    "PlatformImage",
    "Registry",
    "Repository",
    "UnavailableImagePlatformError",
    "UnexpectedImageManifestError",
    "UnusableImageConfigBlobResponseError",
    "UnusableImageConfigBlobPayloadError",
    "UnusableManifestResponseError",
    "UnusableManifestPayloadError",
)
