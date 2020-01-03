import matplotlib.pyplot as plt
import numpy as np
from numpy import r_


def SAE(a, b):
    '''
    calculate Sum of Absolute Errors of two images, divided by number of pixels
    :param a: image A, matrix
    :param b: image B, matrix
    '''
    result = np.sum(np.abs(np.subtract(a,b,dtype=np.float))) / (a.size)
    return result

# 16x16 block's Mode 0 (vertical) prediction mode
def mode0_16x16(block, H):
    size = block.shape
    temp = np.zeros(size)
    for i in range(0, size[0]):
        temp[i,:] = H

    #print(temp)
    return block-temp

# 16x16 block's Mode 1 (horizontal) prediction mode
def mode1_16x16(block, V):
    size = block.shape
    temp = np.zeros(size)
    for i in range(0, size[1]):
        temp[:,i] = V

    #print(temp)
    return block-temp

# 16x16 block's Mode 2 (mean) prediction mode
def mode2_16x16(block, H, V):
    size = block.shape

    mean = (np.sum(H) + np.sum(V)) / (H.size+V.size)

    temp = np.zeros(size)
    temp[:] = mean

    #print(temp)
    return block-temp

def processWholeImage():
    im = plt.imread("E:/liumangxuxu/code/PyCodec/modules/lena2.tif").astype(float)
    print(im.shape)
    
    step = 16 # 16x16 as block
    imsize = im.shape

    result = np.zeros(imsize)   # prediction result
    rebuild = np.zeros(imsize)   # reconstructed frame
    for i in r_[:imsize[0]:step]:
        for j in r_[:imsize[1]:step]:
            if (i==0) and (j==0):  # for left-top block, just copy the data
                result[i:(i+step),j:(j+step)] = im[i:(i+step),j:(j+step)]

            elif i==0 and j!=0:
                #print(im[i:(i+step), j-1])
                #print(rebuild[i:(i+step), j-1])
                result[i:(i+step),j:(j+step)] = mode1_16x16(im[i:(i+step),j:(j+step)], rebuild[i:(i+step),j-1])
                
            elif j==0 and i!=0:
                #print(im[i:(i+step), j-1])
                #print(rebuild[i:(i+step), j-1])
                result[i:(i+step),j:(j+step)] = mode0_16x16(im[i:(i+step),j:(j+step)], rebuild[i-1,j:(j+step)])

            else:
                result[i:(i+step),j:(j+step)] = mode2_16x16(im[i:(i+step),j:(j+step)], rebuild[i-1,j:(j+step)], rebuild[i:(i+step),j-1])

            # todo: need to use quantilization to reconstruct
            rebuild[i:(i+step),j:(j+step)] = im[i:(i+step),j:(j+step)]

    diff = SAE(im, result)
    print(diff)

    plt.figure()
    plt.imshow(im, cmap='gray')
    plt.title("Original of the image")

    plt.figure()
    plt.imshow(result, cmap='gray')
    plt.title("Prediction result of the image")

    plt.figure()
    plt.imshow(rebuild, cmap='gray')
    plt.title("Rebuild of the image")

    plt.show()

if __name__ == "__main__":
    np.set_printoptions(suppress=True)

    processWholeImage()