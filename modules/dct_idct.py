import matplotlib.pyplot as plt
import numpy as np
from scipy.fftpack import fft, dct
import scipy

def img2dct(a):
    return scipy.fftpack.dct( scipy.fftpack.dct( a, axis=0, norm='ortho' ), axis=1, norm='ortho' )

def dct2img(a):
    return scipy.fftpack.idct( scipy.fftpack.idct( a, axis=0 , norm='ortho'), axis=1 , norm='ortho')

def dctUsingMatrix(X):
    print("The 1st Way: using matrix")
    A = np.array([[0.5, 0.5, 0.5, 0.5],
                [0.653, 0.271, -0.271, -0.653],
                [0.5, -0.5, -0.5, 0.5],
                [0.271, -0.653, 0.653, -0.271]])

    #first way, use formula Y=A.X.AT to generate DCT coefficients
    temp = np.dot(A, X)
    temp = np.round(temp, 1)
    Y = np.dot(temp, A.T)
    Y = np.round(Y, 1)

    #get inverse block data
    X_i = np.round(np.dot(np.dot(A.T, Y), A), 0)

    print(X)
    print('\n')
    print(temp)
    print('\n')
    print(Y)
    print('\n')
    print(X_i)
    print('\n')

# second way, use python dct function to generate DCT coefficients
def dctUsingScipy(X):
    print("The 2nd Way: using SciPy DCT")
    dct_python = np.round(img2dct(X), 1)
    #data for testing inverse DCT correctness
    # dct_python = np.array([[537.2, -76, -54.7, -7.8],
    #                        [-106.1, 35, -12.7, -6.1],
    #                        [-42.7, 46.5, 10.2, -9.8],
    #                        [-20.2, 12.9, 3.9, -8.5]])

    img_python = np.round(dct2img(dct_python), 0)

    print(X)
    print('\n')
    print(dct_python)
    print('\n')
    print(img_python)

def dct_iDct():
    #get a 4x4 block
    block = np.array([[126, 159, 178, 181],
                      [98, 151, 181, 181],
                      [80, 137, 176, 156],
                      [75, 114, 88, 68]])
    # another block data
    #block = np.array([[5, 11, 8, 10],
    #                  [9, 8, 4, 12],
    #                  [1, 10, 11, 4],
    #                  [19, 6, 15, 7]])

    dctUsingMatrix(block)

    dctUsingScipy(block)

if __name__ == "__main__":
    dct_iDct()