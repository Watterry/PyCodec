# Do H.264 core encoding process
import prediction
import matplotlib.pyplot as plt
import numpy as np
from numpy import r_
import transform as tf
import coding as cd

def encoding16x16(block):
    """
    Encode a 16x16 macroblock
    Args:
        block: 16x16 matrix block
    
    Returns:
    """
    QP = 6

    # step1: Get the DC element of each 4x4 block
    size = block.shape
    step = 4

    DC_block = np.full((4,4), 0)
    for i in r_[:size[0]:step]:
        for j in r_[:size[1]:step]:
            x = int(i/4)
            y = int(j/4)
            DC_block[x][y] = block[i, j]
    
    # DC transorm coding
    tf.forwardHadamardAndScaling4x4(DC_block, QP)

    # step2: 4x4 transform, quantization and coding
    current = np.full((4,4), 0)
    for i in r_[:size[0]:step]:
        for j in r_[:size[1]:step]:

            current = block[i:(i+step), j:(j+step)]
            print("current block:")
            print(current)

            temp = tf.forwardTransformAndScaling4x4(current, QP)
            print("coefficients:")
            print(temp)
            cd.CAVLC(temp)


def H264Encode(im):
    """
    The core process of H264 encoding
    Args:
        im: the input frame

    returns:
        The binary code of the frame
    """

    predict, residual, mode_map = prediction.IntraPrediction(im, 16)  # 16x16 intra mode

    #according to page 133 Figure 8-6
    step = 16
    imsize = residual.shape
    for i in r_[:imsize[0]:step]:
        for j in r_[:imsize[1]:step]:

            block16x16 = residual[i:(i+step), j:(j+step)]
            encoding16x16(block16x16)


if __name__ == '__main__':
    im = plt.imread("E:/liumangxuxu/code/PyCodec/modules/lena2.tif").astype(float)
    H264Encode(im)
    