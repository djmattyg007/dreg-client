Docker Registry Client
======================

|ci| |pypi| |license|

A Python REST client for the Docker Registry

It's useful for automating image tagging and untagging

.. |ci| image:: https://github.com/djmattyg007/dreg-client/workflows/CI/badge.svg?branch=master
   :target: https://github.com/djmattyg007/dreg-client/actions?query=branch%3Amain+workflow%3ACI
   :alt: Build status
.. |pypi| image:: https://img.shields.io/pypi/v/dreg-client.svg
   :target: https://pypi.org/project/dreg-client
   :alt: Latest version released on PyPI
.. |license| image:: https://img.shields.io/pypi/l/dreg-client.svg
   :target: https://pypi.org/project/dreg-client
   :alt: Apache License 2.0

Usage
-----

The API provides several classes: ``DockerRegistryClient``, ``Repository``.

``DockerRegistryClient`` has the following methods:

- ``namespaces()`` -> a list of all namespaces in the registry
- ``repository(repository_name, namespace)`` -> the corresponding repository object
- ``repositories()`` -> all repositories in the registry

``Repository`` has the following methods:

- ``tags()`` -> a list of all tags in the repository
- ``data(tag)`` -> json data associated with ``tag``
- ``image(tag)`` -> the image associated with ``tag``
- ``untag(tag)`` -> remove ``tag`` from the repository
- ``tag(tag, image_id)`` -> apply ``tag`` to ``image_id``

History
-------

dreg-client is a fork of a project named `docker-registry-client <https://github.com/yodle/docker-registry-client>`_.
I forked it to make some improvements, add type hints (pending), and to resolve several outstanding problems at the time.

Alternatives
------------

* `python-dxf <https://pypi.org/project/python-dxf>`_ (only supports V2)
