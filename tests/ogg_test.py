import unittest


import io
from array import array
import collections
from nose.tools import *

from pytag.containers import OggPage, PacketReader

Result = collections.namedtuple('Result', ['size', 'data'])
Oggfile = collections.namedtuple('Oggfile', ['data', 'description', 'results'])

# len is 5 because 5*51==255, the maximal segment size
text  = b'pytag'
full = text * 51
text2 = b'zz'

oggtests = {
    1: Oggfile(
        data = array('B',
            [0]*26 +         # Header
            [1]    +         # Nr of segments
            [len(text)] +    # Segment table
            list(text))      # Segments
        ,
        description =
            'One page with one packet with one segment.'
            'len(segment) == 5'
        ,
        results = (
                Result(size=len(text), data=text),
                )
        ),

    2: Oggfile(
        data = array('B',
            [0]*26 +           # Header
            [2]    +           # Nr of segments
            [len(full), 0] +   # Segment table
            list(full))        # Segments
        ,
        description =
            'One page with one packet with two segments. '
            'Second segment empty. '
            'len(segment[0]) == 255, len(segment[1]) == 0'
        ,
        results = (
                Result(size=len(full), data=full),
                )
        ),

    3: Oggfile(
        data = array('B',
            [0]*26 +                        # Header
            [2]    +                        # Nr of segments
            [len(full), len(text)] +        # Segment table
            list(full) + list(text))        # Segments
        ,
        description =
            'One page with one packet with two segments. '
            'len(segment) == 260'
        ,
        results = (
                Result(size=len(full)+len(text), data=full+text),
                )
        ),

    4: Oggfile(
        data = array('B',
            [0]*26 +                        # Header
            [2]    +                        # Nr of segments
            [len(text), len(text)] +        # Segment table
            list(text) + list(text))        # Segments
        ,
        description =
            'One page with two packets, every with one segment. '
            'len(segment[0]) == 5, len(segment[1]) == 5'
        ,
        results = (
                Result(size=len(text), data=text),
                Result(size=len(text), data=text),
                )
        ),

    5: Oggfile(
        data = array('B',
            [0]*26 +                        # Header
            [3]    +                        # Nr of segments
            [len(full), 0, len(text)] +     # Segment table
            list(full) + list(text))        # Segments
        ,
        description =
            'One page with two packets, first 2 segments, second 1 segment '
            'len(packet[0]) == 255, len(packet[1]) == 5'
        ,
        results = (
                Result(size=len(full), data=full),
                Result(size=len(text), data=text),
                )
        ),

    6: Oggfile(
        data = array('B',
            [0]*26 +                                # Header
            [3]    +                                # Nr of segments
            [len(full), len(text), len(text)] +     # Segment table
            list(full) + list(text) + list(text))   # Segments
        ,
        description =
            'One page with two packets, first 2 segments, second 1 segment '
            'len(packet[0]) == 260, len(packet[1]) == 5'
        ,
        results = (
                Result(size=len(full+text), data=full+text),
                Result(size=len(text), data=text),
                )
        ),

    7: Oggfile(
        data = array('B',
            [0]*26 +              # Header
            [255]  +              # Nr of segments
            [len(full)] * 255 +   # Segment table
            list(full)*255 +      # Segments

            [0]*26 +              # Header
            [1]  +                # Nr of segments
            [len(text)]  +        # Segment table
            list(text) )          # Segments
        ,
        description =
            'Two pages with one packet'
            'len(packet) == 255*255 + 5'
        ,
        results = (
                Result(size=len(full)*255 + len(text), data=full*255+text),
                #Result(size=len(text), data=text),
                )
        ),
    8: Oggfile(
        data = array('B',
            [0]*26 +              # Header
            [3]  +                # Nr of segments
            [len(text),
                len(text)*4,
                len(text2)]  +   # Segment table

            list(text) +
            list(text)*4 +
            list(text2)         # Segments
            )

        ,
        description =
            'Three packets in one page'
        ,
        results = (
                Result(size=len(text),   data=text),
                Result(size=len(text)*4, data=text*4),
                Result(size=len(text2), data=text2),
                )
        ),
    9: Oggfile(
        data = array('B',
            [0]*26 +              # Header
            [4]  +                # Nr of segments

            # Segment table
            [len(text),
                len(text)*4,
                len(text2),
                len(text)*2,
            ]  +

            # Segments
            list(text) +
            list(text)*4 +
            list(text2)  +
            list(text)*2
            )

        ,
        description =
            'Four packets in one page'
        ,
        results = (
                Result(size=len(text),   data=text),
                Result(size=len(text)*4, data=text*4),
                Result(size=len(text2), data=text2),
                Result(size=len(text)*2, data=text*2),
                )
        ),
    10: Oggfile(
        data = array('B',
            [0]*26 +              # Header
            [255]  +              # Nr of segments
            [len(full)] * 255 +   # Segment table
            list(full)*255 +      # Segments

            [0]*26 +           # Header
            [1]    +           # Nr of segments
            [0])                # Segment table
                               # No segments
        ,
        description =
            'Two pages with one packet. '
            'Second page is empty, only has the end of packet segment '
        ,
        results = (
                Result(size=len(full)*255, data=full*255),
                )
        ),
    11: Oggfile(
        data = array('B',
            [0]*26 +              # Header
            [255]  +              # Nr of segments
            [len(full)] * 255 +   # Segment table
            list(full)*255 +      # Segments

            [1,2,3,4,5,6]+ [0] *20 +              # Header
            [1]  +                # Nr of segments
            [len(text)]  +        # Segment table
            list(text) )          # Segments
        ,
        description =
            'Two pages with one packet'
            'len(packet) == 255*255 + 5'
        ,
        results = (
                Result(size=len(full)*255 + len(text), data=full*255+text),
                #Result(size=len(text), data=text),
                )
        ),
    12: Oggfile(
        data = array('B',
            [0]*26 +              # Header
            [255]  +              # Nr of segments
            [len(full)] * 255 +   # Segment table
            list(full)*255 +      # Segments

            [0]*26 +              # Header
            [255]  +              # Nr of segments
            [len(full)] * 255 +   # Segment table
            list(full)*255 +      # Segments

            [0]*26 +              # Header
            [1]  +                # Nr of segments
            [len(text)]  +        # Segment table
            list(text) )          # Segments
        ,
        description =
            'Three pages with one packet'
            'len(packet) == 255*255 + 255*255 + 5'
        ,
        results = (
            Result(size=len(full)*255*2 + len(text), data=full*255*2+text),
                #Result(size=len(text), data=text),
                )
        ),
    14: Oggfile(
        data = array('B',
            [0]*26 +              # Header
            [255]  +              # Nr of segments
            [len(full)] * 255 +   # Segment table
            list(full)*255 +      # Segments

            [0]*26 +           # Header
            [2]    +           # Nr of segments
            [0, 5]+            # Segment table
            list(b'hello'))    # Segments
        ,
        description =
            'Two pages with two packets. '
            'Second page has the end of packet segment at start'
        ,
        results = (
                Result(size=len(full)*255, data=full*255),
                Result(size=5, data=b'hello'),
                )
        ),

}

