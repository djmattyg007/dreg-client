=========
Changelog
=========

v1.2.0 - 2021-09-05
===================

- Add digest methods to ``PlatformImage`` class.
- Formally declare support for python 3.10.
- Bump minimum supported version of requests
- Fix some issues with the tests (type-checking and a broken assert statement).
- Add a shebang to the show script.

v1.1.0 - 2021-09-05
===================

- Export ``ImageHistoryItem`` through the package entrypoint.
- Add ``image_size`` property to ``PlatformImage`` and ``Manifest`` classes.
- Add ``short_digest`` property to all data classes that have a ``digest`` property. This is meant
  to mimic the short digests shown on Docker Hub.
- Add ``non_empty_history`` property to ``ImageConfig`` class, to retrieve a list of only non-empty
  layers. This is a convenience method to retrieve a list of history items that will nicely line up
  with the list of downloadable layers.
- Add ``clean_created_by`` property to ``ImageHistoryItem`` class, to centralise efforts for
  providing "nice" displays of layer information.

v1.0.2 - 2021-09-04
===================

Fixed a bug with the packaging + release process.

v1.0.1 - 2021-09-04
===================

- Declare support for Python 3.8
- ``Platform`` objects are now stringable
- Added wrapper method ``get_platform_images`` to ``Image`` class

v1.0.0 - 2021-09-04
===================

Initial release after fork from upstream. To understand why the fork happened,
please see the History section of the readme.
