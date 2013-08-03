import unittest
import itertools
#import subprocess
import os
import string
import shutil
import tempfile

from nose.tools import *

from pytag.containers import OggPage
from pytag.formats import OggVorbis, OggVorbisReader, OggOpus

oggs = (
    {'name': 'nocomments.ogg',
     'tags': {}
     },
    {'name': 'sample.ogg',
     'tags':
     {'title': 'test',
      'artist': 'test',
      'album': 'test',
      'comment': 'test',
      'genre': 'test',
      }
     },
    )


def test_generator_for_vorbis():
    path = os.path.join(os.path.dirname(__file__), 'files', 'oggvorbis')
    for ogg in oggs:
        ogg['path'] = os.path.join(path, ogg['name'])
        yield check_get_vorbis_tags, ogg


def check_get_vorbis_tags(ogg):

    eq_(ogg['tags'], OggVorbisReader(ogg['path']).get_tags())


"""
class OpusTest(unittest.TestCase):

    def setUp(self):
        self.opus_path = os.path.join(os.path.dirname(__file__), 'files', 'opus', 'example.opus')
        self.opus_temp = tempfile.mkstemp()[1]
        shutil.copy(self.opus_path, self.opus_temp)

    def test_read(self):
        opus = OggOpus(self.opus_temp)
        tags = {'title': 'opus',
                'artist': 'opus'}

        self.assertEqual({}, opus.get_tags())

        opus.write_tags(tags)

        self.assertEqual(tags, opus.get_tags())

    def tearDown(self):
        os.remove(self.opus_temp)
"""


class OggVorbisWriteTest(unittest.TestCase):

    def setUp(self):
        self.ogg_path = os.path.join(os.path.dirname(__file__), 'files',
                                     'oggvorbis', 'sample.ogg')
        self.temp_ogg = tempfile.mkstemp()[1]
        shutil.copy(self.ogg_path, self.temp_ogg)

    def tearDown(self):
        os.remove(self.temp_ogg)

    def assert_new_tags(self):

        new_tags = OggVorbisReader(self.temp_ogg).get_tags()

        self.assertEqual(new_tags, self.tags)

        with open(self.ogg_path, 'rb') as old,\
                open(self.temp_ogg, 'rb') as new:
            ogg_old = OggPage(old)
            ogg_new = OggPage(new)

            self.assertEqual(ogg_old.crc, ogg_new.crc)

            while not ogg_old.is_last_page():
                ogg_old.next_page()
                ogg_new.next_page()
                if ogg_old.number == 1:
                    self.assertNotEqual(ogg_old.crc, ogg_new.crc)
                else:
                    self.assertEqual(ogg_old.crc, ogg_new.crc)

            self.assertTrue(ogg_new.is_last_page())

    def test_change_tag(self):
        ogg = OggVorbis(self.temp_ogg)
        self.tags = ogg.get_tags()
        self.tags['ALBUM'] = 'aaa'

        ogg.write_tags(self.tags)
        self.assert_new_tags()

    def test_write_same_tags(self):
        ogg = OggVorbis(self.temp_ogg)
        self.tags = ogg.get_tags()

        ogg.write_tags(self.tags)
        self.assert_new_tags()

    def test_write_many_tags(self):
        """Write 255 tags with length of 255, to complete fill a ogg page and
        force to create a new ogg page.
        """

        ogg = OggVorbis(self.temp_ogg)

        self.tags = {}
        keys = [''.join(tup) for tup in (list(itertools.product(
                                              string.ascii_lowercase[:16],
                                              repeat=2)))]

        for key in keys:
            self.tags[key] = 'a'*255

        #tags = utils.tag_dict(tags)

        ogg.write_tags(self.tags)

        #import ipdb; ipdb.set_trace()
        new_tags = OggVorbisReader(self.temp_ogg).get_tags()

        self.assertEqual(new_tags, self.tags)

        with open(self.ogg_path, 'rb') as old,\
                open(self.temp_ogg, 'rb') as new:
            ogg_old = OggPage(old)
            ogg_new = OggPage(new)

            self.assertEqual(ogg_old.crc, ogg_new.crc)

            while not ogg_old.is_last_page():
                ogg_old.next_page()
                ogg_new.next_page()
                self.assertNotEqual(ogg_old.crc, ogg_new.crc)

            self.assertFalse(ogg_new.is_last_page())
            ogg_new.next_page()
            self.assertTrue(ogg_new.is_last_page())
