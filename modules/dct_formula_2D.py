# use dct formula to do dct & idct calculation
import numpy as np
from scipy.fftpack import fft, dct
import scipy
import matplotlib.pyplot as plt
import matplotlib
import math
from numpy import r_
import tools
import logging

def block2dct(a):
    return scipy.fftpack.dct( scipy.fftpack.dct( a, axis=0, norm='ortho' ), axis=1, norm='ortho' )

def dct2block(a):
    return scipy.fftpack.idct( scipy.fftpack.idct( a, axis=0 , norm='ortho'), axis=1 , norm='ortho')

def normalization(data):
    _range = np.max(data) - np.min(data)
    return (data - np.min(data)) / _range

#show all the block in big image, with two margin within two block
# U is 4D array, which is N*N matrix's basis pattern
def showBasisPatternTogether(U, N=4):
    margin = 1 # margin pixel of the bigshow
    # key steps for normalization, must use mean as initialization
    mean = (np.max(U) - np.min(U))/2
    bigShow = np.full((N*N+margin*(N-1), N*N+margin*(N-1)), mean)

    for k in range(0, N):
        for j in range(0, N):
            row = k*N + k*margin
            column = j*N + j*margin
            for m in range(0, N):
                for n in range(0, N):
                    bigShow[row+m][column+n] = U[k][j][m][n]

    bigShow = normalization(bigShow)
    plt.figure()
    plt.imshow(bigShow, cmap='gray')
    plt.title( "%dx%d basis pattern block" % (N, N))
    plt.show()

def dct_detail(S, N = 4):
    # init basis prefix
    A = np.zeros(N)
    A[0] = np.sqrt(1/N)
    for k in range(1, N):
        A[k] = np.sqrt(2/N)
    
    #generate basis patterns
    U_1D = np.zeros((N, N))
    for k in range(0, N):
        for n in range(0, N):
            U_1D[k][n] = np.cos( (k*(2*n+1)/(2*N))*np.pi )
        U_1D[k] = np.round(U_1D[k] * A[k], 4)

    #use the reverse vector to get the kj of N*N block
    U = np.zeros((N, N, N, N))
    for k in range(0, N):
        for j in range(0, N):
            #calculate the k,j of N，N block
            temp = U_1D[k].reshape(N, 1) 
            U[k][j] = np.multiply(temp, U_1D[j])

    # show basis pattern
    #showBasisPatternTogether(U, N)

    T = np.zeros((N, N))
    
    # forward transform, calculate the expansion coefficients
    for k in range(0, N):
        for j in range(0, N):
            T[k][j] = np.multiply(U[k][j], S).sum()

    #print("\nthe expansion coefficients:")
    T = np.around(T, 4)
    #print(T)

    # inverse transform, calculate the S by coefficients & basis
    S_inverse = np.zeros([N, N])
    for k in range(0, 2):
        for j in range(0, 2):
            S_inverse = S_inverse + T[k][j]*U[k][j]
    #print("\nInverse Result:")
    #print(np.round(S_inverse,0))

    return T, S_inverse

def Img2DctUsingScipy(im, m):
    '''
    transform image to dct coefficients using my scipy embed functions
    : param im: image data, currently just support square which means image's width equals to height
    : param m: dct block size,should be width==height
    '''
    imsize = im.shape
    dct = np.zeros(imsize)
    for i in r_[:imsize[0]:m]:
        for j in r_[:imsize[1]:m]:
            dct[i:(i+m),j:(j+m)] = block2dct( im[i:(i+m),j:(j+m)] )
    return dct

def Dct2ImgUsingScipy(dct_im, m):
    '''
    get the inverse image of dct coefficients
    : param dct: dct image data, currently just support square which means dct's width equals to height
    : param m: dct block size,should be width==height
    '''
    imsize = dct_im.shape
    img_dct = np.zeros(imsize)
    for i in r_[:imsize[0]:m]:
        for j in r_[:imsize[1]:m]:
            img_dct[i:(i+m),j:(j+m)] = dct2block( dct_im[i:(i+m),j:(j+m)] )

    return np.round(img_dct, 0)

