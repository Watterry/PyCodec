import numpy as np
import math

def psnr(img1, img2):
    mse = np.mean(np.square(img1 - img2))
    if mse == 0:
        return 100
    PIXEL_MAX = 255.0
    return 10 * math.log10(PIXEL_MAX**2 / mse)

def SAE(a, b):
    '''
    calculate Sum of Absolute Errors of two images, divided by number of pixels
    :param a: image A, matrix
    :param b: image B, matrix
    '''
    result = np.sum(np.abs(np.subtract(a,b,dtype=np.float))) / (a.size)
    return result