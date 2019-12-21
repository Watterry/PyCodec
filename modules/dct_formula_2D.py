# use dct formula to do dct & idct calculation
import numpy as np
from scipy.fftpack import fft, dct
import scipy
import matplotlib.pyplot as plt

def img2dct(a):
    return scipy.fftpack.dct( scipy.fftpack.dct( a, axis=0, norm='ortho' ), axis=1, norm='ortho' )

def dct2img(a):
    return scipy.fftpack.idct( scipy.fftpack.idct( a, axis=0 , norm='ortho'), axis=1 , norm='ortho')

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
    print(U_1D)

    #use the reverse vector to get the kj of N*N block
    U = np.zeros((N, N, N, N))
    for k in range(0, N):
        for j in range(0, N):
            #calculate the k,j of N，N block
            
            print(U_1D[k].T)
            print(U_1D[j])
            U[k][j] = np.multiply(U_1D[k].T, U_1D[j])
            print(" Row %d, column %d" % (k, j))
            print(U[k][j])
            # plt.figure()
            # plt.imshow(U[k][j],cmap='gray')
            # plt.title( "An 4x4 coefficients block")

    T = np.zeros((N, N))
    
    # forward transform, calculate the expansion coefficients
    for k in range(0, N):
        for j in range(0, N):
            T[k][j] = np.multiply(U[k][j], S).sum()

    print("\nthe expansion coefficients:")
    print(T)

    # inverse transform, calculate the S by coefficients & basis
    S_inverse = np.zeros([N, N])
    for k in range(0, N):
        for j in range(0, N):
            S_inverse = S_inverse + T[k][j]*U[k][j]
    print("\nInverse Result:")
    print(np.round(S_inverse,0))

if __name__ == "__main__":
    # test data set
    N = 4
    S = np.array([[1, 2, 2, 0],
                  [0, 1, 3, 1],
                  [0, 1, 2, 1],
                  [1, 2, 2, -1]])

    # random test data
    # N = 8   # axis of 1D vector
    # S = np.random.randint(0, 100, size=[N])
    # print("\nTest 1D number vector:")
    # print(S)

    # calculate DCT patterns by formula
    dct_detail(S, N)

    # check the coefficients by Scipy
    T_scipy = np.round(img2dct(S), 4)
    print("\nthe expansion coefficients using SciPy:")
    print(T_scipy)

    #something wrong with below calculation
    S_scipy = np.round(dct2img(T_scipy), 4)
    print("\nInverse Result using SciPy:")
    print(S_scipy)