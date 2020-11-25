# 4 × 4 Transform and quantization
#
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

import numpy as np
import dct_formula_2D
import ZigZag
import math
import logging

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

# Hadamard transform matrix
HWd = np.array([[1, 1, 1, 1],
                [1, 1, -1, -1],
                [1, -1, -1, 1],
                [1, -1, 1, -1]])

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

    # according to formula 7.22 on page 194
    Vi4 = np.array([[Vtb[row, 0], Vtb[row, 2], Vtb[row, 0], Vtb[row, 2]],
                    [Vtb[row, 2], Vtb[row, 1], Vtb[row, 2], Vtb[row, 1]],
                    [Vtb[row, 0], Vtb[row, 2], Vtb[row, 0], Vtb[row, 2]],
                    [Vtb[row, 2], Vtb[row, 1], Vtb[row, 2], Vtb[row, 1]]])

    return Vi4

def getLevelScaleOfLumaDC(qp):
    '''
    get LevelScale matrix by QP value
    accroding to 8-252 formula on page 136 of [H.264 standard Book]
    : param qp: the QP enum value in H.264
    '''
    row = qp
    if (qp<=5):
        row = qp
    else:
        row = qp%6

    # according to formula 8-252 on page 136
    ls4 = np.array([[Vtb[row, 0], Vtb[row, 2], Vtb[row, 0], Vtb[row, 2]],
                    [Vtb[row, 2], Vtb[row, 1], Vtb[row, 2], Vtb[row, 1]],
                    [Vtb[row, 0], Vtb[row, 2], Vtb[row, 0], Vtb[row, 2]],
                    [Vtb[row, 2], Vtb[row, 1], Vtb[row, 2], Vtb[row, 1]]])

    return ls4

def forwardTransformAndScaling4x4(X, QP):
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

def forwardHadamardAndScaling4x4(X, QP):
    """
    Integer Hadamard transform and quantization : 4 × 4 blocks
    The forward integer Hadamard transform processes for 4 × 4 blocks, 
    accroding to 7.28 formula on page 203
    Args:
        X: input data block, currently should be 4x4 square
        QP: the qp step
    """
    #step1: Calculate 4 × 4 Hadamard transform
    temp = np.dot(HWd, X)
    temp = np.dot(temp, HWd) / 2

    # step2: Scaling and quantization
    Mf4 = getMf4ByQP(QP)
    #print(Mf4)

    scaler = math.pow(2, 15+math.floor(QP/6))
    Y = np.round(temp * Mf4 / scaler, 0)

    return Y

def inverseIntra16x16LumaDCScalingAndTransform(C, QP):
    """
    Scaling and transformation process for luma DC transform coefficients for Intra_16x16 macroblock type
    According to 8.5.6 on page 136 of [H.264 standard Book]
    Args:
        C: input LumaDC data block, currently should be 4x4 square
        QP: the qp step
    """
    #step1: Calculate 4 × 4 inverse transform
    temp = np.dot(HWd, C)
    f = np.dot(temp, HWd)
    logging.debug("Inverse Transform:\n %s", f)

    # step2: Scaling and quantization
    ls4 = getLevelScaleOfLumaDC(QP)
    #logging.debug("\n%s", ls4)

    if QP>=12:
        Y = f * ls4 * pow(2, int(QP/6)-2)
        return Y
    else:
        Y = ( f * ls4 + pow(2, 1-int(QP/6)) ) / pow(2, 2-int(QP/6))
        return Y

def inverseReidual4x4ScalingAndTransform(C, QP):
    """
    Scaling and transformation process for residual 4x4 blocks
    According to 8.5.8 on page 137 of [H.264 standard Book]
    Args:
        C: input coefficients of residual 4x4 block, with C[0, 0] replaced by LumacDC[0, 0] in Intra16x16 mode
        QP: the qp step
    Return:
        r: the reconstruction of residual 4x4 block
    """
    d = np.array([[0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0]])


    vi4 = getVi4ByQP(20)
    #logging.debug(vi4)

    d = C * vi4 * pow(2, int(20/6))
    d[0, 0] = C[0, 0]
    #logging.debug("d:\n%s",d)

    e = np.array([[0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0]])

    for i in range(0, 4):
        e[i,0] = d[i,0] + d[i,2]
        e[i,1] = d[i,0] - d[i,2]
        e[i,2] = (d[i,1]>>1) - d[i,3]
        e[i,3] = d[i,1] + (d[i,3]>>1)

    #logging.debug("e:\n%s",e)

    f = np.array([[0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0]])

    for i in range(0, 4):
        f[i,0] = e[i,0] + e[i,3]
        f[i,1] = e[i,1] + e[i,2]
        f[i,2] = e[i,1] - e[i,2]
        f[i,3] = e[i,0] - e[i,3]

    #logging.debug("f:\n%s",f)

    g = np.array([[0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0]])

    for j in range(0, 4):
        g[0,j] = f[0,j] + f[2,j]
        g[1,j] = f[0,j] - f[2,j]
        g[2,j] = (f[1,j]>>1) - f[3,j]
        g[3,j] = f[1,j] + (f[3,j]>>1)

    #logging.debug("g:\n%s",g)

    h = np.array([[0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0],
                  [0, 0, 0, 0]])

    for j in range(0, 4):
        h[0,j] = g[0,j] + g[3,j]
        h[1,j] = g[1,j] + g[2,j]
        h[2,j] = g[1,j] - g[2,j]
        h[3,j] = g[0,j] - g[3,j]

    #logging.debug("h:\n%s", h)

    r = np.floor( (h + pow(2, 5)) / pow(2, 6) )
    
    #logging.debug("r\n%s", r)
    return r

