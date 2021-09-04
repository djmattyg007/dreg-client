======================
Docker Registry Client
======================

|ci| |pypi| |license|

A Python REST client for Docker Registries. Pronounced ``dee-redge client``.

It's useful for automating image tagging and untagging

.. |ci| image:: https://github.com/djmattyg007/dreg-client/workflows/CI/badge.svg?branch=main
   :target: https://github.com/djmattyg007/dreg-client/actions?query=branch%3Amain+workflow%3ACI
   :alt: Build status
.. |codecov| image:: https://codecov.io/gh/djmattyg007/dreg-client/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/djmattyg007/dreg-client
   :alt: Code coverage
.. |pypi| image:: https://img.shields.io/pypi/v/dreg-client.svg
   :target: https://pypi.org/project/dreg-client
   :alt: Latest version released on PyPI
.. |license| image:: https://img.shields.io/pypi/l/dreg-client.svg
   :target: https://pypi.org/project/dreg-client
   :alt: Apache License 2.0

Usage
=====

Most people will primarily use the ``Registry`` class::

    from dreg_client import Registry

    registry = Registry.build_with_manual_client("https://registry.example.com/v2/")

    namespaces = registry.namespaces()  # a sequence of strings
    repositories = registry.repositories()  # a mapping of repository names to Repository objects
    ns_repositories = registry.repositories("testns")  # a mapping of repository names to Repository objects,
                                                       # but only for those repositories in the "testns" namespace
    test_repo = registry.repository("testrepo", "testns")  # a Repository object
    test_repo = registry.repository("testns/testrepo")  # an identical repository object

The ``Repository`` class has several methods for interacting with individual repositories::

    from dreg_client import Repository, Manifest

    assert isinstance(test_repo, Repository)
    assert test_repo.name == "testns/testrepo"

    tags = test_repo.tags()  # a sequence of strings

    manifest = test_repo.get_manifest(tags[0])  # a Manifest object
    assert isinstance(manifest, Manifest)

    test_repo.delete_manifest(manifest.digest)  # manifests can only be deleted by digest, not by tag

    # At the moment, retrieving and deleting blobs returns a requests Response object directly
    get_blob_response = test_repo.get_blob("sha256:ce17d456b9373523c40fe294e8918a10059f63c54edd2c8ead1f3079f7fbb22a")
    delete_blob_response = test_repo.delete_blob("sha256:ce17d456b9373523c40fe294e8918a10059f63c54edd2c8ead1f3079f7fbb22a")

History
=======

dreg-client is a fork of a project named `docker-registry-client <https://github.com/yodle/docker-registry-client>`_.
While it looked good, development has stalled, with approved PRs remaining unmerged. The code design was also hostile
to strict type checking. I forked it to make some improvements, add type hints, and to resolve several outstanding
problems at the time.

This fork is not a drop-in replacement for ``docker-registry-client``. Major changes from upstream include:

- Complete removal of python2 support
- Complete removal of support for v1 registries
- A re-work of class names
- A re-work of the requests integration and registry auth service

Alternatives
============

* `python-dxf <https://pypi.org/project/python-dxf>`_
