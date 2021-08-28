"""
Copyright 2015 Red Hat, Inc

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import argparse
import json
import logging
import sys
from typing import Optional

import requests
from requests.auth import HTTPBasicAuth

from dreg_client import AuthService, DockerTokenAuthService, Registry
from dreg_client._types import RequestsAuth


class CLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        excl_group = self.parser.add_mutually_exclusive_group()
        excl_group.add_argument("-q", "--quiet", action="store_true")
        excl_group.add_argument("-v", "--verbose", action="store_true")

        self.parser.add_argument("--verify-ssl", dest="verify_ssl", action="store_true")
        self.parser.add_argument("--no-verify-ssl", dest="verify_ssl", action="store_false")
        self.parser.add_argument("--username", metavar="USERNAME")
        self.parser.add_argument("--password", metavar="PASSWORD")

        self.parser.add_argument(
            "--auth-token-url",
            dest="auth_token_url",
            metavar="TOKEN_AUTH_URL",
            type=str,
            help="Authorisation token URL (including scheme)",
        )
        self.parser.add_argument(
            "--auth-service",
            dest="auth_service",
            metavar="AUTH_SERVICE",
            type=str,
            help="Authorisation service",
        )

        self.parser.add_argument(
            "registry", metavar="REGISTRY_URL", help="registry URL (including scheme)"
        )
        self.parser.add_argument(
            "repository", metavar="REPOSITORY", nargs="?", help="repository (including namespace)"
        )
        self.parser.add_argument("ref", metavar="REF", nargs="?", help="tag or digest")

        self.parser.set_defaults(verify_ssl=True)

    def run(self):
        args = self.parser.parse_args()

        basic_config_args = {}
        if args.verbose:
            basic_config_args["level"] = logging.DEBUG
        elif args.quiet:
            basic_config_args["level"] = logging.WARNING

        logging.basicConfig(**basic_config_args)

        basic_auth: RequestsAuth = None
        if args.username and args.password:
            basic_auth = HTTPBasicAuth(args.username, args.password)

        auth_service: Optional[AuthService] = None
        if args.auth_token_url and args.auth_service:
            auth_service = DockerTokenAuthService.build_with_session(
                args.auth_token_url, args.auth_service, auth=basic_auth
            )
            basic_auth = None

        registry = Registry.build_with_manual_client(
            args.registry, auth=basic_auth, auth_service=auth_service
        )

        if args.repository:
            if args.ref:
                self.show_manifest(registry, args.repository, args.ref)
            else:
                self.show_tags(registry, args.repository)
        else:
            self.show_repositories(registry)

    def show_repositories(self, registry: Registry) -> None:
        try:
            repositories = registry.repositories()
        except requests.HTTPError as e:
            if e.response.status_code != requests.codes.not_found:
                raise
            print("Catalog/Search not supported", file=sys.stderr)
            return

        print("Repositories:")
        for repository in repositories.keys():
            print(f"  - {repository}")

    def show_tags(self, registry: Registry, repository: str) -> None:
        try:
            repo = registry.repository(repository)
        except requests.HTTPError as e:
            if e.response.status_code != requests.codes.not_found:
                raise
            print("Repository {0} not found".format(repository), file=sys.stderr)
            return

        print(f"Tags in repository {repository}:")
        for tag in repo.tags():
            print(f"  - {tag}")

    def show_manifest(self, registry: Registry, repository: str, ref: str) -> None:
        try:
            repo = registry.repository(repository)
        except requests.HTTPError as e:
            if e.response.status_code != requests.codes.not_found:
                raise
            print("Repository {0} not found".format(repository), file=sys.stderr)
            return

        manifest = repo.manifest(ref)
        print(f"Digest: {manifest.digest}")
        print("Manifest:")
        print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        cli = CLI()
        cli.run()
    except KeyboardInterrupt:
        pass
