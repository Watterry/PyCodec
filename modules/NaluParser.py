# H.264 Nalu Streamer parser

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
#

# Based on the document of ITU-T Recommendation H.264 05/2003 edition

import logging
from bitstring import BitStream, BitArray
import H264Types
import vlc
import cavlc
import numpy as np
import copy

#class NaluResolver():
#    def __init__(self):

class SpsParser():
    """
    sps parser, get all the element value of sps
    """
    def parse(self, spsNalu):
        """
        Parse sps binary data, the input data should not include 0x00000001 start code
        Args:
            spsNalu: BitStream data: 1. input sps data without 0x00000001 start code
                                     2. the input data is rbsp_trailing_bits
        """
        logging.info("seq_parameter_set_rbsp()")
        logging.info("{")
        
        stream = spsNalu
        self.profile_idc = stream.read(8).uint # u(8)
        self.constraint_set0_flag = stream.read(1).uint # u(1)
        self.constraint_set1_flag = stream.read(1).uint # u(1)
        self.constraint_set2_flag = stream.read(1).uint # u(1)

        logging.info("  profile_idc: %d", self.profile_idc)
        logging.info("  constraint_set0_flag: %s", "true" if self.constraint_set0_flag else "false")
        logging.info("  constraint_set1_flag: %s", "true" if self.constraint_set1_flag else "false")
        logging.info("  constraint_set2_flag: %s", "true" if self.constraint_set2_flag else "false")

        self.reserved_zero_2bits = stream.read(5).bin    # u(5)
        self.level_idc = stream.read(8).uint # u(8)
        self.seq_parameter_set_id = stream.read('ue')  #ue(v)
        self.log2_max_frame_num_minus4 = stream.read('ue') #ue(v)
        self.pic_order_cnt_type = stream.read('ue') #ue(v)

        logging.info("  level_idc: %d", self.level_idc)
        logging.info("  seq_parameter_set_id: %d", self.seq_parameter_set_id)
        logging.info("  log2_max_frame_num_minus4: %d", self.log2_max_frame_num_minus4)
        logging.info("  pic_order_cnt_type: %d", self.pic_order_cnt_type)

        if self.pic_order_cnt_type == 0:
            self.log2_max_pic_order_cnt_lsb_minus4 = stream.read('ue')  #ue(v)
            logging.info("  log2_max_pic_order_cnt_lsb_minus4: %d", self.log2_max_pic_order_cnt_lsb_minus4)
        elif self.pic_order_cnt_type == 1:
            self.delta_pic_order_always_zero_flag = stream.read(1).uint # u(1)
            self.offset_for_non_ref_pic = stream.read('se')
            self.offset_for_top_to_bottom_field = stream.read('se')
            self.num_ref_frames_in_pic_order_cnt_cycle = stream.read('ue')
            logging.info("  delta_pic_order_always_zero_flag: %d", self.delta_pic_order_always_zero_flag)
            logging.info("  offset_for_non_ref_pic: %d", self.offset_for_non_ref_pic)
            logging.info("  offset_for_top_to_bottom_field: %d", self.offset_for_top_to_bottom_field)
            logging.info("  num_ref_frames_in_pic_order_cnt_cycle: %d", self.num_ref_frames_in_pic_order_cnt_cycle)

            offset_for_ref_frame = []
            for i in range(self.num_ref_frames_in_pic_order_cnt_cycle):
                offset_for_ref_frame[i] = stream.read('se')
                self.offset_for_ref_frame = offset_for_ref_frame

        self.num_ref_frames = stream.read('ue')
        self.gaps_in_frame_num_value_allowed_flag = stream.read(1).uint
        self.pic_width_in_mbs_minus1 = stream.read('ue')  #ue(v)
        self.pic_height_in_map_units_minus1 = stream.read('ue')  #ue(v)
        self.frame_mbs_only_flag = stream.read(1).uint
        logging.info("  num_ref_frames: %d", self.num_ref_frames)
        logging.info("  gaps_in_frame_num_value_allowed_flag: %s", "true" if self.gaps_in_frame_num_value_allowed_flag else "false")
        logging.info("  pic_width_in_mbs_minus1: %d", self.pic_width_in_mbs_minus1)
        logging.info("  pic_height_in_map_units_minus1: %d", self.pic_height_in_map_units_minus1)
        logging.info("  frame_mbs_only_flag: %s", "true" if self.frame_mbs_only_flag else "false")

        if self.frame_mbs_only_flag == 0:
            self.mb_adaptive_frame_field_flag = stream.read(1).uint
            logging.info("  mb_adaptive_frame_field_flag: %s", "true" if self.mb_adaptive_frame_field_flag else "false")
        else:
            self.mb_adaptive_frame_field_flag = 0

        self.direct_8x8_inference_flag = stream.read(1).uint
        self.frame_cropping_flag = stream.read(1).uint
        logging.info("  direct_8x8_inference_flag: %s", "true" if self.direct_8x8_inference_flag else "false")
        logging.info("  frame_cropping_flag: %s", "true" if self.frame_cropping_flag else "false")
        if self.frame_cropping_flag:
            self.frame_crop_left_offset = stream.read('ue')  #ue(v)
            self.frame_crop_right_offset = stream.read('ue')  #ue(v)
            self.frame_crop_top_offset = stream.read('ue')  #ue(v)
            self.frame_crop_bottom_offset = stream.read('ue')  #ue(v)

        self.vui_parameters_present_flag = stream.read(1).uint
        logging.info("  vui_parameters_present_flag: %s", "true" if self.vui_parameters_present_flag else "false")
        if self.vui_parameters_present_flag:
            self.vui_parameters()

        logging.info("}")

    def vui_parameters(self):
        logging.error("vui_parameters is not work right now!")