def Img2DctUsingDetail(im, m):
    '''
    transform image to dct coefficients using my own calculation
    : param im: image data, currently just support square which means image's width equals to height
    : param m: dct block size,should be width==height
    '''
    imsize = im.shape
    dct = np.zeros(imsize)
    img_dct = np.zeros(imsize)

    for i in r_[:imsize[0]:m]:
        for j in r_[:imsize[1]:m]:
            dct[i:(i+m),j:(j+m)], img_dct[i:(i+m),j:(j+m)] = dct_detail( im[i:(i+m),j:(j+m)], m )

    return dct, np.round(img_dct, 0)

def processCheck():
    # 4x4 block test data set
    # N = 4
    # S = np.array([[1, 2, 2, 0],
    #               [0, 1, 3, 1],
    #               [0, 1, 2, 1],
    #               [1, 2, 2, -1]])

    # real 8x8 image test data
    N = 8
    S = np.array([[182, 196, 199, 201, 203, 201, 199, 173],
                  [175, 180, 176, 142, 148, 152, 148, 120],
                  [148, 118, 123, 115, 114, 107, 108, 107],
                  [115, 110, 110, 112, 105, 109, 101, 100],
                  [104, 106, 106, 102, 104, 95, 98, 105],
                  [99, 115, 131, 104, 118, 86, 87, 133],
                  [112, 154, 154, 107, 140, 97, 88, 151],
                  [145, 158, 178, 123, 132, 140, 138, 133]])

    # random test data
    # N = 8   # axis of 1D vector
    # S = np.random.randint(0, 100, size=[N, N])
    
    print("\nTest 2D %dx%d matrix:" % (N, N))
    print(S)

    # calculate DCT patterns by formula
    temp, S_i = dct_detail(S, N)
    diff = tools.psnr(S, np.round(S_i))
    print("\nPSNR is: ", np.around(diff, 2))

    # check the coefficients by Scipy
    T_scipy = np.round(block2dct(S), 4)
    print("\nthe expansion coefficients using SciPy:")
    print(T_scipy)

    #something wrong with below calculation
    S_scipy = np.round(dct2block(T_scipy), 4)
    print("\nInverse Result using SciPy:")
    print(S_scipy)

def processWholeImage():
    im = plt.imread("lena2.tif").astype(float)
    print(im.shape)
    
    BLOCK_WIDTH = 8
    # using Scipy way
    dct = Img2DctUsingScipy(im, BLOCK_WIDTH)
    img_dct = Dct2ImgUsingScipy(dct, BLOCK_WIDTH)

    # using my own calculation way
    #dct, img_dct = ImgDctUsingDetail(im, BLOCK_WIDTH)

    plt.figure()
    plt.imshow(dct,cmap='gray',vmax = np.max(dct)*0.01,vmin = 0)
    plt.title( "8x8 DCTs of the image")

    plt.figure()
    plt.imshow( np.hstack( (im, img_dct) ) ,cmap='gray')
    plt.title("Comparison between original and DCT compressed images" )

    diff = tools.psnr(im, img_dct)
    print("\nPSNR is: ", np.around(diff, 2))

    plt.show()

def process4x4iDCT():
    # 4x4 block coefficients data set
    BLOCK_WIDTH = 4
    dct = np.array([[75, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0]])

    logging.debug("dct: %s", dct)

    idct = Dct2ImgUsingScipy(dct, BLOCK_WIDTH)

    logging.debug("idct: %s", idct)

    # scaling
    Vm0 = 13
    block = (idct * 13) * 2
    logging.debug("block: %s", block)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("dct_formula_2D.log", mode='w'),
            logging.StreamHandler(),
        ]
    )

    np.set_printoptions(suppress=True)

    # check the DCT and iDCT process
    #processCheck()

    # check the whole image DCT&iDCT process
    processWholeImage()

    #check a 4x4 block iDCT process
    process4x4iDCT()