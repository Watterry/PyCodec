
from enum import Enum, unique
import numpy as np

@unique
class slice_type(Enum):
    p = 0
    B = 1
    I = 2
    SP = 3
    SI = 4
    p5 = 5
    B6 = 6
    I7 = 7
    SP8 = 8
    SI9 = 9

#table 7-8 on page 71 of [H.264 standard Book]
# row: [mb_type]
# column: [name of mb_type] [MbPartPredMode] [Intra16x16PredMode] [CodedBlockPatternChroma] [CodedBlockPatternLuma]
# value -1 means 'na'
I_slice_Macroblock_types = np.array([
        # mb_type = 0
        ['I_4x4', 'Intra_4x4', -1, -1, -1],
        # mb_type = 1
        ['I_16x16_0_0_0', 'Intra_16x16', 0, 0, 0],
        # mb_type = 2
        ['I_16x16_1_0_0', 'Intra_16x16', 1, 0, 0],
        # mb_type = 3
        ['I_16x16_2_0_0', 'Intra_16x16', 2, 0, 0],
        # mb_type = 4
        ['I_16x16_3_0_0', 'Intra_16x16', 3, 0, 0],
        # mb_type = 5
        ['I_16x16_0_1_0', 'Intra_16x16', 0, 1, 0],
        # mb_type = 6
        ['I_16x16_1_1_0', 'Intra_16x16', 1, 1, 0],
        # mb_type = 7
        ['I_16x16_2_1_0', 'Intra_16x16', 2, 1, 0],
        # mb_type = 8
        ['I_16x16_3_1_0', 'Intra_16x16', 3, 1, 0],
        # mb_type = 9
        ['I_16x16_0_2_0', 'Intra_16x16', 0, 2, 0],
        # mb_type = 10
        ['I_16x16_1_2_0', 'Intra_16x16', 1, 2, 0],
        # mb_type = 11
        ['I_16x16_2_2_0', 'Intra_16x16', 2, 2, 0],
        # mb_type = 12
        ['I_16x16_3_2_0', 'Intra_16x16', 3, 2, 0],
        # mb_type = 13
        ['I_16x16_0_0_1', 'Intra_16x16', 0, 0, 15],
        # mb_type = 14
        ['I_16x16_1_0_1', 'Intra_16x16', 1, 0, 15],
        # mb_type = 15
        ['I_16x16_2_0_1', 'Intra_16x16', 2, 0, 15],
        # mb_type = 16
        ['I_16x16_3_0_1', 'Intra_16x16', 3, 0, 15],
        # mb_type = 17
        ['I_16x16_0_1_1', 'Intra_16x16', 0, 1, 15],
        # mb_type = 18
        ['I_16x16_1_1_1', 'Intra_16x16', 1, 1, 15],
        # mb_type = 19
        ['I_16x16_2_1_1', 'Intra_16x16', 2, 1, 15],
        # mb_type = 20
        ['I_16x16_3_1_1', 'Intra_16x16', 3, 1, 15],
        # mb_type = 21
        ['I_16x16_0_2_1', 'Intra_16x16', 0, 2, 15],
        # mb_type = 22
        ['I_16x16_1_2_1', 'Intra_16x16', 1, 2, 15],
        # mb_type = 23
        ['I_16x16_2_2_1', 'Intra_16x16', 2, 2, 15],
        # mb_type = 24
        ['I_16x16_3_2_1', 'Intra_16x16', 3, 2, 15],
        # mb_type = 25
        ['I_PCM', -1, -1, -1, -1],
        ])

#table 8-3 on page 106 of [H.264 standard Book]
Intra16x16PredMode_names = np.array(['Intra_16x16_Vertical',    # Intra16x16PredMode=0
                                     'Intra_16x16_Horizontal',  # Intra16x16PredMode=1
                                     'Intra_16x16_DC',          # Intra16x16PredMode=2
                                     'Intra_16x16_Plane'        # Intra16x16PredMode=3
                                    ])

def get_I_slice_Intra16x16PredMode(mb_type):
    """
    Get I slice Macroblock CodedBlockPatternChroma info
    Args:
        mb_type: I slice Macroblock type
    Returns:
        int value of CodedBlockPatternChroma
    """
    predType = int(I_slice_Macroblock_types[mb_type][2])

    return predType, Intra16x16PredMode_names[predType]

def get_I_slice_CodedBlockPatternChroma(mb_type):
    """
    Get I slice Macroblock CodedBlockPatternChroma info
    Args:
        mb_type: I slice Macroblock type
    Returns:
        int value of CodedBlockPatternChroma
    """
    return int(I_slice_Macroblock_types[mb_type][3])

def get_I_slice_CodedBlockPatternLuma(mb_type):
    """
    Get I slice Macroblock CodedBlockPatternLuma info
    Args:
        mb_type: I slice Macroblock type
    Returns:
        int value of CodedBlockPatternLuma
    """
    return int(I_slice_Macroblock_types[mb_type][4])


#table 7-10 on page 73 of [H.264 standard Book]
# row: [mb_type]
# column: [name of mb_type] [NumMbPart] [MbPartPredMode] [MbPartPredMode] [MbPartWidth] [MbPartHeight]
# value -1 means 'na'
P_slice_Macroblock_types = np.array([
        # mb_type = 0
        ['P_L0_16x16', 1, 'Pred_L0', -1, 16, 16],
        # mb_type = 1
        ['P_L0_L0_16x8', 2, 'Pred_L0', 'Pred_L0', 16, 8],
        # mb_type = 2
        ['P_L0_L0_8x16', 2, 'Pred_L0', 'Pred_L0', 8, 8],
        # mb_type = 3
        ['P_8x8', 4, -1, -1, 8, 8],
        # mb_type = 4
        ['P_8x8ref0', 4, -1, -1, 8, 8],
        # mb_type = 5
        ['P_Skip', 1, 'Pred_L0', -1, 16, 16],
        ])