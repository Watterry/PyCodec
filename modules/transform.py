# 4 × 4 Transform and quantization

import numpy as np
import dct_formula_2D
import math

Cf4 = np.array([[1, 1, 1, 1],
                [2, 1, -1, -2],
                [1, -1, -1, 1],
                [1, -2, 2, -1]])

Ci4 = np.array([[1, 1, 1, 1],
                [1, 1/2, -1/2, -1],
                [1, -1, -1, 1],
                [1/2, -1, 1, -1/2]])

# table M, from Table 7.4 on page 194
Mtb = np.array([[13107, 5243, 8066],
                [11916, 4660, 7490],
                [10082, 4194, 6554],
                [9362, 3647, 5825],
                [8192, 3355, 5243],
                [7282, 2893, 4559]])

# table V, from Table 7.4 on page 194
Vtb = np.array([[10, 16, 13],
                [11, 18, 14],
                [13, 20, 16],
                [14, 23, 18],
                [16, 25, 20],
                [18, 29, 23]])

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

    # accroding to formula 7.22 on page 194
    Mf4 = np.array([[Mtb[row, 0], Mtb[row, 2], Mtb[row, 0], Mtb[row, 2]],
                    [Mtb[row, 2], Mtb[row, 1], Mtb[row, 2], Mtb[row, 1]],
                    [Mtb[row, 0], Mtb[row, 2], Mtb[row, 0], Mtb[row, 2]],
                    [Mtb[row, 2], Mtb[row, 1], Mtb[row, 2], Mtb[row, 1]]])

    return Mf4

def getVi4ByQP(qp):
    '''
    get Ci4 matrix by QP value
    : param qp: the QP enum value in H.264
    '''
    row = qp
    if (qp<=5):
        row = qp
    else:
        row = qp%6

    # accroding to formula 7.22 on page 194
    Vi4 = np.array([[Vtb[row, 0], Vtb[row, 2], Vtb[row, 0], Vtb[row, 2]],
                    [Vtb[row, 2], Vtb[row, 1], Vtb[row, 2], Vtb[row, 1]],
                    [Vtb[row, 0], Vtb[row, 2], Vtb[row, 0], Vtb[row, 2]],
                    [Vtb[row, 2], Vtb[row, 1], Vtb[row, 2], Vtb[row, 1]]])

    return Vi4

def forwardTransformAndCoding4x4(X, QP):
    '''
    Integer transform and quantization : 4 × 4 blocks
    The forward integer transform processes for 4 × 4 blocks, 
    accroding to 7.24 formula on page 194
    : param X: input data block, currently should be 4x4 square
    : param QP: the qp step
    '''
    #step1: Calculate Cf4·X·Cf4T
    temp = np.dot(np.dot(Cf4, X), np.transpose(Cf4))
    #print(temp)

    # step2: Scaling and quantization
    Mf4 = getMf4ByQP(QP)
    #print(Mf4)

    scaler = math.pow(2, 15+math.floor(QP/6))
    Y = np.round(temp * Mf4 / scaler, 0)
    #print("result:")
    #print(Y)

    return Y

def inverseTransformAndScaling4x4(Y, QP):
    '''
    Integer transform and quantization : 4 × 4 blocks
    The inverse integer transform processes for 4 × 4 blocks, 
    accroding to 7.18 formula on page 194
    : param X: input data block, currently should be 4x4 square coefficients
    : param QP: the qp step
    '''
    # step1: Scaling and quantization, QP = 6
    Vi4 = getVi4ByQP(QP)
    #print(Vi4)

    # step2: calculate middle data
    temp = Y * Vi4
    temp = temp * math.pow(2, math.floor(QP/6))

    #step3: Calculate Vi4T·temp·Vi4
    temp = np.dot(np.dot(np.transpose(Ci4), temp), Ci4)
    #print(temp)

    X = np.round(temp / math.pow(2, 6), 0)
    #print("result:")
    #print(X)

    return X

if __name__ == "__main__":
    test = np.array([[58, 64, 51, 58],
                     [52, 64, 56, 66],
                     [62, 63, 61, 64],
                     [59, 51, 63, 69]])
    print("Test data:")
    print(test)

    QP = 6
    code = forwardTransformAndCoding4x4(test, QP)
    print("Forward transform and coding:")
    print(code)

    back = inverseTransformAndScaling4x4(code, QP)
    print("Inverse transform and decoding:")
    print(back)

    # Use DCT to compare
    dct = np.round(dct_formula_2D.Img2DctUsingScipy(test, 4), 4)
    print(dct)