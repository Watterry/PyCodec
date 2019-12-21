# use dct formula to do dct & idct calculation
import numpy as np
from scipy.fftpack import fft, dct
import scipy

def dct_detail(S, N = 4):
    # init basis prefix
    A = np.zeros(N)
    A[0] = np.sqrt(1/N)
    for k in range(1, N):
        A[k] = np.sqrt(2/N)
    
    #generate basis patterns
    U = np.zeros((N, N))
    for k in range(0, N):
        for n in range(0, N):
            U[k][n] = np.cos( (k*(2*n+1)/(2*N))*np.pi )
        U[k] = np.round(U[k] * A[k], 4)

    print("basis patterns:\n")
    print(U)

    T = np.zeros(N)
    
    # forward transform, calculate the expansion coefficients
    for k in range(0, N):
        # the 1st way to calculate the inner product
        #t[k] = np.inner(U[k], S)
        # the 2nd way to calculate the inner product
        T[k] = sum(U[k][:]*S[:])

    print("\nthe expansion coefficients:")
    print(T)

    # inverse transform, calculate the S by coefficients & basis
    S_inverse = np.zeros(N)
    for k in range(0, N):
        S_inverse = S_inverse + T[k]*U[k]
    print("\nInverse Result:")
    print(np.round(S_inverse,0))

if __name__ == "__main__":
    # test data set
    N = 4
    S = np.array([2, 4, 5, 3])

    # random test data
    # N = 8   # axis of 1D vector
    # S = np.random.randint(0, 100, size=[N])
    # print("\nTest 1D number vector:")
    # print(S)

    # calculate DCT patterns by formula
    dct_detail(S, N)

    # check the coefficients by Scipy
    T_scipy = scipy.fftpack.dct( S, axis=0, norm='ortho' )
    print("\nthe expansion coefficients using SciPy:")
    print(T_scipy)
    S_scipy = scipy.fftpack.idct( T_scipy, axis=0 , norm='ortho')
    print("\nInverse Result using SciPy:")
    print(S_scipy)