class PpsParser():
    """
    pps parser, get all the element value of pps
    """
    def parse(self, ppsNalu):
        """
        Parse pps binary data, the input data should not include 0x00000001 start code
        Args:
            ppsNalu: BitStream data: 1. input sps data without 0x00000001 start code
                                     2. the input data is rbsp_trailing_bits
        """
        logging.info("pic_parameter_set_rbsp()")
        logging.info("{")
        
        stream = ppsNalu

        self.pic_parameter_set_id = stream.read('ue') #ue(v)
        self.seq_parameter_set_id = stream.read('ue') #ue(v)
        self.entropy_coding_mode_flag = stream.read(1).uint
        self.pic_order_present_flag = stream.read(1).uint
        logging.info("  pic_parameter_set_id: %d", self.pic_parameter_set_id)
        logging.info("  seq_parameter_set_id: %d", self.seq_parameter_set_id)
        logging.info("  entropy_coding_mode_flag: %s", "true" if self.entropy_coding_mode_flag else "false")
        logging.info("  pic_order_present_flag: %s", "true" if self.pic_order_present_flag else "false")

        self.num_slice_groups_minus1 = stream.read('ue') #ue(v)
        logging.info("  num_slice_groups_minus1: %d", self.num_slice_groups_minus1)

        if self.num_slice_groups_minus1 > 0:
            self.slice_group_map_type = stream.read('ue')
            # TODO: add more branch here

        self.num_ref_idx_l0_active_minus1 = stream.read('ue') #ue(v)
        logging.info("  num_ref_idx_l0_active_minus1: %d", self.num_ref_idx_l0_active_minus1)

        self.num_ref_idx_l1_active_minus1 = stream.read('ue') #ue(v)
        logging.info("  num_ref_idx_l1_active_minus1: %d", self.num_ref_idx_l1_active_minus1)

        self.weighted_pred_flag = stream.read(1).uint
        logging.info("  weighted_pred_flag: %s", "true" if self.weighted_pred_flag else "false")

        self.weighted_bipred_idc = stream.read(2).uint
        logging.info("  weighted_bipred_idc: %d", self.weighted_bipred_idc)

        self.pic_init_qp_minus26 = stream.read('se') #se(v)
        logging.info("  pic_init_qp_minus26: %d", self.pic_init_qp_minus26)

        self.pic_init_qs_minus26  = stream.read('se') #se(v)
        logging.info("  pic_init_qs_minus26: %d", self.pic_init_qs_minus26)

        self.chroma_qp_index_offset  = stream.read('se') #se(v)
        logging.info("  chroma_qp_index_offset: %d", self.chroma_qp_index_offset)

        self.deblocking_filter_control_present_flag = stream.read(1).uint
        logging.info("  deblocking_filter_control_present_flag: %s", "true" if self.deblocking_filter_control_present_flag else "false")

        self.constrained_intra_pred_flag = stream.read(1).uint
        logging.info("  constrained_intra_pred_flag: %s", "true" if self.constrained_intra_pred_flag else "false")

        self.redundant_pic_cnt_present_flag = stream.read(1).uint
        logging.info("  redundant_pic_cnt_present_flag: %s", "true" if self.redundant_pic_cnt_present_flag else "false")

        logging.info("}")

