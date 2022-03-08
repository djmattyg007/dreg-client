BASE_CONTENT_TYPE = "application/vnd.docker.distribution.manifest"
OCI_CONTENT_TYPE = "application/vnd.oci.image.manifest"

schema_1 = BASE_CONTENT_TYPE + ".v1+json"
schema_1_signed = BASE_CONTENT_TYPE + ".v1+prettyjws"
schema_2 = BASE_CONTENT_TYPE + ".v2+json"
schema_2_list = BASE_CONTENT_TYPE + ".list.v2+json"
schema_oci = OCI_CONTENT_TYPE + ".v1+json"
schema_oci_list = OCI_CONTENT_TYPE + ".list.v1+json"


legacy_manifest_content_types = frozenset(
    {
        schema_1,
        schema_1_signed,
    }
)
known_manifest_content_types = legacy_manifest_content_types | {
    schema_2,
    schema_2_list,
    schema_oci,
    schema_oci_list,
}


__all__ = (
    "schema_1",
    "schema_1_signed",
    "schema_2",
    "schema_2_list",
    "schema_oci",
    "schema_oci_list",
    "legacy_manifest_content_types",
    "known_manifest_content_types",
)
