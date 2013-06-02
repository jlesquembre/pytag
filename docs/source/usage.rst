=====
Usage
=====

Common interface
----------------

pytag defines a common list of tags (or comments) for all the supported audio
formats. This tags are defined at :py:data:`pytag.constants.FIELD_NAMES` and
they are:

* title
* artist
* album
* date
* tracknumber
* organization
* genre
* performer

Using the common interface, doesn't matter if we use want to read from a mp3 or
from a ogg vorbis file. If an audio file contains other tags, they are ignored.

Reading metadata from multiple audio files:

::

    from pytag import AudioReader, FormatNotSupportedError

    files = ['audio.ogg', 'audio.mp3', 'image.png']

    try:
        for file in files:
            audio = AudioReader(file)
            print (audio.get_tags())
    except FormatNotSupportedError:
        print('Process other file...')

.. note::

    If ``audio.ogg`` has a tag called ``band``, this is ignored. If you want
    all the tags, use the Ogg vorbis interface. See:
    :ref:`vorbis-comm`


Writing metadata to an audio file:

::

    from pytag import Audio

    audio = Audio('music.ogg')
    audio.write_tags({'album': 'cool', 'year': '2000'})

.. note::

    Here only tag ``album`` is saved, ``year`` is ignored.

    :py:class:`pytag.Audio` extends :py:class:`pytag.AudioReader`, with
    :py:class:`pytag.Audio` is also possible read the tags. Class
    :py:class:`pytag.AudioReader` is provided just to avoid write some metadata
    by mistake.


.. _vorbis-comm:

Vorbis comments
---------------

Using Vorbis comments is possible to save any metadata.

Writing and reading random tags:

::

    >>> from pytag.format import OggVorbis
    >>> vorbis = OggVorbis('music.ogg')
    >>> vorbis.write_tags({'foo': 'bar'})
    >>> vorbis.get_tags()
    {'foo': 'bar'}

.. note::

    Like :py:class:`pytag.Audio` has a :py:class:`pytag.AudioReader` only for
    reading, :py:class:`pytag.formats.OggVorbis` also has a
    :py:class:`pytag.formats.OggVorbisReader` which only is allow to read the
    comments.

Mp3 tags
--------

Mp3 files uses ID3 to save the metadata. This format defines a list of codes
for the valid tags. See `Wikipedia ID3v2 Frames List
<http://en.wikipedia.org/wiki/ID3#ID3v2_Frame_Specification_.28Version_2.3.29>`_

As this list is huge and many times confusing, I recommend use only the common
interface to read/write Mp3 tags.