class NalParser():
    """
    Slice parser, get all the element value of nalu
    Currently just support one keyframe input and one slice in keyframe
    """
    def parse(self, NaluUnit, SPS, PPS):
        """
        Parse nalu binary data, the input data should not include 0x00000001 start code
        Args:
            NaluUnit: BitStream data: 1. input sps data without 0x00000001 start code
                                      2. the input data is rbsp_trailing_bits
            spsParser: the sps of current sequence, should be type of SpsParser
            ppsParser: the pps of curretn sequence, should be type of PpsParser
        """
        logging.info("slice_header()")
        logging.info("{")
        
        self.stream = NaluUnit
        self.sps = SPS
        self.pps = PPS

        #slice_header
        self.first_mb_in_slice = self.stream.read('ue') #ue(v)
        logging.info("  first_mb_in_slice: %d", self.first_mb_in_slice)

        self.slice_type = self.stream.read('ue') #ue(v)
        logging.info("  slice_type: %s", H264Types.slice_type(self.slice_type))

        self.pic_parameter_set_id = self.stream.read('ue') #ue(v)
        logging.info("  pic_parameter_set_id: %d", self.pic_parameter_set_id)

        length = SPS.log2_max_frame_num_minus4 + 4
        self.frame_num = self.stream.read(length).uint
        logging.info("  frame_num: %d", self.frame_num)

        if not SPS.frame_mbs_only_flag:
            self.field_pic_flag = self.stream.read(1).uint
            logging.info("  field_pic_flag: %d", self.field_pic_flag)
            if self.field_pic_flag:
                self.bottom_field_flag = self.stream.read(1).uint
                logging.info("  bottom_field_flag: %d", self.bottom_field_flag)

        nal_unit_type = 5   #TODO: nal_unit_type should passed in by outside or parse by self??
        if nal_unit_type == 5:
            self.idr_pic_id = self.stream.read('ue') #ue(v)
            logging.info("  idr_pic_id: %d", self.idr_pic_id)

        #TODO: add a lot of parse process here

        nal_ref_idc = 0   #TODO: nal_ref_idc should passed in by outside or parse by self??
        if not nal_ref_idc:
            if nal_unit_type == 5:
                self.no_output_of_prior_pics_flag = self.stream.read(1).uint
                self.long_term_reference_flag = self.stream.read(1).uint
                logging.info("  no_output_of_prior_pics_flag: %s", "true" if self.no_output_of_prior_pics_flag else "false")
                logging.info("  long_term_reference_flag: %s", "true" if self.long_term_reference_flag else "false")
            else:
                self.adaptive_ref_pic_marking_mode_flag = self.stream.read(1).uint
                #TODO add more process here

        # if PPS.entropy_coding_mode_flag and (self.slice_type!=H264Types.slice_type('I') or self.slice_type!=H264Types.slice_type('I7'))
        #    and (self.slice_type!=H264Types.slice_type('SI') or self.slice_type!=H264Types.slice_type('SI9')):
        if PPS.entropy_coding_mode_flag:
           self.cabac_init_idc = self.stream.read('ue') #ue(v)
           logging.info("  cabac_init_idc: %d", self.cabac_init_idc)

        self.slice_qp_delta = self.stream.read('se') #se(v)
        logging.info("  slice_qp_delta: %d", self.slice_qp_delta)

        if PPS.deblocking_filter_control_present_flag:
            self.disable_deblocking_filter_idc = self.stream.read('ue') #ue(v)
            logging.info("  disable_deblocking_filter_idc: %d", self.disable_deblocking_filter_idc)
            if self.disable_deblocking_filter_idc != 1:
                self.slice_alpha_c0_offset_div2 = self.stream.read('se') #se(v)
                logging.info("  slice_alpha_c0_offset_div2: %d", self.slice_alpha_c0_offset_div2)

                self.slice_beta_offset_div2 = self.stream.read('se') #se(v)
                logging.info("  slice_beta_offset_div2: %d", self.slice_beta_offset_div2)
        
        logging.info("}")

        #slice data
        logging.debug("slice data: %s", self.stream.peek(32))   # check the start data of slice_data
        self.__slice_data()

    def __slice_data(self):
        """
        do slice_data() part of H.264 standard
        """
        logging.debug("slice data: %s", self.stream.peek(32))   # check the start data of slice_data
        if self.pps.entropy_coding_mode_flag:
            self.cabac_alignment_one_bit = self.stream.read(1)   #TODO: not verify the validity

        # based on page 62 of ITU-T Recommendation H.264 05/2003 edition
        MbaffFrameFlag = ( self.sps.mb_adaptive_frame_field_flag and (not self.field_pic_flag) )
        CurrMbAddr = self.first_mb_in_slice * ( 1 + MbaffFrameFlag )
        moreDataFlag = 1
        prevMbSkipped = 0

        width = int(512)  #TODO: get this from sps & pps
        height = int(512) #TODO: get this from sps & pps
        self.coefficients = np.zeros((width, height), int)
        self.nAnB = np.zeros((int(width/4), int(height/4)), int)

        self.blk16x16Idx_x = 0   # x position of 16x16 block in this frame
        self.blk16x16Idx_y = 0   # y position of 16x16 block in this frame

        row_block_num = int(width / 16)   # the total num of 16x16 blocks in row
        col_block_num = int(height / 16)  # the total num of 16x16 blocks in column

        while moreDataFlag:

            logging.debug("----------------------------------------")
            if moreDataFlag:
                if( MbaffFrameFlag and ( CurrMbAddr%2==0 or (CurrMbAddr%2==1 and prevMbSkipped) ) ):
                    self.mb_field_decoding_flag = 0
                
                #parsing macroblock_layer()
                self.__macroblock_layer()

            # do next process
            if not self.pps.entropy_coding_mode_flag:
                moreDataFlag = self.__more_rbsp_data()
            else:
                logging.error("Not finish this part yet!")

            # TODO: not finish yet
            #CurrMbAddr = NextMbAddress( CurrMbAddr )

            self.blk16x16Idx_x = self.blk16x16Idx_x + 1
            if self.blk16x16Idx_x >= row_block_num:
                self.blk16x16Idx_x = 0
                self.blk16x16Idx_y = self.blk16x16Idx_y + 1

    def __macroblock_layer(self):
        """
        do macroblock_layer() part of H.264 standard
        """
        startPos = self.stream.pos
        self.mb_type = self.stream.read('ue') #ue(v)

        self.CodedBlockPatternChroma = H264Types.get_I_slice_CodedBlockPatternChroma(self.mb_type)
        self.CodedBlockPatternLuma = H264Types.get_I_slice_CodedBlockPatternLuma(self.mb_type)

        logging.info("  mb_type: %s", H264Types.I_slice_Macroblock_types[self.mb_type][0])
        logging.info("  CodedBlockPatternLuma: %d", self.CodedBlockPatternLuma)
        logging.info("  CodedBlockPatternChroma: %d", self.CodedBlockPatternChroma)

        # mb_pred()
        self.intra_chroma_pred_mode = self.stream.read('ue')
        logging.info("  intra_chroma_pred_mode: %d", self.intra_chroma_pred_mode)

        if (self.CodedBlockPatternLuma>0 or self.CodedBlockPatternChroma>0 or 
            (self.mb_type!=0 and self.mb_type!=25)):
            self.mb_qp_delta = self.stream.read('se')
            self.SliceQPy = 26 + self.pps.pic_init_qp_minus26 + self.slice_qp_delta
            logging.info("  mb_qp_delta: %d", self.mb_qp_delta)
            logging.info("  Slice QP: %d", self.SliceQPy)

        #residual
        temp = self.stream[startPos: self.stream.pos]
        logging.debug("residual header: %s", temp.bin) 
        logging.debug("residual body: %s", self.stream.peek(32).bin)   # check the start data of slice_data

        #logging.debug("nAnB:")
        #logging.debug("\n%s" % (self.nAnB[0:4, 0:4]))

        nC = self.__get_nC(self.blk16x16Idx_y*4, self.blk16x16Idx_x*4)
        logging.info("  blk16x16Idx_x: %d, blk16x16Idx_y: %d, nC: %d", self.blk16x16Idx_x, self.blk16x16Idx_y, nC)
        
        blocks = self.stream[self.stream.pos: self.stream.len]
        Intra16x16DCLevel, position, temp = cavlc.decode(blocks, nC, 16)
        temp = self.stream.read(position)   # drop the decoded data
        logging.debug("processed data: %s", temp.bin)
        logging.debug("Intra16x16DCLevel: %s", Intra16x16DCLevel)

        coeffBlock_16x16 = np.zeros((16, 16), int)

        if self.CodedBlockPatternLuma>0:
            luma4x4BlkIdx = 0
            for m in range(0, 2):
                for n in range(0, 2):
                    for i in range(0, 2):
                        for j in range(0, 2):
                            #different nC
                            x = m*2+i
                            y = n*2+j
                            abs_row = self.blk16x16Idx_y*4 + x
                            abs_col = self.blk16x16Idx_x*4 + y
                            nC = self.__get_nC(abs_row, abs_col)
                            logging.debug("decoding blockInx: %d, nC: %d", luma4x4BlkIdx, nC)
                            logging.debug("x, y in nAnB matrix: %d, %d", abs_row, abs_col)
                            
                            example_len = 80 if (self.stream.len-self.stream.pos)>80 else (self.stream.len-self.stream.pos)
                            logging.debug("following data: %s", self.stream.peek(example_len).bin)
                            blocks = self.stream[self.stream.pos: self.stream.len]
                            Intra4x4ACLevel, position, self.nAnB[abs_row,abs_col] = cavlc.decode(blocks, nC, self.CodedBlockPatternLuma)

                            temp = self.stream.read(position)   # drop the decoded data
                            logging.debug("processed data: %s", temp.bin)
                            logging.debug("Intra16x16ACLevel_%d:", luma4x4BlkIdx)
                            logging.debug("\n%s" % (Intra4x4ACLevel))

                            coeffBlock_16x16[x*4:(x*4+4), y*4:(y*4+4)] = copy.deepcopy(Intra4x4ACLevel)

                            luma4x4BlkIdx = luma4x4BlkIdx + 1

        for i in range(0, 4):
            for j in range(0, 4):
                coeffBlock_16x16[i*4, j*4] = Intra16x16DCLevel[i, j]
        logging.debug("Reconstructed 16x16 coefficients:")
        logging.debug("\n%s", coeffBlock_16x16)

        # dupm luma block to image
        self.coefficients[self.blk16x16Idx_x*16:(self.blk16x16Idx_x+1)*16, self.blk16x16Idx_y*16:(self.blk16x16Idx_y+1)*16] = copy.deepcopy(coeffBlock_16x16)
        #logging.debug("Reconstructed image coefficients:")
        #logging.debug("\n%s", coefficients)

        # chroma DC level, accroding to page 75 on [H.264 standard Book]
        logging.debug("Decoding Chroma DC level")
        example_len = 80 if (self.stream.len-self.stream.pos)>80 else (self.stream.len-self.stream.pos)
        logging.debug("following data: %s", self.stream.peek(example_len).bin)

        if self.CodedBlockPatternChroma>0:
            for i in range(0, 2):
                blocks = self.stream[self.stream.pos: self.stream.len]
                ChromaDCLevel, position, temp = cavlc.decode(blocks, -1, 4)
                temp = self.stream.read(position)   # drop the decoded data
                logging.debug("processed data: %s", temp.bin)
                logging.debug("ChromaDCLevel_%d:", i)
                logging.debug("\n%s" % (ChromaDCLevel))
        else:
            # two DC are zeros
            logging.debug("Two Chroma DC are zeros")

        if self.CodedBlockPatternChroma==2:
            for m in range(0, 2):   # cb & cr
                chroma4x4BlkIdx = 0
                nC = 0
                for i in range(0, 2):
                    for j in range(0, 2):
                        #different nC
                        logging.debug("decoding blockInx: %d, nC: %d", chroma4x4BlkIdx, nC)

                        #logging.debug("x, y in nAnB matrix: %d, %d", x, y)
                        #nC = self.__get_nC(x, y)
                        example_len = 80 if (self.stream.len-self.stream.pos)>80 else (self.stream.len-self.stream.pos)
                        logging.debug("following data: %s", self.stream.peek(example_len).bin)
                        blocks = self.stream[self.stream.pos: self.stream.len]
                        Chroma4x4ACLevel, position, temp = cavlc.decode(blocks, nC, 15)

                        temp = self.stream.read(position)   # drop the decoded data
                        logging.debug("processed data: %s", temp.bin)
                        logging.debug("Chroma4x4ACLevel_%d:", chroma4x4BlkIdx)
                        logging.debug("\n%s" % (Chroma4x4ACLevel))

                        #coeffBlock_16x16[x*4:(x*4+4), y*4:(y*4+4)] = copy.deepcopy(Intra4x4ACLevel)

                        chroma4x4BlkIdx = chroma4x4BlkIdx + 1
        else:
            # two 8x8 AC are zeros
            logging.debug("Two Chroma 8x8 AC are zeros")

    def __get_nC(self, row, col):
        """
        calculate nC of current 4x4 block
        Args:
            row: the row of current nC block
            col: the coloum of current nC block
        Returns:
            the nC value of current block
        """
        nA = 0
        nB = 0
        nC = 0

        i = row - 1
        j = col - 1

        if row==0 and col==0:
            nA = 0
            nB = 0
            nC = nA + nB
        elif row==0:
            nA = self.nAnB[row, col-1]
            nB = 0
            nC = nA + nB
        elif col==0:
            nA = 0
            nB = self.nAnB[row-1, col]
            nC = nA + nB
        else:
            nA = self.nAnB[row, col-1]
            nB = self.nAnB[row-1, col]
            nC = (nA + nB + 1) >> 1

        return nC

    def __more_rbsp_data(self):
        """
        Judge if left block is rbsp_slice_traing_bits()
        TODO: not finished yet
        Returns:
            True or False of more_rbsp_data() in H.264 standard
        """
        if self.stream.len-self.stream.pos > 16:
            return True
        else:
            return False

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
            logging.FileHandler("NaluParser.log", mode='w'),
            logging.StreamHandler(),
        ]
    )

    logging.debug("Unit test for NaluParser")

    main("E:/liumangxuxu/code/PyCodec/test/lena_x264_baseline_I_16x16.264")