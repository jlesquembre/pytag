import collections
import struct
import io
import tempfile
import shutil
from array import array

from pytag import utils
from pytag.containers import OggReader, Ogg
from pytag.codecs import Vorbis, Opus
from pytag.constants import (ID3_ENCODINGS, ID3_GENRES, FIELD_NAMES,
                             TAG_ID3_V22, TAG_ID3_V23, TAG_ID3_V24)


class OggVorbisReader(Vorbis, OggReader):
    pass


class OggVorbis(Vorbis, Ogg):
    pass


class OggOpusReader(Opus, OggReader):
    pass


class OggOpus(Opus, Ogg):
    pass


Id3Frame = collections.namedtuple('Id3Frame', ['comment', 'size'])


class Mp3Reader:

    def __init__(self, path):
        self.path = path

    def get_tags(self):

        tags = {}
        with open(self.path, 'rb') as self.input_file:

            if self._has_id3v2_tags():
                tags = self._read_id3v2_tags()
            elif self._has_id3v1_tags():
                tags = self._read_id3v1_tags()

        return tags

    def _has_id3v1_tags(self):
        self.input_file.seek(0, io.SEEK_END)
        if self.input_file.tell() > 128:
            self.input_file.seek(-128, io.SEEK_END)
            (tag, ) = struct.unpack('> 3s', self.input_file.read(3))
            if tag == b'TAG':
                return True

        return False

    def _has_id3v2_tags(self):
        (id3, ) = struct.unpack('> 3s', self.input_file.read(3))
        return id3 == b'ID3'

    def _read_id3v1_tags(self):
        tags = {}

        title = self._remove_padding(self.input_file.read(30))
        if title:
            tags['title'] = title

        artist = self._remove_padding(self.input_file.read(30))
        if artist:
            tags['artist'] = artist

        album = self._remove_padding(self.input_file.read(30))
        if album:
            tags['album'] = album

        date = self._remove_padding(self.input_file.read(4))
        if date:
            tags['date'] = date

        self.input_file.seek(29, io.SEEK_CUR)  # Ignore comments

        tracknumber = int.from_bytes(self.input_file.read(1), byteorder='big')
        if tracknumber:
            tags['tracknumber'] = tracknumber

        genre = int.from_bytes(self.input_file.read(1), byteorder='big')
        if genre in ID3_GENRES:
            tags['genre'] = ID3_GENRES[genre]

        return tags

    def _remove_padding(self, text):
        try:
            return text[:text.index(b'\x00')].decode()
        except ValueError:
            return text.decode()

    def _read_id3v2_tags(self):
        (mayor, minor) = struct.unpack('> B B', self.input_file.read(2))
        self.input_file.seek(1, io.SEEK_CUR)
        size = utils.decode_bitwise_int(struct.unpack('> B B B B',
                                                      self.input_file.read(4)))

        if mayor == 2:
            read_frame = self._read_id3v22_frame
        elif mayor == 3:
            read_frame = self._read_id3v23_frame
        elif mayor == 4:
            read_frame = self._read_id3v24_frame
        else:   # pragma: no cover
            raise Exception('ID3 version "2.{}" not supported'.format(mayor))

        comments = {}
        while size > 0:
            frame = read_frame()
            size -= frame.size
            if frame.comment:
                comments.update(frame.comment)

        return comments

    def _decode_genre(self, text):

        try:
            genres = []
            for code in text.split(')('):
                code = int(code.strip('()'))
                genres.append(ID3_GENRES[code])

            if len(genres) == 1:
                return genres[0]

            return genres
        except:
            return text


    def _read_id3_generic_frame(self, frame_id, size, id3_type):

        (encoding, ) = struct.unpack('> B', self.input_file.read(1))
        header_size = 6 if id3_type == 2 else 10
        try:
            if id3_type == 2:
                index = TAG_ID3_V22.index(frame_id.decode())
            if id3_type == 3:
                index = TAG_ID3_V23.index(frame_id.decode())
            if id3_type == 4:
                index = TAG_ID3_V24.index(frame_id.decode())

            data = self.input_file.read(size-1)
            data = data.decode(ID3_ENCODINGS[encoding])

            if frame_id == b'TCO' or frame_id == b'TCON':
                if id3_type != 4:
                    data = self._decode_genre(data)

            data = {FIELD_NAMES[index]: data}
            return Id3Frame(data, size + header_size)

        except ValueError:
            self.input_file.seek(size - 1, io.SEEK_CUR)
            return Id3Frame(None, size + header_size)

    def _read_id3v22_frame(self):
        (frame_id, ) = struct.unpack('> 3s ', self.input_file.read(3))
        size = int.from_bytes(self.input_file.read(3), byteorder='big')
        return self._read_id3_generic_frame(frame_id, size, 2)

    def _read_id3v23_frame(self):
        (frame_id, ) = struct.unpack('> 4s ', self.input_file.read(4))
        (size, ) = struct.unpack('> I', self.input_file.read(4))

        self.input_file.seek(2, io.SEEK_CUR)  # Flags, not used

        return self._read_id3_generic_frame(frame_id, size, 3)

    def _read_id3v24_frame(self):
        (frame_id, ) = struct.unpack('> 4s ', self.input_file.read(4))
        size = utils.decode_bitwise_int(struct.unpack('> B B B B',
                                                      self.input_file.read(4)))

        self.input_file.seek(2, io.SEEK_CUR)  # Flags, not used

        return self._read_id3_generic_frame(frame_id, size, 4)


class Mp3(Mp3Reader):

    def write_tags(self, comments):

        with tempfile.NamedTemporaryFile('wb', delete=False) as output_file,\
                open(self.path, 'rb') as self.input_file:

            # Write tags if at least has one supported value
            tags = array('B')
            for key, value in comments.items():
                if key in FIELD_NAMES:

                    frame = array('B',
                                  TAG_ID3_V24[FIELD_NAMES.index(key)].encode())
                    frame.extend([0]*6)  # Size and flags
                    frame.append(3)      # Encoding
                    frame.extend(value.encode())
                    frame[4:8] = utils.encode_bitwise_int(len(frame) - 10)

                    tags.extend(frame)

            if len(tags):
                output_file.write(b'ID3\x04\x00\x00')
                output_file.write(utils.encode_bitwise_int(len(tags)))
                output_file.write(tags)

            # Position input file cursor after id3v2 tags
            if self._has_id3v2_tags():
                self._read_id3v2_tags()
            else:
                self.input_file.seek(0)

            output_file.write(self.input_file.read())

            if self._has_id3v1_tags():
                output_file.seek(-128, io.SEEK_END)
                output_file.truncate()

        shutil.move(output_file.name, self.path)
