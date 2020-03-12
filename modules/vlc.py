# data set tables for CAVLC
# Based on the document of ITU-T Recommendation H.264 05/2003 edition

import numpy as np

# 4x16x4 matrix of table of coeff_taken
# [nC][TotalCoeff][TrailingOnes]
# nC varies from 0 ~ 3 according to Table 9-5 on page 159
# table0: 0 <= nC < 2
# table0: 2 <= nC < 4
# table0: 4 <= nC < 8
# table0: 8 <= nC
# Notice: '0b' is the prefix for NaluStreamer.py
coeff_token = np.array([
                        #talbe0
                        [['0b1'], # row = 0
                         ['0b000101', '0b01'],
                         ['0b00000111', '0b000100', '0b001'],
                         ['0b000000111', '0b00000110', '0b0000101', '0b00011'],
                         # row = 4
                         ['0b0000000111', '0b000000110', '0b00000101', '0b000011'],
                         ['0b00000000111', '0b0000000110', '0b000000101', '0b0000100'],
                         ['0b0000000001111', '0b00000000110', '0b0000000101', '0b00000100'],
                         ['0b0000000001011', '0b0000000001110', '0b00000000101', '0b000000100'],
                         # row = 8
                         ['0b0000000001000', '0b0000000001010', '0b0000000001101', '0b0000000100'],
                         ['0b00000000001111', '0b00000000001110', '0b0000000001001', '0b00000000100'],
                         ['0b00000000001011', '0b00000000001010', '0b00000000001101', '0b0000000001100'],
                         # row from 11~16 to be continued
                        ],

                        #talbe1
                        [[0, 3, -1, 0],
                         [0, -1, 1, 0],
                         [1, 0, 0, 0],
                         [0, 0, 0, 0]],
                         
                        ])

if __name__ == "__main__":
    print(coeff_token.shape)
    print(coeff_token)
    print(coeff_token[0][0][0])
    print(coeff_token[0][2][1])
    print(coeff_token[0][8][1])
    print(type(coeff_token[0][0][0]))