def test_generator():
    for key, oggtest in oggtests.items():
        yield check_get_packet, oggtest



def check_get_packet(oggtest):
    input_file = io.BytesIO(oggtest.data)
    page = OggPage(input_file)

    packet_reader = page.get_packet_reader()
    for result in oggtest.results:
        packet = packet_reader.read()
        eq_(packet, result.data)
        eq_(len(packet), result.size)

class OggReaderTest(unittest.TestCase):

    def test_read_one_packet_two_pages(self):
        index = 11
        input_file = io.BytesIO(oggtests[index].data)
        page = OggPage(input_file)
        packet_reader = page.get_packet_reader()

        #import ipdb; ipdb.set_trace()
        out = packet_reader.read(1)
        #for i in range(255):
        out += packet_reader.read(255*255)
        out += packet_reader.read(4)

        self.assertEqual(len(out), oggtests[index].results[0].size)
        self.assertEqual(out, oggtests[index].results[0].data)

    def test_read_one_packet_two_pages_2(self):
        index = 14
        input_file = io.BytesIO(oggtests[index].data)
        page = OggPage(input_file)
        packet_reader = page.get_packet_reader()

        out = packet_reader.read(255*255)
        self.assertEqual(len(out), oggtests[index].results[0].size)
        self.assertEqual(out, oggtests[index].results[0].data)

        out = packet_reader.read(1)
        self.assertEqual(len(out), 1)
        self.assertEqual(out, b'h')

    def test_read_one_packet_three_pages(self):

        index = 12
        input_file = io.BytesIO(oggtests[index].data)
        page = OggPage(input_file)
        packet_reader = page.get_packet_reader()

        out = packet_reader.read(1)
        out += packet_reader.read(255*255*2)
        out += packet_reader.read(4)

        self.assertEqual(len(out), oggtests[index].results[0].size)
        self.assertEqual(out, oggtests[index].results[0].data)

    def test_read_chunks(self):

        input_file = io.BytesIO(array('B', [0]*26 + [1, 4] +  list(b'pyta') ))
        page = OggPage(input_file)
        packet_reader = page.get_packet_reader()

        #import ipdb; ipdb.set_trace()
        out = packet_reader.read(2)
        self.assertEqual(len(out), 2)
        self.assertEqual(out, b'py')

        out = packet_reader.read(2)
        self.assertEqual(len(out), 2)
        self.assertEqual(out, b'ta')


