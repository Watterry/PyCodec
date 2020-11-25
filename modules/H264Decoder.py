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
# there is something wrong using h26x_extractor installed package
# so including h26x source code directly
#from h26x_extractor import h26x_parser
import h26x_parser

from bitstring import BitStream, BitArray
from NaluParser import *
import prediction

sps_parser = SpsParser()
pps_parser = PpsParser()
nal_parser = NalParser()

index = 0

def get_sps(bytes):
    # do something with the NALU bytes
    logging.debug("get sps")
    logging.debug(bytes)
    sps_parser.parse( BitStream(bytes) )

def get_pps(bytes):
    # do something with the NALU bytes
    logging.debug("get pps")
    logging.debug(bytes)
    pps_parser.parse( BitStream(bytes) )

def get_aud(bytes):
    # do something with the NALU bytes
    logging.debug("aud")
    return bytes

def get_slice(bytes):
    # do something with the NALU bytes
    logging.debug("----------- slice ---------------")

    global index
    if index==0:
        index = index + 1
        return

    image = nal_parser.parse(BitStream(bytes), sps_parser, pps_parser)

    plt.figure()
    plt.imshow(image, cmap='gray')
    plt.title("Inverse image")
    #np.save("image.npy", image)

    plt.show()

def get_nalu(bytes):
    # do something with the NALU bytes
    #logging.debug(bytes)
    logging.debug("nalu bytes")

def main(h264file):
    """
    Args:
        h264file: h264file name, should be using suffix .264 o .h264
    """
    # Test Case 1: use test data with one macroblock directly, hard code binary data
    # sps = BitStream('0x42c01edb02004190')
    # pps = BitStream('0xca83cb20')
    # nal = BitStream('0x88843f0a60109e4400020ed2fd431c63a895f346c35c5f92408f38eae8430cc80c8abc765961')

    # Test Case 2: read H264 binary code from file

    # Option1: use H264Parser to read file directly
    # TODO: something wrong with h264parser, need to fix later
    h264parser = h26x_parser.H26xParser(h264file)
    #h264parser.set_callback("nalu", do_something)
    h264parser.set_callback("sps", get_sps)
    h264parser.set_callback("pps", get_pps)
    h264parser.set_callback("aud", get_aud)
    h264parser.set_callback("slice", get_slice)
    h264parser.set_callback("nalu", get_nalu)
    h264parser.parse()

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("H264Decoder.log", mode='w'),
            logging.StreamHandler(),
        ]
    )
    logging.getLogger('matplotlib.font_manager').disabled = True

    leadingZeroBits = 2
    temp = 'bits:'+str(leadingZeroBits)

    temp = BitStream('0b01')
    temp2 = pow(2, leadingZeroBits) - 1 + temp.int

    main("../test/BasketballPass_720p_P_16x16_without_Intra_4x4.264")
    #main("E:/liumangxuxu/code/PyCodec/test/lena_x264_baseline_I_16x16.264")