# Do H.264 core decoding process
#
# Copyright (C) <2020>  <cookwhy@qq.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
from h26x_extractor import h26x_parser
from bitstring import BitStream, BitArray
from NaluParser import *

def get_sps(bytes):
    # do something with the NALU bytes
    logging.debug(bytes)

def do_something(bytes):
    # do something with the NALU bytes
    logging.debug(bytes)

def main(h264file):
    """
    Args:
        h264file: h264file name, should be using suffix .264 o .h264
    """
    # Test Case 1: use test data with one macroblock directly, hard code binary data
    #sps = BitStream('0x42c01edb02004190')
    #pps = BitStream('0xca83cb20')
    #nal = BitStream('0x88843f0a60109e4400020ed2fd431c63a895f346c35c5f92408f38eae8430cc80c8abc765961')

    # Test Case 2: read H264 binary code from file

    # Option1: use H264Parser to read file directly
    # TODO: something wrong with h264parser, need to fix later
    # h264parser = h26x_parser.H26xParser(h264file)
    # h264parser.set_callback("sps", get_sps)
    # h264parser.set_callback("nalu", do_something)
    # h264parser.parse()

    # Option2: use position directly for test
    b = BitArray(bytes=open(h264file, 'rb').read())
    sps = BitStream(b[5*8: 13*8])
    logging.debug("sps: %s", sps)
   
    pps = BitStream(b[18*8: 22*8])
    logging.debug("pps: %s", pps)
    
    nal = BitStream(b[26*8: b.len])
    logging.debug("data: %s", nal[0:800])

    # do the decoding things
    sps_parser = SpsParser()
    sps_parser.parse(sps)

    pps_parser = PpsParser()
    pps_parser.parse(pps)

    nal_parser = NalParser()
    nal_parser.parse(nal, sps_parser, pps_parser)
    

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("H264Decoder.log", mode='w'),
            logging.StreamHandler(),
        ]
    )

    main("../test/lena_x264_baseline_I_16x16.264")