import dataclasses
import json
import logging

from requests import delete, get

from .AuthorizationService import AuthorizationService


logger = logging.getLogger(__name__)


class CommonBaseClient(object):
    def __init__(self, host, verify_ssl=None, username=None, password=None, api_timeout=None):
        self.host = host

        self.method_kwargs = {}
        if verify_ssl is not None:
            self.method_kwargs["verify"] = verify_ssl
        if username is not None and password is not None:
            self.method_kwargs["auth"] = (username, password)
        if api_timeout is not None:
            self.method_kwargs["timeout"] = api_timeout

    def _http_response(self, url, method, data=None, **kwargs):
        """url -> full target url
        method -> method from requests
        data -> request body
        kwargs -> url formatting args
        """
        header = {"content-type": "application/json"}

        if data:
            data = json.dumps(data)
        path = url.format(**kwargs)
        logger.debug("%s %s", method.__name__.upper(), path)
        response = method(self.host + path, data=data, headers=header, **self.method_kwargs)
        logger.debug("%s %s", response.status_code, response.reason)
        response.raise_for_status()

        return response

    def _http_call(self, url, method, data=None, **kwargs):
        """url -> full target url
        method -> method from requests
        data -> request body
        kwargs -> url formatting args
        """
        response = self._http_response(url, method, data=data, **kwargs)
        if not response.content:
            return {}

        return response.json()


@dataclasses.dataclass(frozen=True)
class _Manifest:
    content: dict
    content_type: str
    digest: str


BASE_CONTENT_TYPE = "application/vnd.docker.distribution.manifest"


class BaseClientV2(CommonBaseClient):
    LIST_TAGS = "/v2/{name}/tags/list"
    MANIFEST = "/v2/{name}/manifests/{reference}"
    BLOB = "/v2/{name}/blobs/{digest}"
    schema_1_signed = BASE_CONTENT_TYPE + ".v1+prettyjws"
    schema_1 = BASE_CONTENT_TYPE + ".v1+json"
    schema_2 = BASE_CONTENT_TYPE + ".v2+json"

    def __init__(self, *args, **kwargs):
        auth_service_url = kwargs.pop("auth_service_url", "")
        super().__init__(*args, **kwargs)
        self.auth = AuthorizationService(
            registry=self.host,
            url=auth_service_url,
            verify=self.method_kwargs.get("verify", True),
            auth=self.method_kwargs.get("auth", None),
            api_timeout=self.method_kwargs.get("api_timeout"),
        )

    def check_status(self):
        self.auth.desired_scope = "registry:catalog:*"
        return self._http_call("/v2/", get)

    def catalog(self):
        self.auth.desired_scope = "registry:catalog:*"
        return self._http_call("/v2/_catalog", get)

    def get_repository_tags(self, name):
        self.auth.desired_scope = "repository:%s:*" % name
        return self._http_call(self.LIST_TAGS, get, name=name)

    def get_digest_and_manifest(self, name, reference):
        m = self.get_manifest(name, reference)
        return m.digest, m.content

    def get_manifest(self, name, reference) -> _Manifest:
        self.auth.desired_scope = "repository:%s:*" % name
        response = self._http_response(
            self.MANIFEST,
            get,
            name=name,
            reference=reference,
            schema=self.schema_1_signed,
        )
        return _Manifest(
            content=response.json(),
            content_type=response.headers.get("Content-Type", "application/json"),
            digest=response.headers.get("Docker-Content-Digest"),
        )

    def delete_manifest(self, name, digest):
        self.auth.desired_scope = "repository:%s:*" % name
        return self._http_call(self.MANIFEST, delete, name=name, reference=digest)

    def delete_blob(self, name, digest):
        self.auth.desired_scope = "repository:%s:*" % name
        return self._http_call(self.BLOB, delete, name=name, digest=digest)

    def _http_response(self, url, method, data=None, content_type=None, schema=None, **kwargs):
        """url -> full target url
        method -> method from requests
        data -> request body
        kwargs -> url formatting args
        """

        if schema is None:
            schema = self.schema_2

        header = {
            "content-type": content_type or "application/json",
            "Accept": schema,
        }

        # Token specific part. We add the token in the header if necessary
        auth = self.auth
        token_required = auth.token_required
        token = auth.token
        desired_scope = auth.desired_scope
        scope = auth.scope

        if token_required:
            if not token or desired_scope != scope:
                logger.debug("Getting new token for scope: %s", desired_scope)
                auth.get_new_token()

            header["Authorization"] = "Bearer %s" % self.auth.token

        if data and not content_type:
            data = json.dumps(data)

        path = url.format(**kwargs)
        logger.debug("%s %s", method.__name__.upper(), path)
        response = method(self.host + path, data=data, headers=header, **self.method_kwargs)
        logger.debug("%s %s", response.status_code, response.reason)
        response.raise_for_status()

        return response


def BaseClient(
    host, verify_ssl=None, username=None, password=None, auth_service_url="", api_timeout=None
):
    return BaseClientV2(
        host,
        verify_ssl=verify_ssl,
        username=username,
        password=password,
        auth_service_url=auth_service_url,
        api_timeout=api_timeout,
    )
