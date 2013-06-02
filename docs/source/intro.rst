============
Introduction
============


Requisites
----------

pytag only requires Python >= 3.3.


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

    The returned object (:py:class:`PytagDict`) extends the Python :py:class:`dict`, and
    can be used as a :py:class:`dict`

    For more information about PytagDict see:
    :py:class:`pytag.structures.PytagDict`


