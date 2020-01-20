# Based on the document of ITU-T Recommendation H.264 05/2003 edition
# 

from bitstring import BitStream, BitArray
from h26x_extractor import nalutypes

START_CODE_PREFIX = '0x00000001'
START_CODE_PREFIX_SHORT = "0x000001"

class NaluStreamer():

    def __init__(self, nalu_type):
        '''
        init the value of nalu unit
        : param nalu_type: something like NAL_UNIT_TYPE_CODED_SLICE_IDR in nalutypes.py
        '''
        self.forbidden_zero_bit = '0b0'
        self.nal_ref_idc = '0b11'
        self.nal_unit_type = "0b" + "{0:05b}".format(nalu_type)

        self.stream = BitStream(START_CODE_PREFIX)

    def export(self, bitstream_outputfile):
        """
        output the binary data into file
        """
        self.stream.append(self.forbidden_zero_bit)
        self.stream.append(self.nal_ref_idc)
        self.stream.append(self.nal_unit_type)

        #output to the file
        f = open(bitstream_outputfile, 'wb')
        self.stream.tofile(f)
        f.close()

class SPSStreamer(NaluStreamer):
    """
    Sequence Parameter Set class
    Based on 7.3.2.1 setion on page 31 & 7.4.2.1 setion on page 53
    """

    def __init__(self, nalu_type):
        super().__init__(nalu_type)

        # initializers
        #self.offset_for_ref_frame = []
        #self.seq_scaling_list_present_flag = []

        # use some default value
        self.profile_idc = '0x64'   # u(8)
        self.constraint_set0_flag = '0b0' # u(1)
        self.constraint_set1_flag = '0b0' # u(1)
        self.constraint_set2_flag = '0b0' # u(1)

        self.reserved_zero_2bits = '0b00000' # u(5)
        self.level_idc = '0b00001' # u(5)
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

        self.log2_max_frame_num_minus4 = '0b1' #ue(v)
        self.pic_order_cnt_type = '0b1' #ue(v)

        # if self.pic_order_cnt_type == 0:
        #     self.log2_max_pic_order_cnt_lsb_minus4 = '0b1' #ue(1), TODO
        # elif self.pic_order_cnt_type == 1:
        #     self.delta_pic_order_always_zero_flag = '0b1' # u(1)
        #     self.offset_for_non_ref_pic = self.s.read('se')
        #     self.offset_for_top_to_bottom_filed = self.s.read('se')
        #     self.num_ref_frames_in_pic_order_cnt_cycle = self.s.read('ue')
        #     for i in range(self.num_ref_frames_in_pic_order_cnt_cycle):
        #         self.offset_for_ref_frame.append(self.s.read('se'))

        # self.num_ref_frames = self.s.read('ue')
        # self.gaps_in_frame_num_value_allowed_flag = self.s.read('uint:1')
        # self.pic_width_in_mbs_minus_1 = self.s.read('ue')
        # self.pic_height_in_map_units_minus_1 = self.s.read('ue')
        # self.frame_mbs_only_flag = self.s.read('uint:1')
        # if not self.frame_mbs_only_flag:
        #     self.mb_adapative_frame_field_flag = self.s.read('uint:1')
        # self.direct_8x8_inference_flag = self.s.read('uint:1')
        # self.frame_cropping_flag = self.s.read('uint:1')
        # if self.frame_cropping_flag:
        #     self.frame_crop_left_offst = self.s.read('ue')
        #     self.frame_crop_right_offset = self.s.read('ue')
        #     self.frame_crop_top_offset = self.s.read('ue')
        #     self.frame_crop_bottom_offset = self.s.read('ue')
        # self.vui_parameters_present_flag = self.s.read('uint:1')

        # # TODO: parse VUI
        # #self.rbsp_stop_one_bit         = self.s.read('uint:1')

        # self.print_verbose()

    def set_level_idc(self, level_number):
        '''
        set level_idc in SPS, foramt: u(8)
        : param set_id: int number of set id, according to Table A-1 Level limits on page 207
        '''
        self.level_idc = "0b" + "{0:08b}".format(level_number*10)
        print(self.level_idc)

    def set_seq_parameter_set_id(self, set_id):
        '''
        set seq_parameter_set_id in SPS, foramt: ue(v)
        : param set_id: int number of set id
        '''
        s = BitArray(ue=set_id)
        self.seq_parameter_set_id = s
        print(self.seq_parameter_set_id)

    def set_log2_max_frame_num_minus4(self, value):
        '''
        set log2_max_frame_num_minus4 in SPS, foramt: ue(v)
        : param value: described on page 54
        '''
        s = BitArray(ue=value)
        self.log2_max_frame_num_minus4 = s
        print(self.log2_max_frame_num_minus4)

    def export(self, bitstream_outputfile):
        """
        output the binary data into file
        """
        self.stream.append(self.profile_idc)
        self.stream.append(self.constraint_set0_flag)
        self.stream.append(self.constraint_set1_flag)
        self.stream.append(self.constraint_set2_flag)
        self.stream.append(self.reserved_zero_2bits)
        self.stream.append(self.level_idc)
        self.stream.append(self.seq_parameter_set_id)

        super().export(bitstream_outputfile)

def main():
    f = "E:/temp/output/nalustreamer.264"
    ex = SPSStreamer(nalutypes.NAL_UNIT_TYPE_SPS)
    ex.profile_idc = '0x42'
    ex.set_level_idc(3) # level 3
    ex.set_seq_parameter_set_id(0)
    ex.set_log2_max_frame_num_minus4(0)
    ex.export(f)

if __name__ == '__main__':
    main()