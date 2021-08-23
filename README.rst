Docker Registry Client
======================

|Build Status| |pypi|

A Python REST client for the Docker Registry

It's useful for automating image tagging and untagging

.. |Build Status| image:: https://travis-ci.org/yodle/docker-registry-client.svg?branch=master
   :target: https://travis-ci.org/yodle/docker-registry-client
   :alt: Build status

.. |pypi| image:: https://img.shields.io/pypi/v/dreg-client.svg
    :target: https://pypi.org/project/dreg-client
    :alt: Latest version released on PyPI

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

Alternatives
------------

* `python-dxf <https://pypi.org/project/python-dxf>`_ (only supports V2)
