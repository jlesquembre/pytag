import struct
from array import array

from pytag.constants import CRC_LOOKUP


int_struct = struct.Struct('< I')


def read_in_chunks(fileobj, chunk_size=255):
    """Read a file in chunks."""
    chunk = fileobj.read(chunk_size)
    while chunk:
        # Do stuff with byte.
        yield chunk
        chunk = fileobj.read(chunk_size)


def crc32(*args):

    crc_reg = 0
    for element in args:
        for i, value in enumerate(element):
            crc_reg = ((crc_reg << 8) ^ CRC_LOOKUP[((crc_reg >> 24) & 0xff) ^
                                                   element[i]]) & 0xFFFFFFFF

    a = (crc_reg & 0xff)
    b = ((crc_reg >> 8) & 0xff)
    c = ((crc_reg >> 16) & 0xff)
    d = ((crc_reg >> 24) & 0xff)

    return a, b, c, d


def decode_bitwise_int(tup):
    d, c, b, a = tup
    return ((a | (b << 7)) | (c << 14)) | (d << 21)


def encode_bitwise_int(number):

    r = array('B')
    mask = 127  # 01111111
    r.insert(0, mask & number)
    r.insert(0, ((mask << 7) & number) >> 7)
    r.insert(0, ((mask << 14) & number) >> 14)
    r.insert(0, ((mask << 21) & number) >> 21)
    return r
