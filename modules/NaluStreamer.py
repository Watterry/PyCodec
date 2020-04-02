# Based on the document of ITU-T Recommendation H.264 05/2003 edition
# 

from bitstring import BitStream, BitArray
from h26x_extractor import nalutypes
import matplotlib.pyplot as plt

START_CODE_PREFIX = '0x00000001'
START_CODE_PREFIX_SHORT = "0x000001"

def openNaluFile(bitstream_outputfile):
    '''
    Init Nalu File, which means clean all the old data in the file
    '''
    return open(bitstream_outputfile, 'wb')

def closeNaluFile(bitstream_outputfile_handler):
    bitstream_outputfile_handler.close()

class NaluStreamer():

    def __init__(self, nalu_type):
        '''
        init the value of nalu unit
        : param nalu_type: something like NAL_UNIT_TYPE_CODED_SLICE_IDR in nalutypes.py
        '''
        if (nalu_type != nalutypes.NAL_UNIT_TYPE_UNSPECIFIED):
            # for specific nalutypes
            self.forbidden_zero_bit = '0b0'
            self.nal_ref_idc = '0b11'
            self.nal_unit_type = "0b" + "{0:05b}".format(nalu_type)

            self.stream = BitStream(START_CODE_PREFIX)
            self.stream.append(self.forbidden_zero_bit)
            self.stream.append(self.nal_ref_idc)
            self.stream.append(self.nal_unit_type)
        else:
            # for slice_data
            self.stream = BitStream()

    def rbsp_trailing_bits(self):
        '''
        according to RBSP trainling bits syntax on page 35, and according to explanation page 49
        '''
        rbsp_stop_one_bit = '0b1'
        rbsp_alignment_zero_bit = '0b0'
        self.stream.append(rbsp_stop_one_bit)

        plus = 8 - (self.stream.length % 8)

        for x in range(0, plus):
            self.stream.append(rbsp_alignment_zero_bit)

        #print("length after plus:")
        #print(self.stream.length)

    def export(self, bitstream_output_handler):
        """
        output the binary data into file
        """
        self.stream.tofile(bitstream_output_handler)