def inverse_P_Reidual4x4ScalingAndTransform(P, C, QP):
    """
    Scaling and transformation process for residual 4x4 P macroblocks
    According to 8.6.1.1 on page 140 of [H.264 standard Book]
    Args:
        P: 4x4 array of prediction samples
        C: input coefficients of residual 4x4 block, with C[0, 0] replaced by LumacDC[0, 0] in Intra16x16 mode
        QP: the qp step
    Return:
        r: the reconstruction of residual 4x4 block
    """
    # step1: inverse transform coefficients
    CL4 = np.array([[1, 1, 1, 1],
                    [2, 1, -1, -2],
                    [1, -1, -1, 1],
                    [1, -2, 2, -1]])

    CR4 = np.array([[1, 2, 1, 1],
                    [1, 1, -1, -2],
                    [1, -1, -1, 2],
                    [1, -2, 1, -1]])

    temp = np.dot(CL4, P)
    f = np.dot(temp, CR4)

    # step2: Scaling and quantization
    ls4 = getLevelScaleOfLumaDC(QP)
    #logging.debug("\n%s", ls4)

    A = np.array([[16, 20, 16, 20],
                  [20, 25, 20, 25],
                  [16, 20, 16, 20],
                  [20, 25, 20, 25]])

    Cs = f + (((C * ls4 * A) << int(QP/6)) >> 6)

    levelScale2 = getMf4ByQP(QP)

    r = (np.sign(Cs) * (abs(Cs) * levelScale2 + (1<<(14+int(QP/6))))) >> (15+int(QP/6))

    return inverseReidual4x4ScalingAndTransform(r, QP)

def testCase1():
    test = np.array([[58, 64, 51, 58],
                     [52, 64, 56, 66],
                     [62, 63, 61, 64],
                     [59, 51, 63, 69]])
    print("Test data:")
    print(test)

    # part1: use H.264 formula to transform
    QP = 6
    code = forwardTransformAndScaling4x4(test, QP)
    print("Forward transform and coding:")
    print(code)

    #use Zigzag to scan
    print("ZiaZag scan:")
    zig = ZigZag.ZigzagMatrix()
    res = zig.matrix2zig(code)
    print(res)

    print("UnZiaZag scan:")
    res = zig.zig2matrix(res, 4, 4)
    print(res)

    #inverse transform
    back = inverseTransformAndScaling4x4(res, QP)
    print("Inverse transform and decoding:")
    print(back)

    # Part2: Use DCT to compare, it is not totally the same as H.264 transform
    dct = np.round(dct_formula_2D.Img2DctUsingScipy(test, 4), 4)
    print(dct)
    img_dct = dct_formula_2D.Dct2ImgUsingScipy(dct, 4)
    print(img_dct)

def testCase2():
    dct = np.array([[0, 0, -2, -1],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0]])
    logging.debug("dct data:\n %s", dct)

    QP = 20
    back = inverseTransformAndScaling4x4(dct, QP)
    logging.debug("Inverse:\n %s", back)

def testLumaDC():
    luma_dc_dct = np.array([[75, 0, -1, 2],
                            [3, 1, -1, 1],
                            [2, 0, 0, 0],
                            [1, 0, 0, 0]])
    logging.debug("Luma DC dct data:\n %s", luma_dc_dct)

    QP = 20
    back = inverseIntra16x16LumaDCScalingAndTransform(luma_dc_dct, QP)
    logging.debug("Inverse:\n %s", back)

def testResidual4x4():
    # c = np.array([[2158, 0, 0, 0],
    #               [0, 0, 0, 0],
    #               [0, 0, 0, 0],
    #               [0, 0, 0, 0]])

    # c = np.array([[2002, 1, 0, 0],
    #               [1, 0, 0, 0],
    #               [0, 0, 0, 0],
    #               [0, -1, 0, 0]])

    c = np.array([[1898, -2, 1, -1],
                  [0, 0, 0, 0],
                  [1, -1, 1, 0],
                  [0, 0, 0, 0]])

    residual = inverseReidual4x4ScalingAndTransform(c, 20)
    logging.debug("Inverse:\n %s", residual)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("transform.log", mode='w'),
            logging.StreamHandler(),
        ]
    )

    #testCase1()

    #testCase2()

    testLumaDC()

    testResidual4x4()