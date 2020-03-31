# Do H.264 core decoding process
import logging
from h26x_extractor import h26x_parser
from bitstring import BitStream, BitArray
from NaluParser import *

def get_sps(bytes):
    # do something with the NALU bytes
    logging.debug(bytes)

def main(h264file):
    """
    Args:
        h264file: h264file name, should be using suffix .264 o .h264
    """
    # TODO: something wrong with h264parser, need to fix later
    #h264parser = h26x_parser.H26xParser(h264file)
    #h264parser.set_callback("sps", get_sps)
    #h264parser.parse()

    # use test data directly, hard code binary data
    sps = BitStream('0x42c01edb02004190')
    pps = BitStream('0xca83cb20')
    nal = BitStream('0x88843f0a60109e4400020ed2fd431c63a895f346c35c5f92408f38eae8430cc80c8abc765961')

    sps_parser = SpsParser()
    sps_parser.parse(sps)
    

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