import magic

from pytag.structures import PytagDict
from pytag.constants import FIELD_NAMES
from pytag.formats import OggVorbisReader, OggVorbis, Mp3Reader, Mp3


MIMETYPE = {'application/ogg': (OggVorbisReader, OggVorbis),
            'audio/mpeg': (Mp3Reader, Mp3)
            }


class Tag:
    """Descriptor class.
    """

    def __init__(self, name):
        self.name = name

    def __get__(self, instance, cls):

        if instance is None:  # pragma: nocover
            return self

        try:
            return instance.__dict__[self.name]
        except KeyError:
            tags = instance.get_tags()
            for name in (set(tags) ^ set(FIELD_NAMES)):
                instance.__dict__[name] = None
            return instance.__dict__[self.name]

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value


class MetaAudio(type):
    """Set all the FIELD_NAMES as class descriptors.
    """

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in FIELD_NAMES:
            setattr(cls, name, Tag(name))


class AudioReader(metaclass=MetaAudio):
    """High level interface for pytag. Creates a new object if the audio format
    is supported, or returns a :py:exc:`pytag.FormatNotSupportedError` if not.
    """

    _index = 0

    def __init__(self, path):

        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
            self.mimetype = m.id_filename(path)

        try:
            self._format = MIMETYPE[self.mimetype][self._index](path)
        except KeyError:
            # Old filemagic versions don't recognize some mp3 files
            if (self.mimetype == 'application/octet-stream' and
                    path.endswith('.mp3')):
                self._format = MIMETYPE['audio/mpeg'][self._index](path)
            else:
                raise FormatNotSupportedError(
                    '"{}" type is not suppored'.format(self.mimetype))

    def get_tags(self):

        tags = PytagDict(self._format.get_tags())
        for name, value in tags.items():
            setattr(self, name, value)
        return tags


class Audio(AudioReader):
    """Extends :py:class:`pytag.AudioReader` and adds a ``write_tags`` method.
    """

    _index = 1

    def write_tags(self, tags):
        self._format.write_tags(PytagDict(tags))


class FormatNotSupportedError(Exception):
    pass
