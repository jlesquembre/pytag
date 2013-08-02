import os
import tempfile
import shutil
import unittest

from pytag import Audio, AudioReader, FormatNotSupportedError


class InterfaceTest(unittest.TestCase):

    def setUp(self):
        self.tags = {
            'title': 'test',
            'artist': 'test',
            'album': 'test',
            'genre': 'test'
        }

    def test_read(self):
        path = os.path.join(os.path.dirname(__file__),
                            'files', 'oggvorbis', 'sample.ogg')

        audio = AudioReader(path)
        self.assertEqual(self.tags, audio.get_tags())

    def test_read_lazy(self):
        path = os.path.join(os.path.dirname(__file__),
                            'files', 'oggvorbis', 'sample.ogg')

        audio = AudioReader(path)
        self.assertEqual(audio.title, 'test')
        self.assertEqual(audio.artist, 'test')
        self.assertEqual(audio.album, 'test')
        self.assertEqual(audio.genre, 'test')
        self.assertEqual(audio.tracknumber, None)

    def test_write(self):
        path = os.path.join(os.path.dirname(__file__),
                            'files', 'oggvorbis', 'sample.ogg')
        temp = tempfile.mkstemp(suffix='.ogg')[1]
        shutil.copy(path, temp)

        audio = Audio(temp)
        self.assertEqual(self.tags, audio.get_tags())

        audio.write_tags({'foo': 'foo', 'bar': 'bar'})
        self.assertEqual({}, audio.get_tags())

        new_tags = {'foo': 'foo'}
        new_tags.update(self.tags)
        audio.write_tags(new_tags)
        self.assertEqual(self.tags, audio.get_tags())

        os.remove(temp)

    def test_not_valid_format(self):
        temp = tempfile.mkstemp(suffix='.unknow')[1]
        self.assertRaises(FormatNotSupportedError, Audio, temp)
        os.remove(temp)
