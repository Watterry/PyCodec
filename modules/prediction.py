# prediction and inverse prediction, reconstrcut of frame
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

import matplotlib.pyplot as plt
import numpy as np
from numpy import r_
import sys
import ZigZag
import tools
import logging
import copy
import dct_formula_2D

# the function mode0_16x16 to mode3_16x16 is according to Table 8-3 on page 106 of [H.264 standard Book]
def mode0_16x16(size, H):
    """
    16x16 block's Mode 0 (Vertical) prediction mode
    Args:
        size: the prediction block's size, should be 16x16 here
        H: the horizontal predict value
    Return:
        the prediction result
    """
    logging.debug("H: %s", H)
    temp = np.zeros(size, int)
    for i in range(0, size[1]):
        temp[i,:] = H

    #print(temp)
    return temp

def mode1_16x16(size, V):
    """
    16x16 block's Mode 1 (Horizontal) prediction mode
    Args:
        size: the prediction block's size, should be 16x16 here
        H: the horizontal predict value
    Return:
        the prediction result
    """
    logging.debug("V: %s", V)
    temp = np.zeros(size, int)
    for j in range(0, size[1]):
        temp[:,j] = V

    return temp

def mode2_16x16(size, H, V):
    """
    16x16 block's Mode 2 (DC) prediction mode
    Args:
        size: the prediction block's size, should be 16x16 here
        H: the horizontal predict value, -1 means not available
        V: the vertical predict value, -1 means not available
    Return:
        the prediction result
    """
    H_Available = False if np.sum(H<0) > 0 else True
    V_Available = False if np.sum(V<0) > 0 else True
    logging.debug("H: %s", H)
    logging.debug("V: %s", V)
    mean = 0
    if H_Available and V_Available:
        logging.debug("H & V are available")
        mean = ((np.sum(H) + np.sum(V)) + 16) >> 5
    elif H_Available and (not V_Available):
        logging.debug("H are available")
        mean =  (np.sum(H)+8) >> 4
    elif (not H_Available) and V_Available:
        logging.debug("V are available")
        mean =  (np.sum(V)+8) >> 4
    else:
        logging.debug("H & V are not available")
        mean = 128

    temp = np.zeros(size, int)
    temp[:] = int(mean)

    return temp

def Clip3(x, y, z):
    """
    According to page 10 of [H.264 standard Book]
    """
    if z<x:
        return x
    elif z > y:
        return y
    else:
        return z

def Clip1(x):
    """
    According to page 10 of [H.264 standard Book]
    """
    return Clip3( int(0), int(255), x)

# TODO: this function should be verified by x264 related code
def mode3_16x16(size, H, V, P):
    """
    16x16 block's Mode 3 (plan) prediction mode
    Args:
        size: the prediction block's size, should be 16x16 here
        H: the horizontal predict value
        V: the vertical predict value
        P: the P[-1, -1] value
    Return:
        the prediction result
    """
    logging.debug("H: %s", H)
    logging.debug("V: %s", V)
    logging.debug("p: %d", P)
    h = 0
    v = 0

    for x in range(0,8):
        if (x==7):
            h = h + (x+1)*(H[8+x]-P)   # use P point value to replace p[-1, -1]
        else:
            h = h + (x+1)*(H[8+x]-H[6-x])

    for y in range(0,8):
        if (y==7):
            v = v + (y+1)*(V[8+y]-P)   # use P point value to replace p[-1, -1]
        else:
            v = v + (y+1)*(V[8+y]-V[6-y])

    a = 16*( H[15] + V[15] )
    b = ( 5*h + 32 ) >> 6
    c = ( 5*v + 32 ) >> 6

    temp = np.zeros(size, int)

    for x in range(0,16):
        for y in range(0,16):
            pred = int( (a + b*(x-7) + c*(y-7) + 16) >> 5 )
            temp[y,x] = Clip1( pred )   # Attention: here x, y is inverse of matrix [y,x]

    return temp

def pickTheBestMode(block, H, V, P):
    temp0 = mode0_16x16(block.shape, H)
    diff0 = tools.SAE(block, temp0)
    
    temp1 = mode1_16x16(block.shape, V)
    diff1 = tools.SAE(block, temp1)

    temp2 = mode2_16x16(block.shape, H, V)
    diff2 = tools.SAE(block, temp2)

    temp3 = mode3_16x16(block.shape, H, V, P)
    diff3 = tools.SAE(block, temp3)

    list1, list2 = [temp0, temp1, temp2, temp3], [diff0, diff1, diff2, diff3]
    mode = list2.index(min(list2))

    return list1[mode], mode