class SpsStreamer(NaluStreamer):
    """
    Sequence Parameter Set class
    Based on 7.3.2.1 setion on page 31 & 7.4.2.1 setion on page 53
    The sequence of set__ function is not important.
    the function export() will take care of the sequence of the SODB.
    """

    def __init__(self, nalu_type):
        super().__init__(nalu_type)

        # use some default value
        self.profile_idc = '0x64'   # u(8)
        self.constraint_set0_flag = '0b0' # u(1)
        self.constraint_set1_flag = '0b0' # u(1)
        self.constraint_set2_flag = '0b0' # u(1)

        self.reserved_zero_2bits = '0b00000' # u(5)
        self.level_idc = '0b00000001' # u(8)
        self.seq_parameter_set_id = '0b0' #ue(v)

        # if ((self.profile_idc == 100) or (self.profile_idc == 110) or (self.profile_idc == 122) or (self.profile_idc == 144)):
        #     self.chroma_format_idc = self.s.read('ue')
        #     if self.chroma_format_idc == 3:
        #         self.residual_colour_transform_flag = self.s.read('uint:1')

        #     self.bit_depth_luma_minus8 = self.s.read('ue')
        #     self.bit_depth_chroma_minus8 = self.s.read('ue')
        #     self.qpprime_y_zero_transform_bypass_flag = self.s.read('uint:1')
        #     self.seq_scaling_matrix_present_flag = self.s.read('uint:1')

        #     if self.seq_scaling_matrix_present_flag:
        #         # TODO: have to implement this, otherwise it will fail
        #         raise NotImplementedError("Scaling matrix decoding is not implemented.")

        self.log2_max_frame_num_minus4 = '0b0' #ue(v)
        self.pic_order_cnt_type = '0b1' #ue(v)

        self.num_ref_frames = '0b1' #ue(v)
        self.gaps_in_frame_num_value_allowed_flag = '0b0' #u(1)
        self.pic_width_in_mbs_minus_1 = '0b0' #u(ue)
        self.pic_height_in_map_units_minus_1 = '0b0' #u(ue)
        self.frame_mbs_only_flag = '0b1' #u(1)
        # if not self.frame_mbs_only_flag:
        #     self.mb_adapative_frame_field_flag = self.s.read('uint:1')
        self.direct_8x8_inference_flag = '0b0' #u(1)
        self.frame_cropping_flag = '0b0' #u(1)
        # if self.frame_cropping_flag:
        #     self.frame_crop_left_offst = self.s.read('ue')
        #     self.frame_crop_right_offset = self.s.read('ue')
        #     self.frame_crop_top_offset = self.s.read('ue')
        #     self.frame_crop_bottom_offset = self.s.read('ue')
        self.vui_parameters_present_flag = '0b0' #u(1)

    def set__profile_idc(self, profile_idc):
        '''
        set level_idc in SPS, foramt: u(8)
        : param set_id: int number of set id, according to Table A-1 Level limits on page 207
        '''
        self.profile_idc = "0b" + "{0:08b}".format(profile_idc)

    def set__level_idc(self, level_number):
        '''
        set level_idc in SPS, foramt: u(8)
        : param set_id: int number of set id, according to Table A-1 Level limits on page 207
        '''
        self.level_idc = "0b" + "{0:08b}".format(level_number*10)

    def set__seq_parameter_set_id(self, set_id):
        '''
        set seq_parameter_set_id in SPS, foramt: ue(v)
        : param set_id: int number of set id
        '''
        s = BitArray(ue=set_id)
        self.seq_parameter_set_id = s

    def set__log2_max_frame_num_minus4(self, value):
        '''
        set log2_max_frame_num_minus4 in SPS, foramt: ue(v)
        : param value: described on page 54
        '''
        s = BitArray(ue=value)
        self.log2_max_frame_num_minus4 = s

    def get__log2_max_frame_num_minus4(self):
        """
        Get and decode log2_max_frame_num_minus4 from sps
        """
        temp = self.log2_max_frame_num_minus4.ue
        return temp

    def set__pic_order_cnt_type(self, value):
        '''
        set pic_order_cnt_type in SPS, foramt: ue(v)
        : param value: described on page 54
        '''
        s = BitArray(ue=value)
        self.pic_order_cnt_type = s

        if (value == 0):
            # log2_max_pic_order_cnt_lsb_minus4
            log2_max_pic_order_cnt_lsb_minus4 = 0   # todo, need to add specific data
            temp = BitArray(ue=log2_max_pic_order_cnt_lsb_minus4)
            self.pic_order_cnt_type.append(temp)
        elif (value == 1):
            print("TODO: ADD MORE SPECIFIC ITEM")
        #     self.delta_pic_order_always_zero_flag = '0b1' # u(1)
        #     self.offset_for_non_ref_pic = self.s.read('se')
        #     self.offset_for_top_to_bottom_filed = self.s.read('se')
        #     self.num_ref_frames_in_pic_order_cnt_cycle = self.s.read('ue')
        #     for i in range(self.num_ref_frames_in_pic_order_cnt_cycle):
        #         self.offset_for_ref_frame.append(self.s.read('se'))

    def set__num_ref_frames(self, value):
        '''
        set num_ref_frames in SPS, foramt: ue(v)
        : param value: described on page 55
        '''
        s = BitArray(ue=value)
        self.num_ref_frames = s

    def set__gaps_in_frame_num_value_allowed_flag(self, bool_value):
        '''
        set gaps_in_frame_num_value_allowed_flag in SPS, foramt: u(1)
        : param value: described on page 55
        '''
        if (bool_value):
            self.gaps_in_frame_num_value_allowed_flag = '0b1'
        else:
            self.gaps_in_frame_num_value_allowed_flag = '0b0'

    def set__pic_width_in_mbs_minus_1(self, width):
        '''
        set pic_width_in_mbs_minus_1 in SPS, foramt: ue(v)
        : param width: video width, according to page 55 formula 7-3, 7-4, 7-5
        '''
        MB_width = 16
        pic_width_in_mbs_minus_1 = int( width/MB_width - 1 )
        s = BitArray(ue=pic_width_in_mbs_minus_1)
        self.pic_width_in_mbs_minus_1 = s

    def set__pic_height_in_map_units_minus1(self, height):
        '''
        set pic_height_in_map_units_minus1 in SPS, foramt: ue(v)
        : param width: video height, according to page 55 formula 7-6, 7-7
        '''
        MB_height = 16
        pic_height_in_map_units_minus_1 = int( height/MB_height - 1 )
        s = BitArray(ue=pic_height_in_map_units_minus_1)
        self.pic_height_in_map_units_minus_1 = s

    def set__frame_mbs_only_flag(self, bool_value):
        '''
        set frame_mbs_only_flag in SPS, foramt: ue(1)
        : param bool_value: have or not have field slices or field MBs, according to page 55
        '''
        if (bool_value):
            self.frame_mbs_only_flag = '0b1'
        else:
            self.frame_mbs_only_flag = '0b0'
            # todo: add mb_adaptive_frame_field_flag
            #mb_adaptive_frame_field_flag = '0b0' #u(1) TODO
            # self.frame_mbs_only_flag.append(mb_adaptive_frame_field_flag) #TODO

    def set__direct_8x8_inference_flag(self, bool_value):
        '''
        set direct_8x8_inference_flag in SPS, foramt: ue(v)
        : param bool_value: Specifies how certain B macroblock motion vectors are derived on page 55
        '''
        if (bool_value):
            self.direct_8x8_inference_flag = '0b1'
        else:
            self.direct_8x8_inference_flag = '0b0'

    def set__frame_cropping_flag(self, bool_value):
        '''
        set frame_cropping_flag in SPS, foramt: ue(v)
        : param bool_value: Specifies how certain B macroblock motion vectors are derived on page 55
        '''
        if (bool_value):
            self.frame_cropping_flag = '0b1'
            # TODO add more flags
            # frame_crop_left_offset
            # frame_crop_left_offset
            # frame_crop_left_offset
            # frame_crop_bottom_offset
        else:
            self.frame_cropping_flag = '0b0'

    def set__vui_parameters_present_flag(self, bool_value):
        '''
        set vui_parameters_present_flag in SPS, foramt: ue(v)
        : param bool_value: Specifies how certain B macroblock motion vectors are derived on page 55
        '''
        if (bool_value):
            self.vui_parameters_present_flag = '0b1'
            # TODO add more flags
            # vui_parameters_present_flag
        else:
            self.vui_parameters_present_flag = '0b0'

    def export(self, bitstream_output_handler):
        """
        output the binary data into file
        The sequence here is very important, should be exact the same as SPECIFIC of H.264
        """
        self.stream.append(self.profile_idc)
        self.stream.append(self.constraint_set0_flag)
        self.stream.append(self.constraint_set1_flag)
        self.stream.append(self.constraint_set2_flag)
        self.stream.append(self.reserved_zero_2bits)
        self.stream.append(self.level_idc)
        self.stream.append(self.seq_parameter_set_id)
        self.stream.append(self.log2_max_frame_num_minus4)
        self.stream.append(self.pic_order_cnt_type)
        self.stream.append(self.num_ref_frames)
        self.stream.append(self.gaps_in_frame_num_value_allowed_flag)
        self.stream.append(self.pic_width_in_mbs_minus_1)
        self.stream.append(self.pic_height_in_map_units_minus_1)
        self.stream.append(self.frame_mbs_only_flag)
        self.stream.append(self.direct_8x8_inference_flag)
        self.stream.append(self.frame_cropping_flag)
        self.stream.append(self.vui_parameters_present_flag)
        super().rbsp_trailing_bits()

        super().export(bitstream_output_handler)

