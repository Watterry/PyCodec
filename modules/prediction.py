import matplotlib.pyplot as plt
import numpy as np
from numpy import r_
import dct_formula_2D
import sys
import ZigZag
import tools

# 16x16 block's Mode 0 (vertical) prediction mode
def mode0_16x16(block, H):
    size = block.shape
    temp = np.zeros(size)
    for i in range(0, size[0]):
        temp[i,:] = H

    #print(temp)
    diff = tools.SAE(block, temp)
    return temp, diff

# 16x16 block's Mode 1 (horizontal) prediction mode
def mode1_16x16(block, V):
    size = block.shape
    temp = np.zeros(size)
    for i in range(0, size[1]):
        temp[:,i] = V

    #print(temp)
    diff = tools.SAE(block, temp)
    return temp, diff

# 16x16 block's Mode 2 (mean) prediction mode
def mode2_16x16(block, H, V):
    size = block.shape

    mean = (np.sum(H) + np.sum(V)) / (H.size+V.size)

    temp = np.zeros(size)
    temp[:] = mean

    #print(temp)
    diff = tools.SAE(block, temp)
    return temp, diff

# 16x16 block's Mode 3 (plan) prediction mode
# TODO: this function should be verified by x264 related code
def mode3_16x16(block, H, V, P):
    size = block.shape

    h = 0
    v = 0

    for x in range(0,8):
        if (x==7):
            h = h + (x+1)*(V[8+x]-P)   # use P point value to replace p[-1, -1]
        else:
            h = h + (x+1)*(V[8+x]-V[6-x])

    for y in range(0,8):
        if (y==7):
            v = v + (y+1)*(H[8+y]-P)   # use P point value to replace p[-1, -1]
        else:
            v = v + (y+1)*(H[8+y]-H[6-y])

    a = 16*( H[15] + V[15] )
    b = ( 5*h + 32 ) / 64
    c = ( 5*v + 32 ) / 64

    temp = np.zeros(size)

    for i in range(0,8):
        for j in range(0,8):
            temp[i,j] = (a + b*(i-7) + c*(j-7) + 16) / 32

    #print(temp)
    diff = tools.SAE(block, temp)
    return temp, diff

def pickTheBestMode(block, H, V, P):
    temp0, diff0 = mode0_16x16(block, H)
    temp1, diff1 = mode1_16x16(block, V)
    temp2, diff2 = mode2_16x16(block, H, V)
    temp3, diff3 = mode3_16x16(block, H, V, P)

    list1, list2 = [temp0, temp1, temp2, temp3], [diff0, diff1, diff2, diff3]
    mode = list2.index(min(list2))

    return list1[mode], mode

def IntraPrediction(im, qp, step):
    '''
    image intra predict
    : param im: input image
    : param qp: quantization step size
    : return: dct coefficient after quantization, zigzag, zlib compression
    '''
    imsize = im.shape

    predict = np.zeros(imsize)    # intra prediction result, motion compensation
    mode_map = np.zeros(imsize)    # save block mode information

    for i in r_[:imsize[0]:step]:
        for j in r_[:imsize[1]:step]:
            H = np.zeros((step, 1))
            V = np.zeros((1, step))
            P = 0   # the value of left top conner of pixel

            if (i==0) and (j==0):  # for left-top block, just copy the data
                H = im[i,j:(j+step)]
                V = im[i:(i+step),j]
                P = im[0, 0]

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

            predict[i:(i+step),j:(j+step)], mode = pickTheBestMode(im[i:(i+step),j:(j+step)], H, V, P)
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
    predict, residual, mode_map = IntraPrediction(im, qp, block_step)


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
    img = dct_formula_2D.Dct2ImgUsingScipy(dct_residual, block_step)

    mode_map =  ZigZag.UnCompress(mode_1D, 1, m, n)

    return img

if __name__ == "__main__":
    np.set_printoptions(suppress=True)

    qp = 15
    step = 16
    im = plt.imread("E:/liumangxuxu/code/PyCodec/modules/lena2.tif").astype(float)
    print(im.shape)
    residual_1D, mode_1D = predictImage(im, qp, step)

    i_im = inversePredictImage(residual_1D, mode_1D, qp, im.shape[0], im.shape[1], step)

    plt.figure()
    plt.imshow(i_im, cmap='gray')
    plt.title("Inverse image")

    print("Inverse Image PSNR:")
    print(tools.psnr(im, i_im))

    plt.show()