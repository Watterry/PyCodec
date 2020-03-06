# 4 × 4 Transform and quantization

import numpy as np
import dct_formula_2D
import math

Cf4 = np.array([[1, 1, 1, 1],
                [2, 1, -1, -2],
                [1, -1, -1, 1],
                [1, -2, 2, -1]])

# table M
Mtb = np.array([[13107, 5243, 8066],
                [11916, 4660, 7490],
                [10082, 4194, 6554],
                [9362, 3647, 5825],
                [8192, 3355, 5243],
                [7282, 2893, 4559]])

def getMf4ByQP(qp):
    '''
    get Mf4 matrix by QP value
    : param qp: the QP enum value in H.264
    '''
    row = qp
    if (qp<=5):
        row = qp
    else:
        row = qp%6

    Mf4 = np.array([[Mtb[row, 0], Mtb[row, 2], Mtb[row, 0], Mtb[row, 2]],
                    [Mtb[row, 2], Mtb[row, 1], Mtb[row, 2], Mtb[row, 1]],
                    [Mtb[row, 0], Mtb[row, 2], Mtb[row, 0], Mtb[row, 2]],
                    [Mtb[row, 2], Mtb[row, 1], Mtb[row, 2], Mtb[row, 1]]])

    return Mf4

def forwardTransformAndCoding4x4(X):
    '''
    Integer transform and quantization : 4 × 4 blocks
    The forward integer transform processes for 4 × 4 blocks, 
    accroding to 7.24 formula on page 194
    : param X: input data block, currently should be 4x4 square
    '''
    #step1: Calculate Cf4·X·Cf4T
    temp = np.dot(np.dot(Cf4, X), np.transpose(Cf4))
    #print(temp)

    # step2: Scaling and quantization, QP = 6
    QP = 6 
    Mf4 = getMf4ByQP(QP)
    #print(Mf4)

    scaler = math.pow(2, 15+math.floor(QP/6))
    Y = np.round(temp * Mf4 / scaler, 0)
    #print("result:")
    #print(Y)

    return Y

def inverseTransformAndCoding4x4(X):
    '''
    Integer transform and quantization : 4 × 4 blocks
    The inverse integer transform processes for 4 × 4 blocks, 
    accroding to 7.18 formula on page 194
    : param X: input data block, currently should be 4x4 square coefficients
    '''

if __name__ == "__main__":
    test = np.array([[58, 64, 51, 58],
                     [52, 64, 56, 66],
                     [62, 63, 61, 64],
                     [59, 51, 63, 69]])
    print("Test data:")
    print(test)

    code = forwardTransformAndCoding4x4(test)
    print("Forward transform and coding:")
    print(code)


    # Use DCT to compare
    dct = np.round(dct_formula_2D.Img2DctUsingScipy(test, 4), 4)
    print(dct)