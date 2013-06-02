import struct
import io
import collections
import tempfile
import shutil
import abc

from array import array

from pytag import utils


PacketInfo = collections.namedtuple('PacketInfo', ['size', 'complete'])


class OggPage:
    """
    """

    header_struct = struct.Struct("< 4s B B q I I I B")

    def __init__(self, fileobj):
        """Inizializates a OggPage

        :param fileobj: Stream to read from.
        :type fileobj: ``io.RawIOBase``
        """

        self.fileobj = fileobj
        self.segment_table_index = 0

        self._unpack(fileobj.read(27))
        self.segment_table = array('B', fileobj.read(self.page_segments))
        self.packet_reader = None

    def next_page(self):
        """Iterates to next page.
        """

        # If page has not readed segments, seek them
        self.fileobj.seek(sum(self.segment_table[self.segment_table_index:]),
                          io.SEEK_CUR)
        self.__init__(self.fileobj)
        return self

    def rest_of_pages(self):
        """Iterator over still not readed pages.
        """

        while not self.is_last_page():
            yield self.next_page()

    def as_bytes(self, update_crc=False):
        """Get the complete page as bytes.

        :paramer update_crc: Flag to know if recalculate the CRC.
        :type update_crc: ``boolean``
        :returns: Ogg page
        :rtype: :py:class:`array.array` of bytes, typecode = 'B'
        """

        if update_crc:
            self.crc = 0

        page = array('B')
        page.extend(self._pack())
        page.extend(self.segment_table)
        page.extend(self.fileobj.read(sum(self.segment_table)))
        self.segment_table_index = len(self.segment_table)

        if update_crc:
            crc = utils.crc32(page)
            page[22:26] = array('B', crc)

        return page

    def is_last_page(self):
        """Check if the page is the last in a logical bitstream.
        :returns: True if is the last one, False if not.
        :rtype: ``boolean``
        """

        return self.header_type == 4

    def _pack(self):
        """Packs the page header.
        :returns: A bytes object containing the page header.
        :rtype: ``bytes``
        """

        return self.header_struct.pack(self.oggs, self.version,
                                       self.header_type, self.granule_position,
                                       self.serial, self.number, self.crc,
                                       self.page_segments)

    def _unpack(self, buf):
        """Unpacks a bytes buffer to set the page header values.
        """

        (self.oggs, self.version, self.header_type, self.granule_position,
         self.serial, self.number, self.crc, self.page_segments) = (
             self.header_struct.unpack(buf))

    def get_packet_info(self):
        """Gets the size of the next packet (or partial packet) in the current
        page. This size can be smaller than the full packet because a packet
        can we splited in severa pages. Also check it the packet finish in the
        current page.  If page has no more bytes to read, this function
        iterates to the next page.
        The idea is use this function as callback in PacketReader, this way,
        when a packet is readed, the reader doesn't need to worry about how the
        packet is saved inside an ogg stream.

        :returns: Next packet size and if the packet finish in this page.
        :rtype: :py:class:`collections.namedtuple` of type ``PacketInfo``
        """

        # Check if current page has more segments to read
        if len(self.segment_table) == self.segment_table_index:
            self.next_page()

        total_size = 0
        for size in self.segment_table[self.segment_table_index:]:
            self.segment_table_index += 1
            total_size += size
            if size is not 255:
                return PacketInfo(size=total_size, complete=True)

        return PacketInfo(size=total_size, complete=False)

    def get_packet_reader(self):
        """Get a packet reader for the current page.

        :returns: A packet reader over the same stream used by this OggPage
        :rtype: ``PacketReader``
        """

        if not self.packet_reader:
            self.packet_reader = PacketReader(self.fileobj,
                                              self.get_packet_info)
        return self.packet_reader

    def __str__(self):   # pragma: no cover
        return ('Magic:  {o.oggs}, '
                'Version: {o.version}, '
                'Header type: {o.header_type}, '
                'Granule position: {o.granule_position}, '
                'Serial Nr: {o.serial}, '
                'Position: {o.number}, '
                'CRC: {o.crc}, '
                'Page segments: {o.page_segments}'
                .format(o=self))


