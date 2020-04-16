import numpy as np
import zlib
import sys

class ZigzagMatrix:
    # @param: a matrix of integers
    # @return: a list of integers
    def matrix2zig(self, matrix):
        i = 0
        j = 0
        m = len(matrix)
        n = len(matrix[0])
        ret = np.zeros(m*n)

        up = True
        for index in range(m*n):
            #ret.append(matrix[i][j])
            ret[index] = matrix[i][j]
            if up:
                if i-1<0 or j+1>=n:
                    up = False
                    if j+1>=n:  # go down
                        i += 1
                    else:  # go right
                        j += 1
                else:
                    i -= 1
                    j += 1
            else:
                if i+1>=m or j-1<0:
                    up = True
                    if i+1>=m:
                        j += 1  # go right
                    else:
                        i += 1  # go up
                else:
                    i += 1
                    j -= 1

        return ret

    def zig2matrix(self, zig, m, n):
        i = 0
        j = 0
        matrix = np.zeros((m,n))

        up = True
        for index in range(m*n):
            matrix[i][j] = zig[index]
            if up:
                if i-1<0 or j+1>=n:
                    up = False
                    if j+1>=n:  # go down
                        i += 1
                    else:  # go right
                        j += 1
                else:
                    i -= 1
                    j += 1
            else:
                if i+1>=m or j-1<0:
                    up = True
                    if i+1>=m:
                        j += 1  # go right
                    else:
                        i += 1  # go up
                else:
                    i += 1
                    j -= 1

        return matrix

def Compress(matrix, QPstep):
    '''
    do the ZigZag re-arrange and quantization of an matrix, and compress it using zlib
    : param matrix: input numpy data, can be array or matrix
    : param step: quantization step, a setting of 0&1 will produce lossless output.
    '''
    qp = 1
    if QPstep > 0:
        qp = QPstep

    # step1: transform to Zigzag
    zig = ZigzagMatrix()
    data_1D = zig.matrix2zig( matrix )

    # step2: quantilization
    quantizer = np.round( data_1D / qp )

    # step3: zlib compression
    compressed = zlib.compress(quantizer)

    return compressed

def UnCompress(binary, QPstep, m, n):
    '''
    Undo the zlib compression, quantization, ZigZag process
    : param binary: the binary data compressed by zlib
    : param step: quantization step before zlib
    : param m: the width of the image
    : param n: the height of the image
    '''
    qp = 1
    if QPstep > 0:
        qp = QPstep

    # step1: unzip
    temp = np.fromstring(zlib.decompress(binary), 'float64')

    # step2: inverse quantization
    data_1D = temp * qp

    # step3: unzigzag to matrix
    zig = ZigzagMatrix()
    matrix = zig.zig2matrix(data_1D, m, n)

    return matrix

def testZigzag(test):
    #test code for ZigZag
    zig = ZigzagMatrix()

    print("Test data:")
    print(test)

    print("ZiaZag transform:")
    res = zig.matrix2zig(test)
    print(res)

    print("Inverse ZiaZag:")
    mat = zig.zig2matrix(res, test.shape[0], test.shape[1])
    print(mat)

    print("check diff:")
    print(test-mat)  # the result should be zero

def testZlibCompressWithZigzag(test):
    # test for zlib with Zigzag

    print("Test data:")
    print(test)
    zlibstream = Compress(test, 1)
    unzipMatrix = UnCompress(zlibstream, 1, test.shape[0], test.shape[1])

    print("check diff:")
    print(unzipMatrix)
    print(test-unzipMatrix)  # the result should be zero

if __name__ == "__main__":

    # test = np.array([[1, 2, 3, 4, 5, 6],
    #                  [7, 8, 9, 10, 11, 12],
    #                  [13, 14, 15, 16, 17, 18]])

    # test = np.array([[1, 2, 3, 4],
    #                  [5, 6, 7, 8],
    #                  [9, 10, 11, 12],
    #                  [13, 14, 15, 16]])

    test = np.array([[0, 0],
                     [0, 0]
                    ])

    testZigzag(test)

    #testZlibCompressWithZigzag(test)

