import struct
import io
from array import array

from pytag import utils
from pytag.structures import CaseInsensitiveDict
from pytag.constants import VENDOR_NAME


class VorbisComment:
    """Base class to read/write vorbis comments as defined at:
    http://www.xiph.org/vorbis/doc/Vorbis_I_spec.html
    """

    vendor_name = VENDOR_NAME.encode()
    framing_bit = True

    def process_comments(self, packet):
        """Reads the comments.

        :param packet: Object to read from, has a read method.
        :type packet: ``pytag.containers.PacketReader``
        :returns: A ``dict``-like object with all the comments.
        :rtype: ``pytag.structures.CaseInsensitiveDict``
        """

        # Signature is not used
        packet.read(self.signature_struct.size)

        (vendor_lenght,) = utils.int_struct.unpack(packet.read(4))
        packet.read(vendor_lenght)

        (user_comment_list_length,) = utils.int_struct.unpack(packet.read(4))

        comments = CaseInsensitiveDict()
        for i in range(user_comment_list_length):
            (length,) = utils.int_struct.unpack(packet.read(4))
            comment = packet.read(length).decode('utf-8')
            comments.update((comment.split('='),))

        return comments

    def generate_comments(self, comments):
        comments = CaseInsensitiveDict(comments)

        # Packet type + vorbis magic
        packet = array('B', self.signature)

        packet.extend(utils.int_struct.pack(len(self.vendor_name)))
        packet.extend(self.vendor_name)

        packet.extend(utils.int_struct.pack(len(comments)))

        for k, v in comments.items():
            comment = '{}={}'.format(k, v).encode()
            packet.extend(utils.int_struct.pack(len(comment)))
            packet.extend(comment)

        if self.framing_bit:
            packet.append(1)

        return io.BytesIO(packet)


class Vorbis(VorbisComment):

    signature = (0x3, 0x76, 0x6f, 0x72, 0x62, 0x69, 0x73)
    signature_struct = struct.Struct('< B 6s')

    def comments_page_position(self):
        return 1

    def packets_after_comments(self):
        return 1


class Opus(VorbisComment):      # pragma: no cover

    signature = (0x4f, 0x70, 0x75, 0x73, 0x54, 0x61, 0x67, 0x73)
    signature_struct = struct.Struct('< 8s')
    framing_bit = False

    def comments_page_position(self):
        return 1

    def packets_after_comments(self):
        return 0
