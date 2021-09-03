import json
from collections import OrderedDict
from hashlib import sha256
from typing import Any, Dict

from .manifest import ImageConfig, Manifest, ManifestList, ManifestRef
from .schemas import schema_2_list


def synth_manifest_list_from_manifest(
    manifest: Manifest, image_config: ImageConfig
) -> ManifestList:
    manifest_ref_platform: Dict[str, Any] = OrderedDict()
    manifest_ref_platform["architecture"] = image_config.platform.architecture
    manifest_ref_platform["os"] = image_config.platform.os
    if image_config.platform.variant:
        manifest_ref_platform["manifests"] = image_config.platform.variant

    manifest_ref_data: Dict[str, Any] = OrderedDict()
    manifest_ref_data["mediaType"] = manifest.content_type
    manifest_ref_data["digest"] = manifest.digest
    manifest_ref_data["size"] = manifest.content_length
    manifest_ref_data["platform"] = manifest_ref_platform

    manifest_list_data: Dict[str, Any] = OrderedDict()
    manifest_list_data["mediaType"] = schema_2_list
    manifest_list_data["schemaVersion"] = 2
    manifest_list_data["manifests"] = [manifest_ref_data]

    manifest_list_json = json.dumps(manifest_list_data, indent=3)
    digest_hash = sha256()
    digest_hash.update(manifest_list_json.encode())
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

    return manifest_list