class PacketReaderTest(unittest.TestCase):

    def get_reader(self, data, results):

        iterator = results.__iter__()
        return PacketReader(io.BytesIO(data), lambda: iterator.__next__())

    def test_read_all(self):
        reader = self.get_reader(b'a',
                                 [(1,True)])
        self.assertEqual(b'a', reader.read())

    def test_read_all_splited(self):
        reader = self.get_reader(b'ab',
                                 [(1,False), (1,True)])

        self.assertEqual(b'ab', reader.read())

    def test_read_current_page(self):
        reader = self.get_reader(b'ab',
                                 [(1,False), (1,True)])
        self.assertEqual(b'a', reader.read(1))
        self.assertEqual(b'b', reader.read(1))
        #self.assertEqual(b'', reader.read(1))

    def test_read_current_page_in_chunks(self):
        reader = self.get_reader(b'abcd',
                                 [(4,True)])
        self.assertEqual(b'a', reader.read(1))
        self.assertEqual(b'b', reader.read(1))
        self.assertEqual(b'cd', reader.read(2))
        #self.assertEqual(b'', reader.read(1))

    def test_read_two_pages(self):
        reader = self.get_reader(b'ab',
                                 [(1,False), (1,True)])
        self.assertEqual(b'ab', reader.read(2))
        #self.assertEqual(b'', reader.read(1))

    def test_read_multiple_pages(self):
        reader = self.get_reader(b'abcd',
                                 [(1,False), (1,False), (1,False),(1,True)])
        self.assertEqual(b'ab', reader.read(2))
        self.assertEqual(b'c', reader.read(1))
        self.assertEqual(b'd', reader.read())
        #self.assertEqual(b'', reader.read(1))
        #self.assertEqual(b'', reader.read())

    def test_read_multiple_pages_in_chunks(self):
        reader = self.get_reader(b'abcde',
                                 [(2,False), (1,False), (1,False),(1,True)])
        self.assertEqual(b'a', reader.read(1))
        self.assertEqual(b'bc', reader.read(2))
        self.assertEqual(b'de', reader.read())
        #self.assertEqual(b'', reader.read(1))
        #self.assertEqual(b'', reader.read())

    def test_read_multiple_pages_in_chunks_2(self):
        reader = self.get_reader(b'abcde',
                                 [(2,True), (1,False), (1,False),(1,True)])
        self.assertEqual(b'ab', reader.read(2))
        reader.position = 0  # Force read next packet
        self.assertEqual(b'cd', reader.read(2))
        self.assertEqual(b'e', reader.read())
        #self.assertEqual(b'', reader.read(1))
        #self.assertEqual(b'', reader.read())

    def test_read_multiple_pages_in_chunks_3(self):
        reader = self.get_reader(b'abcde',
                                 [(2,True), (1,False), (1,False),(1,True)])
        self.assertEqual(b'a', reader.read(1))
        self.assertEqual(b'bc', reader.read(2))
        self.assertEqual(b'de', reader.read())

    def test_read_multiple_pages_in_chunks_4(self):
        reader = self.get_reader(b'abcde',
                                 [(1,True), (4,True)])
        self.assertEqual(b'a', reader.read())
        self.assertEqual(b'bcde', reader.read())

    def test_read_multiple_pages_in_chunks_5(self):
        reader = self.get_reader(b'abcde',
                                 [(1,True), (4,True)])
        self.assertEqual(b'a', reader.read())
        self.assertEqual(b'bc', reader.read(2))
        self.assertEqual(b'de', reader.read(2))

    def test_read_multiple_pages_in_chunks_6(self):
        reader = self.get_reader(b'abcde12',
                                 [(1,True), (4,True), (2,True)])
        self.assertEqual(b'a', reader.read())
        reader.position = 0
        self.assertEqual(b'bc', reader.read(2))
        self.assertEqual(b'de', reader.read(2))
        reader.position = 0
        self.assertEqual(b'12', reader.read(2))
