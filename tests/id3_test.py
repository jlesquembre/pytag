import unittest
import tempfile
import shutil
import os
import pytag

from pytag.formats import Mp3
from pytag.constants import FIELD_NAMES

class Mp3Test(unittest.TestCase):

    def setUp(self):
        self.mp3_folder = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 'files', 'mp3')

    def test_v1(self):
        mp3_path = os.path.join(self.mp3_folder, 'id3v1.mp3')

        id3 = Mp3(mp3_path)
        tags = {
            'title': 'Title',
            'artist': 'Artist',
            'album': 'Album',
            'date': '2011',
            'tracknumber': 1
            }

        self.assertEqual(id3.get_tags(), tags)

    def test_v1_genre(self):
        mp3_path = os.path.join(self.mp3_folder, 'id3v1_g.mp3')

        id3 = Mp3(mp3_path)
        tags = {
            'title': 'Title',
            'artist': 'Artist',
            'album': 'Album',
            'date': '2011',
            'tracknumber': 1,
            'genre': 'Rock'
            }

        self.assertEqual(id3.get_tags(), tags)

    def test_v22(self):
        mp3_path = os.path.join(self.mp3_folder, 'id3v22.mp3')

        id3 = Mp3(mp3_path)
        tags = {
            'album': 'ァアィイゥウェエォオカガキギクグ',
            'title': 'Track Name',
            'tracknumber': '1/2',
            }

        self.assertEqual(id3.get_tags(), tags)

    def test_v23(self):
        mp3_path = os.path.join(self.mp3_folder, 'id3v23.mp3')

        id3 = Mp3(mp3_path)
        tags = {
            'album': 'ァアィイゥウェエォオカガキギクグ',
            'title': 'Track Name',
            'tracknumber': '1/2',
            }

        self.assertEqual(id3.get_tags(), tags)

    def test_v23_g(self):
        mp3_path = os.path.join(self.mp3_folder, 'id3v23_g.mp3')

        id3 = Mp3(mp3_path)
        tags = {
            'album': 'ァアィイゥウェエォオカガキギクグ',
            'title': 'Track Name',
            'tracknumber': '1/2',
            'genre': 'Alternative',
            }

        self.assertEqual(id3.get_tags(), tags)

    def test_v23_g2(self):
        mp3_path = os.path.join(self.mp3_folder, 'id3v23_g2.mp3')

        id3 = Mp3(mp3_path)
        tags = {
            'album': 'ァアィイゥウェエォオカガキギクグ',
            'title': 'Track Name',
            'tracknumber': '1/2',
            'genre': ['Blues', 'Classic Rock'],
            }
        self.assertEqual(id3.get_tags(), tags)

    def test_v24(self):
        mp3_path = os.path.join(self.mp3_folder, 'id3v24.mp3')

        id3 = Mp3(mp3_path)
        tags = {
            'album': 'ァアィイゥウェエォオカガキギクグ',
            'title': 'Track Name',
            'tracknumber': '1/2',
            }

        self.assertEqual(id3.get_tags(), tags)

    def test_v24_all_tags(self):
        mp3_path = os.path.join(self.mp3_folder, 'id3v24_all_tags.mp3')

        id3 = Mp3(mp3_path)
        tags = { t:t for t in FIELD_NAMES}
        tags['tracknumber'] = '1/2'
        tags['date'] = '2000'
        tags['genre'] = 'Blues'

        #import ipdb; ipdb.set_trace()

        self.assertEqual(id3.get_tags(), tags)

    def test_write_tags(self):
        mp3_path = os.path.join(self.mp3_folder, 'id3v24_all_tags.mp3')
        mp3_temp = tempfile.mkstemp()[1]
        shutil.copy(mp3_path, mp3_temp)

        id3 = Mp3(mp3_temp)
        tags = { t:t for t in FIELD_NAMES}
        tags['tracknumber'] = '1/2'
        tags['date'] = '2000'
        tags['genre'] = 'Blues'

        id3.write_tags(tags)

        self.assertEqual(id3.get_tags(), tags)

        os.remove(mp3_temp)

    def test_delete_tags(self):
        mp3_path = os.path.join(self.mp3_folder, 'id3v24.mp3')
        mp3_temp = tempfile.mkstemp()[1]
        shutil.copy(mp3_path, mp3_temp)

        tags = {
            'album': 'ァアィイゥウェエォオカガキギクグ',
            'title': 'Track Name',
            'tracknumber': '1/2',
            }
        id3 = Mp3(mp3_temp)
        self.assertEqual(id3.get_tags(), tags)

        id3.write_tags({})
        self.assertEqual(id3.get_tags(), {})

        id3.write_tags(tags)
        self.assertEqual(id3.get_tags(), tags)

        os.remove(mp3_temp)

    def test_write_v1_to_v2(self):
        mp3_path = os.path.join(self.mp3_folder, 'id3v1.mp3')
        mp3_temp = tempfile.mkstemp()[1]
        shutil.copy(mp3_path, mp3_temp)

        id3 = Mp3(mp3_temp)
        tags = {
            'album': 'ァアィイゥウェエォオカガキギクグ',
            'title': 'Track Name',
            'tracknumber': '1/2',
            }
        id3.write_tags(tags)

        self.assertEqual(id3.get_tags(), tags)
