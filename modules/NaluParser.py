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
import sys
import matplotlib.pyplot as plt
import transform
import statistics
import prediction

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

        self.PicWidthInSamples = (self.pic_width_in_mbs_minus1+1) * 16
        self.PicHeightInSamples = (self.pic_height_in_map_units_minus1+1) * 16
        logging.info("  width: %d, height %d", self.PicWidthInSamples, self.PicHeightInSamples)

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

    def getWidth(self):
        return self.PicWidthInSamples

    def getHeight(self):
        return self.PicHeightInSamples

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
        
        Returns:
            residual of current frame
            prediction mode map of all macroblock block
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

        #hard code for nal_unit_type, temp code
        #nal_unit_type should be passed by outside in NAL parser
        if self.slice_type == H264Types.slice_type.I7.value:
            nal_unit_type = 5
        else:
            nal_unit_type = 1

        if nal_unit_type == 5:
            self.idr_pic_id = self.stream.read('ue') #ue(v)
            logging.info("  idr_pic_id: %d", self.idr_pic_id)

        if self.slice_type == H264Types.slice_type.p5.value:
            self.num_ref_idx_active_override_flag = self.stream.read('uint:1')
            logging.info("  num_ref_idx_active_override_flag: %d", self.num_ref_idx_active_override_flag)
            if self.num_ref_idx_active_override_flag:
                self.num_ref_idx_l0_active_minus1 = self.stream.read('ue')
                logging.info("  num_ref_idx_l0_active_minus1: %d", self.num_ref_idx_l0_active_minus1)

        # ref_pic_list_reordering( )
        if self.slice_type != H264Types.slice_type.I7.value and self.slice_type != H264Types.slice_type.SI.value:
            self.ref_pic_list_reordering_flag_l0 = self.stream.read('uint:1')
            logging.info("  ref_pic_list_reordering_flag_l0: %d", self.ref_pic_list_reordering_flag_l0)
            if self.ref_pic_list_reordering_flag_l0:
                logging.error("  This part is not supported yet!")

        #TODO: nal_ref_idc should passed in by outside
        # below is just temp code
        if self.slice_type == H264Types.slice_type.I7.value:
            nal_ref_idc = 3
        else:
            nal_ref_idc = 0
        if nal_ref_idc!=0:
            if nal_unit_type == 5:
                self.no_output_of_prior_pics_flag = self.stream.read(1).uint
                self.long_term_reference_flag = self.stream.read(1).uint
                logging.info("  no_output_of_prior_pics_flag: %s", "true" if self.no_output_of_prior_pics_flag else "false")
                logging.info("  long_term_reference_flag: %s", "true" if self.long_term_reference_flag else "false")
            else:
                self.adaptive_ref_pic_marking_mode_flag = self.stream.read(1).uint
                if self.adaptive_ref_pic_marking_mode_flag:
                    logging.error("  adaptive_ref_pic_marking_mode_flag part is not support yet!")

        # if PPS.entropy_coding_mode_flag and (self.slice_type!=H264Types.slice_type('I') or self.slice_type!=H264Types.slice_type('I7'))
        #    and (self.slice_type!=H264Types.slice_type('SI') or self.slice_type!=H264Types.slice_type('SI9')):
        if PPS.entropy_coding_mode_flag:
           self.cabac_init_idc = self.stream.read('ue') #ue(v)
           logging.info("  cabac_init_idc: %d", self.cabac_init_idc)

        self.slice_qp_delta = self.stream.read('se') #se(v)
        logging.info("  slice_qp_delta: %d", self.slice_qp_delta)
        self.SliceQPy = 26 + self.pps.pic_init_qp_minus26 + self.slice_qp_delta
        logging.info("  Slice QP: %d", self.SliceQPy)

        if PPS.deblocking_filter_control_present_flag:
            self.disable_deblocking_filter_idc = self.stream.read('ue') #ue(v)
            logging.info("  disable_deblocking_filter_idc: %d", self.disable_deblocking_filter_idc)
            if self.disable_deblocking_filter_idc != 1:
                self.slice_alpha_c0_offset_div2 = self.stream.read('se') #se(v)
                logging.info("  slice_alpha_c0_offset_div2: %d", self.slice_alpha_c0_offset_div2)

                self.slice_beta_offset_div2 = self.stream.read('se') #se(v)
                logging.info("  slice_beta_offset_div2: %d", self.slice_beta_offset_div2)
        
        logging.info("}")

        # temp code, load reference frame
        self.reference = np.load("../test/keyframe-BasketballPass_720p_P_16x16_without_Intra_4x4.npy")
        # plt.figure()
        # plt.imshow(self.reference, cmap='gray')
        # plt.title("Whole image")
        # plt.show()

        self.__slice_data()

        if self.MbPartPredMode == 'Intra_16x16':
            image = prediction.inverseIntraPrediction(self.residual, self.modemap, 16)
            return image
        else:
            return self.residual

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

        width = int(self.sps.getWidth())
        height = int(self.sps.getHeight())
        self.coefficients = np.zeros((height, width), int)
        self.residual = np.zeros((height, width), int)
        self.modemap = np.zeros((height, width), int)
        self.nAnB = np.zeros((int(height/4), int(width/4)), int)
        self.nAnB_UV = np.zeros((2, int(height/8), int(width/8)), int)

        self.mvd = np.zeros((int(height/16), int(width/16), 2), int)  # just support 16x16 macroblock
        self.mv  = np.zeros((int(height/16), int(width/16), 2), int)  # just support 16x16 macroblock

        self.blk16x16Idx_x = 0   # x position of 16x16 block in this frame
        self.blk16x16Idx_y = 0   # y position of 16x16 block in this frame

        row_block_num = int(width / 16)   # the total num of 16x16 blocks in row
        col_block_num = int(height / 16)  # the total num of 16x16 blocks in column


        macroblockIdx = 0

        while moreDataFlag:

            logging.debug("----------------------------------------")
            logging.debug("macroblockIdx: %d", macroblockIdx)

            if self.slice_type != H264Types.slice_type.I7.value and self.slice_type != H264Types.slice_type.I.value:
                if not self.pps.entropy_coding_mode_flag:
                    mb_skip_run = self.stream.read('ue')
                    logging.debug("mb_skip_run: %d", mb_skip_run)
                    prevMbSkipped = (mb_skip_run>0)

                    if mb_skip_run>0:
                        # do the skip calculation of following skip_run macroblock
                        for i in range(0, mb_skip_run):

                            self.__set_P_skip_macroblock()

                            macroblockIdx = macroblockIdx + 1
                            logging.debug("----------------------------------------")
                            logging.debug("macroblockIdx: %d", macroblockIdx)

                            self.blk16x16Idx_x = self.blk16x16Idx_x + 1
                            if self.blk16x16Idx_x >= row_block_num:
                                self.blk16x16Idx_x = 0
                                self.blk16x16Idx_y = self.blk16x16Idx_y + 1

            if moreDataFlag:
                if( MbaffFrameFlag and ( CurrMbAddr%2==0 or (CurrMbAddr%2==1 and prevMbSkipped) ) ):
                    self.mb_field_decoding_flag = self.stream.read('uint:1')
                else:
                    self.mb_field_decoding_flag = 0   # more complex situation
                
                #parsing macroblock_layer()
                self.__macroblock_layer()

                macroblockIdx = macroblockIdx + 1

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

            # if self.blk16x16Idx_x == 0 and self.blk16x16Idx_y == 45:
            #     moreDataFlag = False

    def __macroblock_layer(self):
        """
        do macroblock_layer() part of H.264 standard
        """
        startPos = self.stream.pos
        self.__show_binary_fragment()
        self.mb_type = self.stream.read('ue') #ue(v)

        self.MbPartPredMode = 'na'
        self.name_of_mb_type = 'na'
        self.NumMbPart = 1
        if self.slice_type == H264Types.slice_type.I7.value:
            # I slice
            self.name_of_mb_type = H264Types.I_slice_Macroblock_types[self.mb_type][0]
            self.MbPartPredMode = H264Types.I_slice_Macroblock_types[self.mb_type][1]
            self.NumMbPart = 1 # default value
        else:
            # p slice
            if self.mb_type<=4:
                self.name_of_mb_type = H264Types.P_slice_Macroblock_types[self.mb_type][0]
                self.MbPartPredMode = H264Types.P_slice_Macroblock_types[self.mb_type][2]
                self.NumMbPart = int(H264Types.P_slice_Macroblock_types[self.mb_type][1])
            else:
                self.name_of_mb_type = H264Types.I_slice_Macroblock_types[self.mb_type-5][0]
                self.MbPartPredMode = H264Types.I_slice_Macroblock_types[self.mb_type-5][1]
                self.NumMbPart = 1 #TODO: temp value

        logging.debug("macroblock_layer(){")
        logging.debug("  mb_type: %d", self.mb_type)
        logging.debug("  name of mb_type: %s", self.name_of_mb_type)
        logging.debug("  MbPartPredMode: %s", self.MbPartPredMode)

        if self.name_of_mb_type == 'I_PCM':
            logging.error("Not support I_PCM mb_type yet!")
        else:
            if self.MbPartPredMode != "Intra_4x4" and self.MbPartPredMode != "Intra_16x16" and self.NumMbPart==4:
                self.__sub_mb_pred()
                logging.error("Not support sub_mb_type yet!")
            else:
                self.__mb_pred()

            self.__show_binary_fragment()
            #self.stream.read('bits:26')
            #logging.debug("temp4 body: %s", self.stream.peek(64).bin)
            if self.MbPartPredMode != 'Intra_16x16' :
                if self.pps.entropy_coding_mode_flag == 0:
                    coded_block_pattern = self.__read_me()
                else:
                    coded_block_pattern = self.stream.read('ae')
                logging.debug("  coded_block_pattern: %d", coded_block_pattern)
                self.CodedBlockPatternLuma = coded_block_pattern % 16
                self.CodedBlockPatternChroma = coded_block_pattern // 16
            else:
                # Intra_16x16
                self.CodedBlockPatternChroma = H264Types.get_I_slice_CodedBlockPatternChroma(self.mb_type)
                self.CodedBlockPatternLuma = H264Types.get_I_slice_CodedBlockPatternLuma(self.mb_type)

        logging.debug("  CodedBlockPatternLuma: %d", self.CodedBlockPatternLuma)
        logging.debug("  CodedBlockPatternChroma: %d", self.CodedBlockPatternChroma)

        logging.debug("}")

        if (self.CodedBlockPatternLuma>0 or self.CodedBlockPatternChroma>0 or 
            self.MbPartPredMode == 'Intra_16x16'):
            self.mb_qp_delta = self.stream.read('se')
            logging.debug("  mb_qp_delta: %d", self.mb_qp_delta)
            #TODO: seems has some bug in below QP calculating
            self.mb_current_qp = (self.SliceQPy + self.mb_qp_delta + 52) % 52 # the QP of current macroblock
            logging.debug("  the value of QPY in the macroblock layer: %d", self.mb_current_qp)

            residual_header = self.stream[startPos: self.stream.pos]
            startPos = self.stream.pos
            self.__residual()
            logging.debug("residual header: %s", residual_header.bin) 
            residual_body = self.stream[startPos: self.stream.pos]
            logging.debug("residual body: %s", residual_body.bin)

    def __mb_pred(self):
        """
        mb_pred(), on page 42 of [H.264 standard Book]
        """
        if self.MbPartPredMode == 'Intra_4x4' or self.MbPartPredMode == 'Intra_16x16':
            #TODO: add Intra_4x4 part
            if self.MbPartPredMode == 'Intra_4x4':
                logging.error("Not support Intra_4x4 mb_pred subroutine yet!")
            self.intra_chroma_pred_mode = self.stream.read('ue')
            logging.debug("intra_chroma_pred_mode: %d", self.intra_chroma_pred_mode)
        elif self.MbPartPredMode != 'Direct':
            ref_idx_l0 = []

            for mbPartIdx in range(0, self.NumMbPart):
                if ((self.num_ref_idx_l0_active_minus1>0 or self.mb_field_decoding_flag) and
                    self.MbPartPredMode != 'Pred_L1'):
                    temp = self.__read_te()
                    ref_idx_l0.append(temp)
                    logging.debug("ref_idx_l0[%d]: %d", mbPartIdx, temp)
                else:
                    ref_idx_l0.append(0)
                    logging.debug("ref_idx_l0[0]: %d", ref_idx_l0[0])

            self.__show_binary_fragment()

            mvd_l0 = [0, 0]   # hard code for 16x16 macroblock
            for compIdx in range(0, 2):
                if self.pps.entropy_coding_mode_flag == 0:
                    #mvd_l0[0][0][compIdx] = self.stream.read('se')
                    mvd_l0[compIdx] = self.stream.read('se')
                else:
                    #mvd_l0[0][0][compIdx] = self.stream.read('ae')
                    mvd_l0[compIdx] = self.stream.peek(64)
            logging.debug("mvd_l0: %s", mvd_l0)
            self.__set_motion_vector(mvd_l0)

    def __sub_mb_pred(self):
        """
        sub_mb_pred
        TODO: not finish yet
        """
        sub_mb_type = []
        for mbPartIdx in range(0, 4):
            temp = self.stream.read('ue') #ue(v)
            sub_mb_type.append(temp)

        ref_idx_l0 = []
        if self.MbPartPredMode == 'P_8x8ref0':
            for mbPartIdx in range(0, self.NumMbPart):
                ref_idx_l0.append(0)
                logging.debug("ref_idx_l0[%d]: %d", mbPartIdx, 0)

    def __residual(self):
        """
        residual
        """
        row = self.blk16x16Idx_y*16
        col = self.blk16x16Idx_x*16

        # dump luma block to image
        if self.MbPartPredMode == 'Intra_16x16':
            coeffBlock_16x16, residual_16x16 = self.__residual_block_Intra16x16()
            self.coefficients[row:(row+16), col:(col+16)] = copy.deepcopy(coeffBlock_16x16)
            self.modemap[row:(row+16), col:(col+16)] = H264Types.get_I_slice_Intra16x16PredMode(self.mb_type)[0]
            self.residual[row:(row+16), col:(col+16)] = copy.deepcopy(residual_16x16)
        else:
            coeffBlock_16x16, residual_16x16 = self.__residual_block_LumaLevel()
            self.coefficients[row:(row+16), col:(col+16)] = copy.deepcopy(coeffBlock_16x16)
            self.residual[row:(row+16), col:(col+16)] = copy.deepcopy(residual_16x16)

        logging.debug("Reconstructed 16x16 coefficients:")
        logging.debug("\n%s", coeffBlock_16x16)

        logging.debug("Reconstructed 16x16 residual:")
        logging.debug("\n%s", residual_16x16)

        #logging.debug("Reconstructed image coefficients:")
        #logging.debug("\n%s", coefficients)

        # deifne UV plane
        UV_plane_16x16 = np.zeros((2, 8, 8), int)
        ChromaDCLevel = np.zeros((2, 2, 2), int)

        # chroma DC level, accroding to page 75 on [H.264 standard Book]
        logging.debug("Decoding Chroma DC level")
        self.__show_binary_fragment()

        for i in range(0, 2):
            if self.CodedBlockPatternChroma&3:
                blocks = self.stream[self.stream.pos: self.stream.len]
                ChromaDCLevel[i], position, temp = cavlc.decode(blocks, -1, 4)
                temp = self.stream.read(position)   # drop the decoded data
                logging.debug("processed data: %s", temp.bin)
                logging.debug("ChromaDCLevel_%d:", i)
                logging.debug("\n%s" % (ChromaDCLevel[i]))
            else:
                # two DC are zeros, already zeros, do nothing
                logging.debug("Two Chroma DC are zeros")

        if self.CodedBlockPatternChroma&2:
            for m in range(0, 2):   # cb & cr
                chroma4x4BlkIdx = 0
                nC = 0
                for i in range(0, 2):
                    for j in range(0, 2):
                        #different nC
                        logging.debug("decoding blockInx: %d, nC: %d", chroma4x4BlkIdx, nC)

                        abs_row = self.blk16x16Idx_y*2 + i
                        abs_col = self.blk16x16Idx_x*2 + j
                        logging.debug("row, col in nAnB_UV matrix: %d, %d", abs_row, abs_col)
                        nC = self.__get_nC_UV(m, abs_row, abs_col)
                        
                        self.__show_binary_fragment()
                        blocks = self.stream[self.stream.pos: self.stream.len]
                        Chroma4x4ACLevel, position, self.nAnB_UV[m][abs_row,abs_col] = cavlc.decode(blocks, nC, 15)

                        temp = self.stream.read(position)   # drop the decoded data
                        logging.debug("processed data: %s", temp.bin)
                        logging.debug("Chroma4x4ACLevel_%d:", chroma4x4BlkIdx)
                        logging.debug("\n%s" % (Chroma4x4ACLevel))

                        Chroma4x4ACLevel[0, 0] = ChromaDCLevel[m][i, j]
                        UV_plane_16x16[m][i*4:(i*4+4), j*4:(j*4+4)] = copy.deepcopy(Chroma4x4ACLevel)

                        chroma4x4BlkIdx = chroma4x4BlkIdx + 1
        else:
            # two 8x8 AC are zeros
            logging.debug("Two Chroma 8x8 AC are zeros")
            # replace DC element
            for m in range(0, 2):   # cb & cr
                for i in range(0, 2):
                    for j in range(0, 2):
                        UV_plane_16x16[m][i*4, j*4] = ChromaDCLevel[m][i, j]

        logging.debug("Reconstructed 8x8 U plane coefficients:")
        logging.debug("\n%s", UV_plane_16x16[0])

        logging.debug("Reconstructed 8x8 V plane coefficients:")
        logging.debug("\n%s", UV_plane_16x16[1])

    def __residual_block_Intra16x16(self):
        """
        residual_block( Intra16x16DCLevel, 16 )
        residual_block( Intra16x16ACLevel[ i8x8 * 4 + i4x4 ], 15 )
        on page 44 of H.264 standard
        """
        #logging.debug("nAnB:")
        #logging.debug("\n%s" % (self.nAnB[0:4, 0:4]))

        nC = self.__get_nC(self.blk16x16Idx_y*4, self.blk16x16Idx_x*4)
        logging.debug("  blk16x16Idx_x: %d, blk16x16Idx_y: %d, nC: %d", self.blk16x16Idx_x, self.blk16x16Idx_y, nC)
        
        blocks = self.stream[self.stream.pos: self.stream.len]
        Intra16x16DCLevel, position, temp = cavlc.decode(blocks, nC, 16)
        temp = self.stream.read(position)   # drop the decoded data
        logging.debug("processed data: %s", temp.bin)
        logging.debug("Intra16x16DCLevel: %s", Intra16x16DCLevel)
        
        # do DC level transform
        residual_lumDC = transform.inverseIntra16x16LumaDCScalingAndTransform(Intra16x16DCLevel, self.mb_current_qp)
        logging.debug("residual_lumDC: %s", residual_lumDC)

        coeffBlock_16x16 = np.zeros((16, 16), int)
        residual_16x16 = np.zeros((16, 16), int)

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
                            logging.debug("row, col in nAnB matrix: %d, %d", abs_row, abs_col)
                            
                            self.__show_binary_fragment()
                            blocks = self.stream[self.stream.pos: self.stream.len]
                            Intra4x4ACLevel, position, self.nAnB[abs_row,abs_col] = cavlc.decode(blocks, nC, 15)

                            temp = self.stream.read(position)   # drop the decoded data
                            logging.debug("processed data: %s", temp.bin)
                            logging.debug("Intra16x16ACLevel_%d:", luma4x4BlkIdx)
                            #logging.debug("\n%s" % (Intra4x4ACLevel))

                            coeffBlock_16x16[x*4:(x*4+4), y*4:(y*4+4)] = copy.deepcopy(Intra4x4ACLevel)

                            #do AC level transform
                            temp4x4ACLevel = copy.deepcopy(Intra4x4ACLevel.astype(int))
                            temp4x4ACLevel[0, 0] = residual_lumDC[x, y]
                            residualAC = transform.inverseReidual4x4ScalingAndTransform(temp4x4ACLevel, self.mb_current_qp)
                            residual_16x16[x*4:(x*4+4), y*4:(y*4+4)] = copy.deepcopy(residualAC)

                            luma4x4BlkIdx = luma4x4BlkIdx + 1

        for i in range(0, 4):
            for j in range(0, 4):
                coeffBlock_16x16[i*4, j*4] = Intra16x16DCLevel[i, j]

        return coeffBlock_16x16, residual_16x16

    def __residual_block_LumaLevel(self):
        """
        residual_block( LumaLevel[ i8x8 * 4 + i4x4 ], 16 )
        on page 44 of H.264 standard
        """
        #logging.debug("nAnB:")
        #logging.debug("\n%s" % (self.nAnB[0:4, 0:4]))

        nC = self.__get_nC(self.blk16x16Idx_y*4, self.blk16x16Idx_x*4)
        logging.debug("  blk16x16Idx_x: %d, blk16x16Idx_y: %d, nC: %d", self.blk16x16Idx_x, self.blk16x16Idx_y, nC)
        
        coeffBlock_16x16 = np.zeros((16, 16), int)
        residual_16x16 = np.zeros((16, 16), int)

        mc_sample = self.__get_P_prediction()

        luma4x4BlkIdx = 0
        for m in range(0, 2):
            for n in range(0, 2):
                for i in range(0, 2):
                    for j in range(0, 2):
                        #different nC
                        x = m*2+i
                        y = n*2+j
                        tempindex = m*2 + n
                        if (self.CodedBlockPatternLuma & (1<<tempindex)):


                            abs_row = self.blk16x16Idx_y*4 + x
                            abs_col = self.blk16x16Idx_x*4 + y
                            nC = self.__get_nC(abs_row, abs_col)
                            logging.debug("decoding blockInx: %d, nC: %d", luma4x4BlkIdx, nC)
                            logging.debug("row, col in nAnB matrix: %d, %d", abs_row, abs_col)
                            
                            self.__show_binary_fragment()
                            blocks = self.stream[self.stream.pos: self.stream.len]
                            Intra4x4ACLevel, position, self.nAnB[abs_row,abs_col] = cavlc.decode(blocks, nC, 16)

                            temp = self.stream.read(position)   # drop the decoded data
                            logging.debug("processed data: %s", temp.bin)
                            logging.debug("Inter16x16ACLevel_%d:", luma4x4BlkIdx)
                            #logging.debug("\n%s" % (Intra4x4ACLevel))

                            coeffBlock_16x16[x*4:(x*4+4), y*4:(y*4+4)] = copy.deepcopy(Intra4x4ACLevel)

                        else:
                            coeffBlock_16x16[x*4:(x*4+4), y*4:(y*4+4)] = 0

                        #do AC level transform
                        temp4x4ACLevel = copy.deepcopy(coeffBlock_16x16[x*4:(x*4+4), y*4:(y*4+4)].astype(int))

                        # according to page 140 formula 8-289
                        CP = mc_sample[x*4:(x*4+4), y*4:(y*4+4)]

                        residualAC = transform.inverse_P_Reidual4x4ScalingAndTransform(CP, temp4x4ACLevel, self.mb_current_qp)
                        residual_16x16[x*4:(x*4+4), y*4:(y*4+4)] = copy.deepcopy(residualAC+CP)

                        luma4x4BlkIdx = luma4x4BlkIdx + 1

        return coeffBlock_16x16, residual_16x16

    def __read_te(self):
        """
        read te data from stream
        """
        logging.debug("before read te(v) data: %s", self.stream.peek(32).bin)
        
        value = self.__get_codeNum()
        result = 0
        if value > 1:
            temp = self.stream.read('ue')
            result = temp
        elif value==1:
            result = 0
        else: # value==0
            result = 1   # temp code, should fix

        logging.debug("after read te(v) data: %s", self.stream.peek(32).bin)
        return result

    def __get_codeNum(self):
        """
        get codeNum from stream
        """
        logging.debug("before read codeNum data:")
        self.__show_binary_fragment()
        
        leadingZeroBits = -1
        b = 0
        while not b:
            leadingZeroBits = leadingZeroBits + 1
            b = self.stream.read('uint:1')

        follow = 0
        if leadingZeroBits>0:
            temp = self.stream.read('bits:'+str(leadingZeroBits))
            follow = temp.uint

        codeNum = pow(2, leadingZeroBits) - 1 + follow

        logging.debug("after read codeNum data:")
        self.__show_binary_fragment()
        logging.debug("codeNum: %d", codeNum)

        # get coded_block_pattern by codeNum
        return codeNum

    def __read_me(self):
        """
        read me data from stream
        """
        codeNum = self.__get_codeNum()

        pattern = 0
        #get from table 9-4
        if self.MbPartPredMode == 'Intra_4x4':
            pattern = vlc.coded_block_pattern[codeNum][0]
        else:
            pattern = vlc.coded_block_pattern[codeNum][1]

        # get coded_block_pattern by codeNum
        return pattern

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

    def __get_nC_UV(self, plane, row, col):
        """
        calculate nC of current 4x4 block
        Args:
            plane: U plane or V plane
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
            nA = self.nAnB_UV[plane][row, col-1]
            nB = 0
            nC = nA + nB
        elif col==0:
            nA = 0
            nB = self.nAnB_UV[plane][row-1, col]
            nC = nA + nB
        else:
            nA = self.nAnB_UV[plane][row, col-1]
            nB = self.nAnB_UV[plane][row-1, col]
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

    def __show_binary_fragment(self, length=64):
        """
        show folloing binary code of decoding stream
        """
        example_len = length if (self.stream.len-self.stream.pos)>length else (self.stream.len-self.stream.pos)
        logging.debug("following data: %s", self.stream.peek(example_len).bin)

    def __set_motion_vector(self, mvd):
        """
        calculate the motion vector accroding to mvd
        according to 8.4.1.3.1 on page 120 of H.264 standard
        """
        self.mvd[self.blk16x16Idx_y, self.blk16x16Idx_x] = mvd

        mvp = [0, 0]
        mvA = [0, 0]
        mvB = [0, 0]
        mvC = [0, 0]
        if self.blk16x16Idx_y==0 and self.blk16x16Idx_x==0:
            # A B C not available
            mvA = [0, 0]
            mvB = [0, 0]
            mvC = [0, 0]
        
        elif self.blk16x16Idx_x==0 and self.blk16x16Idx_y!=0:
            # A not availabl, B & C available
            mvA = [0, 0]
            mvB = self.mv[self.blk16x16Idx_y-1, self.blk16x16Idx_x]
            mvC = self.mv[self.blk16x16Idx_y-1, self.blk16x16Idx_x+1]

        elif self.blk16x16Idx_x!=0 and self.blk16x16Idx_y==0:
            # A available, B C not available
            mvA = self.mv[self.blk16x16Idx_y, self.blk16x16Idx_x-1]
            mvB = mvA
            mvC = mvA
        else:
            # A, B, C available
            mvA = self.mv[self.blk16x16Idx_y, self.blk16x16Idx_x-1]
            mvB = self.mv[self.blk16x16Idx_y-1, self.blk16x16Idx_x]
            x_C = self.blk16x16Idx_x+1
            if x_C >= self.mv.shape[1]:
                mvC = mvA
            else:
                mvC = self.mv[self.blk16x16Idx_y-1, x_C]
        
        mvp[0] = statistics.median([mvA[0], mvB[0], mvC[0]])
        mvp[1] = statistics.median([mvA[1], mvB[1], mvC[1]])

        self.mv[self.blk16x16Idx_y, self.blk16x16Idx_x][0] = mvd[0] + mvp[0]
        self.mv[self.blk16x16Idx_y, self.blk16x16Idx_x][1] = mvd[1] + mvp[1]

        logging.debug("mvp: %s", mvp)
        logging.debug("mv: %s", self.mv[self.blk16x16Idx_y, self.blk16x16Idx_x])

    def __get_P_prediction(self):
        """
        get P prediction according to MVP
        """
        # the process here is different from __residual_block_Intra16x16
        mc_sample = np.zeros((16, 16), int)
        ref_x = self.mv[self.blk16x16Idx_y, self.blk16x16Idx_x][0] + self.blk16x16Idx_x * 16 * 4
        ref_y = self.mv[self.blk16x16Idx_y, self.blk16x16Idx_x][1] + self.blk16x16Idx_y * 16 * 4
        ref_x = int(ref_x/4) #TODO: should use interpolation here
        ref_y = int(ref_y/4) #TODO: should use interpolation here

        # temp code
        if ref_x<0:
            ref_x = 1279 + ref_x
        if ref_y<0:
            ref_y = 719 + ref_y
        if ref_x+16>=1280:
            ref_x = 1280 - 16 -1
        if ref_y+16>=720:
            ref_y = 720 - 16 - 1
        mc_sample = copy.deepcopy(self.reference[ref_y:(ref_y+16), ref_x:(ref_x+16)])

        return mc_sample

    def __set_P_skip_macroblock(self):
        """
        set P skip macroblock to restore frame
        """
        mvd_l0 = [0, 0]
        self.__set_motion_vector(mvd_l0)   # P_skip macroblock has no MVP

        row = self.blk16x16Idx_y*16
        col = self.blk16x16Idx_x*16

        mc_sample = self.__get_P_prediction()
        
        self.coefficients[row:(row+16), col:(col+16)] = 0
        self.residual[row:(row+16), col:(col+16)] = copy.deepcopy(mc_sample)

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
    residual, modemap = nal_parser.parse(nal, sps_parser, pps_parser)
    np.save("residual.npy", residual)
    np.save("modemap.npy", modemap)

    plt.figure()
    plt.imshow(residual, cmap='gray')
    plt.title("residual image")

    plt.figure()
    plt.imshow(modemap, cmap='gray')
    plt.title("modemap image")

    plt.show()

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("NaluParser.log", mode='w'),
            logging.StreamHandler(),
        ]
    )
    logging.getLogger('matplotlib.font_manager').disabled = True

    logging.debug("Unit test for NaluParser")

    main("../test/lena_x264_baseline_I_16x16.264")