def IntraPrediction(im, step):
    '''
    image intra predict
    : param im: input image
    : param step: macroblock's width
    : return: dct coefficient after quantization, zigzag, zlib compression
    '''
    imsize = im.shape

    predict = np.zeros(imsize, int)    # intra prediction result, motion compensation
    mode_map = np.zeros(imsize, int)    # save block mode information

    # init value
    H = im[0, 0:(0+step)].copy()
    V = im[0:(0+step), 0].copy()

    P = 128

    for i in r_[:imsize[0]:step]:
        for j in r_[:imsize[1]:step]:

            if (i==0) and (j==0):  # for left-top block, just copy the data
                H[:] = 128
                V[:] = 128
                P = 128

            elif i==0 and j!=0:
                H = im[i,j:(j+step)]
                V = im[i:(i+step),j-1]
                P = im[i, j-1]
                
            elif j==0 and i!=0:
                H = im[i-1,j:(j+step)]
                V = im[i:(i+step),j]
                P = im[i-1, j]

            else:
                H = im[i-1,j:(j+step)]
                V = im[i:(i+step),j-1]
                P = im[i-1, j-1]

            block = im[i:(i+step),j:(j+step)].copy()
            predict[i:(i+step),j:(j+step)], mode = pickTheBestMode(block, H, V, P)
            mode_map[i:(i+step),j:(j+step)].fill(mode)

    diff = tools.SAE(im, predict)
    print(diff)

    residual = im - predict

    return predict, residual, mode_map

def predictImage(im, qp, block_step):
    '''
    image intra predict, transform, zigzag coding example
    : param im: input image
    : param qp: quantization step size
    : param block_step: the predict block size, the block should be step*step
    : return: dct coefficient after quantization, zigzag, zlib compression
    '''
    
    step = block_step # 16x16 as block
    predict, residual, mode_map = IntraPrediction(im, block_step)


    plt.figure()
    plt.imshow(im, cmap='gray')
    plt.title("Original of the image")

    plt.figure()
    plt.imshow(predict, cmap='gray')
    plt.title("Prediction Using H.264 16x16 intra prediction")

    plt.figure()
    plt.imshow(mode_map, cmap='gray')
    # add mode number on the picture
    # for i in r_[:imsize[0]:step]:
    #     for j in r_[:imsize[1]:step]:
    #         plt.text(i+4, j+4, mode_map[i,j])
    plt.title("mode map of 16x16 block intra prediction")

    plt.figure()
    plt.imshow(residual, cmap='gray')
    plt.title("residual after subtracting intra prediction")

    #compare the DCT result of origianl image and residual image
    # dct, img_dct = dct_formula_2D.ImgDctUsingDetail(im)
    # dct_residual, idct_residual = dct_formula_2D.ImgDctUsingDetail(residual)
    dct = np.round(dct_formula_2D.Img2DctUsingScipy(im, step), 4)
    dct_residual = np.round(dct_formula_2D.Img2DctUsingScipy(residual, step), 4)

    plt.figure()
    plt.imshow(dct, cmap='gray', vmax = np.max(dct)*0.01,vmin = 0)
    plt.title("DCT coefficients of original image")

    plt.figure()
    plt.imshow(dct_residual, cmap='gray', vmax = np.max(dct_residual)*0.01,vmin = 0)
    plt.title("DCT coefficients of residual image")

    # np.savetxt("dct.csv", np.trunc(dct), delimiter=",", fmt='%.1f')
    # np.savetxt("dct_residual.csv", np.trunc(dct_residual), delimiter=",", fmt='%.1f')

    print("Image zlib size:")
    im_1D = ZigZag.Compress(im, qp)
    print(sys.getsizeof(im_1D))

    print("DCT zlib size:")
    dct_1D = ZigZag.Compress(dct, qp)
    print(sys.getsizeof(dct_1D))

    print("dct_residual zlib size:")
    dct_res_1D = ZigZag.Compress(dct_residual, qp)
    print(sys.getsizeof(dct_res_1D))

    print("mode map zlib size:")
    mode_1D = ZigZag.Compress(mode_map, 1)
    print(sys.getsizeof(mode_1D))

    #return dct_1D   #temp test code
    return dct_res_1D, mode_1D

