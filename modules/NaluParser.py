import logging
from bitstring import BitStream, BitArray

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

if __name__ == '__main__':
    # Test case for NaluStreamer
    logging.debug("Unit test for NaluParser")