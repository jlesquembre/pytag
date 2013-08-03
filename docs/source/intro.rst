============
Introduction
============


Requisites
----------

pytag requires Python >= 3.3 and `filemagic`_.

.. _filemagic: http://filemagic.readthedocs.org/en/latest/


Installation
------------

.. code-block:: bash

    pip install pytag


Basic usage
-----------

::

    >>> from pytag import Audio
    >>> audio = Audio('/path/to/file.ogg')
    >>> audio.get_tags()
    PytagDict({'album': 'a cool album'})

    >>> audio.write_tags({'album': 'a new name'})
    >>> audio.get_tags()
    PytagDict({'album': 'a new name'})

.. note::

    The returned object (:py:class:`PytagDict`) extends the Python
    :py:class:`dict`, and can be used as a :py:class:`dict`

    For more information about PytagDict see:
    :py:class:`pytag.structures.PytagDict`


Is also possible access to the tags/comments as an attribute of the Audio object:

::

    >>> from pytag import AudioReader
    >>> audio = Audio('/path/to/file.ogg')
    >>> audio.album
    'a cool album'


Take a look to the common interface to see all the valid tags/comments values
:ref:`common-tags`