class PacketReader:
    """My class doc."""

    def __init__(self, fileobj, get_packet_info_callback):
        """Method doc"""

        self.fileobj = fileobj
        self.get_packet_info_callback = get_packet_info_callback
        self.position = 0

    def read(self, _n=-1):
        """Read up to n bytes from the current packet in the stream and return
        them. If n is unspecified or -1, read and return all the bytes until
        the packet end.
        """

        if self.position == 0:
            self.limit, self.complete = self.get_packet_info_callback()

        # Read complete packet
        if _n == -1:
            partial_n = self.limit - self.position
            ret = self.fileobj.read(partial_n)
            while not self.complete:
                self.position = 0
                self.limit, self.complete = self.get_packet_info_callback()
                ret += self.fileobj.read(self.limit)

        # Read n bytes from packet
        else:
            ret = b''
            while _n != 0:
                if _n + self.position <= self.limit:
                    partial_n = _n
                else:
                    partial_n = self.limit - self.position
                _n -= partial_n
                self.position += partial_n
                ret += self.fileobj.read(partial_n)
                if _n != 0:
                    self.position = 0
                    self.limit, self.complete = self.get_packet_info_callback()

        return ret


class OggReader(metaclass=abc.ABCMeta):

    def __init__(self, path):
        self.path = path

    def get_tags(self):
        with open(self.path, 'rb') as input_file:
            current_page = OggPage(input_file)
            for i in range(self.comments_page_position()):
                current_page.next_page()
            tags = self.process_comments(current_page.get_packet_reader())

        return tags

    @abc.abstractmethod
    def comments_page_position(self):
        """Returns the page number where the comments start."""

    @abc.abstractmethod
    def process_comments(self, packet):
        """Returns the comments."""


class Ogg(OggReader):

    def __init__(self, path):

        self.output_page_nr = 0
        self.page_out = array('B')
        super().__init__(path)

    @abc.abstractmethod
    def packets_after_comments(self):
        """Returns the number of packets in the same page after the comments
        packet
        """

    def write_tags(self, comments):
        """Write the tags to a new file, if no path is provided, the original
        file is overwrited
        """

        with tempfile.NamedTemporaryFile('wb',
                                         delete=False) as self.output_file,\
                open(self.path, 'rb') as input_file:

            # First page, get serial number and write
            current_page = OggPage(input_file)
            self.serial = current_page.serial
            self.output_file.write(current_page.as_bytes())

            # Second page
            current_page.next_page()

            # Get a packet reader
            packet_reader = current_page.get_packet_reader()

            # Ignore old comments, advance to next packet
            packet_reader.read()

            # Generate and write new comments
            codec_packet = self.generate_comments(comments)
            self._to_page(codec_packet)

            # Read setup header
            for i in range(self.packets_after_comments()):
                codec_packet = packet_reader.read()
                self._to_page(io.BytesIO(codec_packet), force_page_end=True)

            new_pages = self.output_page_nr - current_page.number
            # We need to increment the page secuence number for all pages
            if new_pages > 0:
                for page in current_page.rest_of_pages():
                    page.number += new_pages
                    self.output_file.write(page.as_bytes(update_crc=True))
            else:
                self.output_file.write(input_file.read())

        shutil.move(self.output_file.name, self.path)

    def _to_page(self, packet, p_type=0, force_page_end=False):

        if len(self.page_out) is 0:
            self.page_out.extend(b'OggS')
            self.page_out.extend([0,                       # Version
                                  p_type,                  # Header type
                                  0, 0, 0, 0, 0, 0, 0, 0,  # Granular position
                                  ])

            self.page_out.extend(utils.int_struct.pack(self.serial))  # Ser.Nr
            self.output_page_nr += 1
            self.page_out.extend(utils.int_struct.pack(self.output_page_nr))

            self.page_out.extend([0, 0, 0, 0,  # CRC
                                  0])        # Nr page segments

            self.s_table = array('B')
            self.segments = array('B')

        for segment in utils.read_in_chunks(packet, 255):
            self.s_table.append(len(segment))
            self.segments.extend(segment)
            if len(self.s_table) == 255:
                # Page is full, write and continue in new page
                self._write_page()
                self.page_out = array('B')
                self._to_page(packet, p_type=1)

        # Finish this page
        if force_page_end:
            self._write_page()
            self.page_out = array('B')

    def _write_page(self):
        self.page_out[-1] = len(self.s_table)
        crc = utils.crc32(self.page_out, self.s_table, self.segments)
        self.page_out[22:26] = array('B', crc)
        self.output_file.write(self.page_out)
        self.output_file.write(self.s_table)
        self.output_file.write(self.segments)
