from bitstring import BitStream
from h26x_extractor import nalutypes


class NaluStreamer():

    def __init__(self):
        START_CODE_PREFIX = '0x00000001'
        START_CODE_PREFIX_SHORT = "0x000001"
        self.stream = BitStream(START_CODE_PREFIX)

    def export(self, bitstream_outputfile):
        """
        output the binary data into file
        """
        f = open(bitstream_outputfile, 'wb')
        self.stream.tofile(f)

class SPSStreamer():
    """
    Sequence Parameter Set class
    """

    def __init__(self):

        # initializers
        self.offset_for_ref_frame = []
        # self.seq_scaling_list_present_flag = []

        # self.profile_idc = self.s.read('uint:8')
        # self.constraint_set0_flag = self.s.read('uint:1')
        # self.constraint_set1_flag = self.s.read('uint:1')
        # self.constraint_set2_flag = self.s.read('uint:1')
        # self.constraint_set3_flag = self.s.read('uint:1')
        # self.constraint_set4_flag = self.s.read('uint:1')
        # self.constraint_set5_flag = self.s.read('uint:1')
        # self.reserved_zero_2bits = self.s.read('uint:2')
        # self.level_idc = self.s.read('uint:8')
        # self.seq_parameter_set_id = self.s.read('ue')

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

        # self.log2_max_frame_num_minus4 = self.s.read('ue')
        # self.pic_order_cnt_type = self.s.read('ue')

        # if self.pic_order_cnt_type == 0:
        #     self.log2_max_pic_order_cnt_lsb_minus4 = self.s.read('ue')
        # elif self.pic_order_cnt_type == 1:
        #     self.delta_pic_order_always_zero_flag = self.s.read('uint:1')
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

def main():
    f = "E:/temp/output/nalustreamer.264"
    ex = NaluStreamer()
    ex.export(f)

if __name__ == '__main__':
    main()