class PpsStreamer(NaluStreamer):
    """
    Picture Parameter Set class
    Based on 7.3.2.1 setion on page 31 & 7.4.2.2 setion on page 56
    The sequence of set__ function is not important.
    the function export() will take care of the sequence of the SODB.
    """
    def __init__(self, nalu_type):
        super().__init__(nalu_type)

        # use some default value
        s = BitArray(ue=0)
        self.pic_parameter_set_id = s   # ue(v)
        self.seq_parameter_set_id = s # ue(v)
        self.entropy_coding_mode_flag = '0b0' # u(1)
        self.pic_order_present_flag = '0b0' # u(1)

        self.num_slice_groups_minus1 = s #ue(v)
        # TODO: subclause of num_slice_groups_minus1
        # if (num_slice_groups_minus1>0)

        s = BitArray(ue=9)
        self.num_ref_idx_l0_active_minus1 = s # ue(v)
        self.num_ref_idx_l1_active_minus1 = s # ue(v)

        self.weighted_pred_flag = '0b0' # u(1)
        self.weighted_bipred_idc = '0b00' # u(2)

        s = BitArray(se=0)
        self.pic_init_qp_minus26 = s   # se(v)
        self.pic_init_qs_minus26 = s   # se(v)
        self.chroma_qp_index_offset = s   # se(v)

        self.deblocking_filter_control_present_flag = '0b0' # u(1)
        self.constrained_intra_pred_flag = '0b0' # u(1)
        self.redundant_pic_cnt_present_flag = '0b0' # u(1)

    def set__pic_init_qp_minus26(self, qp_minus26):
        s = BitArray(se=qp_minus26)
        self.pic_init_qp_minus26 = s   # se(v)

    def get__pic_init_qp_minus26(self):
        temp = self.pic_init_qp_minus26.se
        return temp

    def set__deblocking_filter_control_present_flag(self, bool_value):
        if bool_value:
            self.deblocking_filter_control_present_flag = '0b1'
        else:
            self.deblocking_filter_control_present_flag = '0b0'


    def export(self, bitstream_output_handler):
        """
        output the binary data into file
        The sequence here is very important, should be exact the same as SPECIFIC of H.264
        """
        self.stream.append(self.pic_parameter_set_id)
        self.stream.append(self.seq_parameter_set_id)
        self.stream.append(self.entropy_coding_mode_flag)
        self.stream.append(self.pic_order_present_flag)
        self.stream.append(self.num_slice_groups_minus1)
        self.stream.append(self.num_ref_idx_l0_active_minus1)
        self.stream.append(self.num_ref_idx_l1_active_minus1)
        self.stream.append(self.weighted_pred_flag)
        self.stream.append(self.weighted_bipred_idc)
        self.stream.append(self.pic_init_qp_minus26)
        self.stream.append(self.pic_init_qs_minus26)
        self.stream.append(self.chroma_qp_index_offset)
        self.stream.append(self.deblocking_filter_control_present_flag)
        self.stream.append(self.constrained_intra_pred_flag)
        self.stream.append(self.redundant_pic_cnt_present_flag)

        super().rbsp_trailing_bits()

        super().export(bitstream_output_handler)