def inverseIntraPrediction(residual, mode_map, mb_step):
    """
    image intra predict inverse operation

    Args:
        residual: residual image after coefficient inverse operation
        mode_map: the prediction mode map of residual image
        mb_step: macroblock's width
    
    Returns:
        the recovered original image
    """
    imsize = residual.shape
    reconstruted = np.zeros(imsize, int)    # intra prediction result, motion compensation
    step = mb_step
    size = (step, step)

    # init value
    H = reconstruted[0, 0:(0+step)].copy()
    V = reconstruted[0:(0+step), 0].copy()
    P = 128

    for i in r_[:imsize[0]:step]:
        for j in r_[:imsize[1]:step]:
            logging.debug("----------------------------------------")
            logging.debug("blk16x16Idx x: %d, y: %d", i/16, j/16)
            if (i==0) and (j==0):  # for left-top block, just copy the data
                H[:] = int(128)
                V[:] = int(128)
                P = int(128)

            elif i==0 and j!=0:
                H[:] = -1   # -1 means not available
                V = reconstruted[i:(i+step),j-1].copy()
                P = reconstruted[i, j-1]
                
            elif j==0 and i!=0:
                H = reconstruted[i-1,j:(j+step)].copy()
                V[:] = -1   # -1 means not available
                P = reconstruted[i-1, j]

            else:
                H = reconstruted[i-1,j:(j+step)].copy()
                V = reconstruted[i:(i+step),j-1].copy()
                P = reconstruted[i-1, j-1]

            #get mode and generate predction image
            predicted = np.zeros((step, step), int)
            if mode_map[i+1, j+1] == 0:
                logging.debug("Prediction Mode Vertical")
                predicted = mode0_16x16(size, H)
            elif mode_map[i+1, j+1] == 1:
                logging.debug("Prediction Mode Horizontal")
                predicted = mode1_16x16(size, V)
            elif mode_map[i+1, j+1] == 2:
                logging.debug("Prediction Mode DC")
                predicted = mode2_16x16(size, H, V)
            elif mode_map[i+1, j+1] == 3:
                logging.debug("Prediction Mode Plane")
                predicted = mode3_16x16(size, H, V, P)
            else:
                logging.error("Predict Mode Error!")

            reconstruted[i:(i+step),j:(j+step)] = (residual[i:(i+step),j:(j+step)] + predicted).copy()
            logging.debug("residual Values:\n%s", residual[i:(i+step),j:(j+step)])
            logging.debug("Predicted Values:\n%s", predicted)
            logging.debug("Decoded Y Values:\n%s", reconstruted[i:(i+step),j:(j+step)])

    return reconstruted

def inversePredictImage(binary, mode_1D, qp, m, n, block_step):
    '''
    Inverse image intra predict, transform, zigzag coding example
    : param binary: the binary data compressed by zlib
    : param mode_1D: the predict mode map of image
    : param qp: the quantization step
    : param m,n: the size of image, m*n
    : param block_step: the predict block size, the block should be step*step
    '''
    dct_residual =  ZigZag.UnCompress(binary, qp, m, n)
    residual = dct_formula_2D.Dct2ImgUsingScipy(dct_residual, block_step)

    mode_map =  ZigZag.UnCompress(mode_1D, 1, m, n)

    # TODO: use residual and mode_map to reconstruct the original image
    original = inverseIntraPrediction(residual, mode_map, block_step)

    return original

def testCase1():
    qp = 15
    step = 16
    im = plt.imread("E:/liumangxuxu/code/PyCodec/modules/lena2.tif").astype(int)
    print(im.shape)
    residual_1D, mode_1D = predictImage(im, qp, step)

    i_im = inversePredictImage(residual_1D, mode_1D, qp, im.shape[0], im.shape[1], step)

    plt.figure()
    plt.imshow(i_im, cmap='gray')
    plt.title("Inverse image")

    logging.debug("Inverse Image PSNR:")
    logging.debug(tools.psnr(im, i_im))

    plt.show()

def testCase2():
    mbWidth = 16

    residual = np.load("../test/residual.npy")
    modemap = np.load("../test/modemap.npy")

    image = inverseIntraPrediction(residual, modemap, mbWidth)

    plt.figure()
    plt.imshow(residual, cmap='gray')
    plt.title("residual image")

    plt.figure()
    plt.imshow(modemap, cmap='gray')
    plt.title("ModeMap image")

    plt.figure()
    plt.imshow(image, cmap='gray')
    plt.title("Inverse image")

    plt.show()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("prediction.log", mode='w'),
            logging.StreamHandler(),
        ]
    )
    logging.getLogger('matplotlib.font_manager').disabled = True
    np.set_printoptions(threshold=sys.maxsize)

    np.set_printoptions(suppress=True)

    #testCase1()
    testCase2()