from os.path import splitext

from pytag.structures import PytagDict
from pytag.formats import OggVorbisReader, OggVorbis, Mp3Reader, Mp3


EXTENSIONS = {'.ogg': (OggVorbisReader, OggVorbis),
              '.mp3': (Mp3Reader, Mp3)
              }


class AudioReader:
    """High level interface for pytag. Creates a new object if the audio format
    is supported, or returns a :py:exc:`pytag.FormatNotSupportedError` if not.
    """

    _index = 0

    def __init__(self, path):
        try:
            ext = splitext(path)[1].lower()
            self.audio = EXTENSIONS[ext][self._index](path)
        except KeyError:
            raise FormatNotSupportedError(
                '"{}" extension is not suppored'.format(ext))

    def get_tags(self):
        return PytagDict(self.audio.get_tags())


class Audio(AudioReader):
    """Extends :py:class:`pytag.AudioReader` and adds a ``write_tags`` method.
    """

    _index = 1

    def write_tags(self, tags):
        self.audio.write_tags(PytagDict(tags))


class FormatNotSupportedError(Exception):
    pass
