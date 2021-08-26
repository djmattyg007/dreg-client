import json
import logging

from requests import delete, get

from .auth_service import AuthorizationService
from .manifest import Manifest


logger = logging.getLogger(__name__)


BASE_CONTENT_TYPE = "application/vnd.docker.distribution.manifest"

schema_1_signed = BASE_CONTENT_TYPE + ".v1+prettyjws"
schema_1 = BASE_CONTENT_TYPE + ".v1+json"
schema_2 = BASE_CONTENT_TYPE + ".v2+json"


class Client:
    def __init__(
        self,
        host,
        verify_ssl=None,
        username=None,
        password=None,
        api_timeout=None,
        auth_service_url="",
    ):
        self.host = host

        if username is not None and password is not None:
            auth = (username, password)
        else:
            auth = None

        self.method_kwargs = {}
        if verify_ssl is not None:
            self.method_kwargs["verify"] = verify_ssl
        if auth:
            self.method_kwargs["auth"] = auth
        if api_timeout is not None:
            self.method_kwargs["timeout"] = api_timeout

        self.auth = AuthorizationService(
            registry=host,
            url=auth_service_url,
            verify=verify_ssl,
            auth=auth,
            api_timeout=api_timeout,
        )

    def check_status(self):
        self.auth.desired_scope = "registry:catalog:*"
        return self._http_call("/v2/", get)

    def catalog(self):
        self.auth.desired_scope = "registry:catalog:*"
        return self._http_call("/v2/_catalog", get)

    def get_repository_tags(self, name):
        self.auth.desired_scope = "repository:%s:*" % name
        return self._http_call("/v2/{name}/tags/list", get, name=name)

    def get_manifest(self, name: str, reference: str) -> Manifest:
        self.auth.desired_scope = "repository:%s:*" % name
        response = self._http_response(
            "/v2/{name}/manifests/{reference}",
            get,
            name=name,
            reference=reference,
            schema=schema_1_signed,
        )
        return Manifest(
            content=response.json(),
            content_type=response.headers.get("Content-Type", "application/json"),
            digest=response.headers.get("Docker-Content-Digest"),
        )

    def delete_manifest(self, name, digest):
        self.auth.desired_scope = "repository:%s:*" % name
        return self._http_call(
            "/v2/{name}/manifests/{reference}", delete, name=name, reference=digest
        )

    def delete_blob(self, name, digest):
        self.auth.desired_scope = "repository:%s:*" % name
        return self._http_call("/v2/{name}/blobs/{digest}", delete, name=name, digest=digest)

    def _http_response(self, url, method, data=None, content_type=None, schema=None, **kwargs):
        """url -> full target url
        method -> method from requests
        data -> request body
        kwargs -> URL formatting args
        """

        if schema is None:
            schema = schema_2

        header = {
            "Content-Type": content_type or "application/json",
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


__all__ = ("Client",)