class SliceHeader(NaluStreamer):
    """
    slice_header syntax class
    Based on 7.3.3 section on page 36 & 7.4.3 section on page 60
    @notice currently just support ONE SLICE frame
    The sequence of set__ function is not important.
    the function export() will take care of the sequence of the SODB.
    """
    def __init__(self, nalu_type, slice_type):
        super().__init__(nalu_type)

        # use some default value
        s = BitArray(ue=0)
        self.first_mb_in_slice = s   # ue(v)

        s = BitArray(ue=slice_type)
        self.slice_type = s # ue(v)

        s = BitArray(ue=0)
        self.pic_parameter_set_id = s # ue(v)

        self.frame_num = '0b0' # u(v)
        self.idr_pic_id = s # ue(v)

        self.pic_order_cnt_lsb = '0b0' # u(1)
        self.no_output_of_prior_pics_flag = '0b0' # u(1)
        self.long_term_reference_flag = '0b0' # u(1)

        s = BitArray(se=-3)
        self.slice_qp_delta = s  #se(v)

        s = BitArray(ue=0)
        self.disable_deblocking_filter_idc = s #ue(v)
        
        s = BitArray(se=0)
        self.slice_alpha_c0_offset_div2 = s
        self.slice_beta_offset_div2 = s
    
    def set__frame_num(self, sps_log2_minus4, frameNum):
        """
        set frame_num field in slice header
        the length of bits should be log2_max_frame_num_minus4+4 bits
        Args:
            sps_log2_minus4: the value of sps log2_max_frame_num_minus4
            frameNum: the frame num of current slice
        """
        bit_length = sps_log2_minus4 + 4
        
        temp = bin(frameNum).replace('0b','')
        while len(temp) < bit_length:
            temp = '0' + temp
        self.frame_num = '0b' + temp

    def set__slice_qp_delta(self, qp_delta):
        """
        set slice_qp_delta field in slice header
        Args:
            qp_delta: the int value of field slice_qp_delta
        """
        s = BitArray(se=qp_delta)
        self.slice_qp_delta = s  #se(v) 

    def export(self, bitstream_output_handler, PPS):
        """
        output the binary data into file
        The sequence here is very important, should be exact the same as SPECIFIC of H.264
        Args:
            bitstream_output_handler: output binary file handler
            PPS: the sequence PPS set
        """
        self.stream.append(self.first_mb_in_slice)
        self.stream.append(self.slice_type)
        self.stream.append(self.pic_parameter_set_id)
        self.stream.append(self.frame_num)

        #TODO: add frame_mbs_only_flag judgement

        #if (self.nalu_type==nalutypes.NAL_UNIT_TYPE_CODED_SLICE_IDR):
        self.stream.append(self.idr_pic_id)

        #self.stream.append(self.pic_order_cnt_lsb)   # TODO: should adjust this value according to SPS
        self.stream.append(self.no_output_of_prior_pics_flag)
        self.stream.append(self.long_term_reference_flag)
        self.stream.append(self.slice_qp_delta)

        # should be some judgement here
        if (PPS.deblocking_filter_control_present_flag):
            self.stream.append(self.disable_deblocking_filter_idc)
            if self.disable_deblocking_filter_idc != 1 :
                self.stream.append(self.slice_alpha_c0_offset_div2)
                self.stream.append(self.slice_beta_offset_div2)

        super().export(bitstream_output_handler)

class SliceData(NaluStreamer):
    """
    slice_data syntax class
    Based on 7.3.4 section on page 40 & 7.4.4 section on page 69
    @notice currently just support ONE SLICE frame
    The sequence of set__ function is not important.
    the function export() will take care of the sequence of the SODB.
    """
    def __init__(self):
        super().__init__(nalutypes.NAL_UNIT_TYPE_UNSPECIFIED)

        # use some default value
        # TODO: add cabac_aligned_one_bit part

        #s = BitArray(ue=0)
        #self.first_mb_in_slice = s   # ue(v)

    def set__macroblock_layer(self, macroblock_layer):
        self.macroblock_layer = macroblock_layer

    def export(self, bitstream_output_handler):
        """
        output the binary data into file
        The sequence here is very important, should be exact the same as SPECIFIC of H.264
        """
        self.stream.append(self.macroblock_layer)

        super().rbsp_trailing_bits()

        super().export(bitstream_output_handler)

class MacroblockLayer():
    """
    macroblock_layer syntax class
    Based on 7.3.5 section on page 41 & 7.4.5 section on page 70
    @notice currently just support ONE SLICE frame
    The sequence of set__ function is not important.
    the function export() will take care of the sequence of the SODB.
    : param mb_type: macroblock type
    """
    def __init__(self, mb_type):
        # use some default value
        s = BitArray(ue=mb_type)
        self.mb_type = s   # ue(v)
   
        self.mb_pred = ''

        s = BitArray(se=0)
        self.mb_qp_delta = s   # se(v)

        self.residual = ''

    def set__mb_pred(self, intra_chroma_pred_mode):
        #TODO: should use a independent function to generate mb_pred
        s = BitArray(ue=intra_chroma_pred_mode)
        self.mb_pred = s

    def set__residual(self, residual):
        self.residual = residual

    def gen(self):
        """
        generate the binary data of this macroblock
        The sequence here is very important, should be exact the same as SPECIFIC of H.264
        """
        stream = BitStream()

        stream.append(self.mb_type)
        #current we just handle 16x16 mode
        stream.append(self.mb_pred)
        stream.append(self.mb_qp_delta)
        stream.append(self.residual)

        return stream

def main():
    """
    basic unit test code
    """
    # step1, open the file
    f = "E:/temp/output/nalustreamer.264"
    handler = openNaluFile(f)

    # step2, generate sps & pps
    sps = SpsStreamer(nalutypes.NAL_UNIT_TYPE_SPS)
    sps.set__profile_idc(66) # Baseline profile
    sps.set__level_idc(3) # level 3
    sps.set__seq_parameter_set_id(0)
    sps.set__log2_max_frame_num_minus4(0)
    sps.set__pic_order_cnt_type(0)
    sps.set__num_ref_frames(2)
    sps.set__gaps_in_frame_num_value_allowed_flag(False)
    sps.set__pic_width_in_mbs_minus_1(512)
    sps.set__pic_height_in_map_units_minus1(512)
    sps.set__frame_mbs_only_flag(True)
    sps.set__direct_8x8_inference_flag(True)
    sps.set__frame_cropping_flag(False)
    sps.set__vui_parameters_present_flag(False)
    sps.export(handler)

    pps = PpsStreamer(nalutypes.NAL_UNIT_TYPE_PPS)
    pps.export(handler)

    # step3, write a key frame
    frame = SliceHeader(nalutypes.NAL_UNIT_TYPE_CODED_SLICE_IDR, 7)  # TODO: slice type shoud be defined
    temp = sps.get__log2_max_frame_num_minus4()
    frame.set__frame_num(temp, 0)
    
    frame.export(handler, pps)

    # step4, write slice & macroblock data
    I_16x16_2_0_1 = 15   #temp code, TODO: should add some basic prediction type in nalutypes
    mb = MacroblockLayer(I_16x16_2_0_1)
    mb.gen()

    # step5, close the file
    closeNaluFile(handler)

    #t = BitArray('0x88')

if __name__ == '__main__':
    # Test case for NaluStreamer
    main()