# The coding and decoding of encoder
import numpy as np
import ZigZag

def getTotalCoeffs(block_1D):
    '''
    get non-zeros coefficients in a macroblock
    : param block: 1D array, that's Reordered macroblock which is 4x4 matrix
    '''
    total = 0
    for x in block_1D:
        if x!=0:
            total = total + 1

    return total

def getTotalZeros(block_1D):
    '''
    get zero coefficients in a macroblock
    TotalZeros is the sum of all zeros preceding the highest non-zero coefficient
    in the re-ordered array and is coded with a VLC.
    : param block: 1D array, that's Reordered macroblock which is 4x4 matrix
    '''
    
    [cols] = block_1D.shape

    pos = 0
    for i in range(cols):
        val = block_1D[i]
        if val!=0:
            pos = i

    total = 0
    for j in range(cols):
        if j > pos:
            break
    
        val = block_1D[j]
        if val==0:
            total = total + 1

    return total

if __name__ == "__main__":
    test = np.array([[0, 3, -1, 0],
                     [0, -1, 1, 0],
                     [1, 0, 0, 0],
                     [0, 0, 0, 0]])
    print("Test data:")
    print(test)

    #use Zigzag to scan
    zig = ZigZag.ZigzagMatrix()
    print("ZiaZag scan:")
    res = zig.matrix2zig(test)
    print(res)

    #get TotalCoeffs
    totalCoeffs = getTotalCoeffs(res)
    print("TotalCoeffs: ", totalCoeffs)

    #get TotalZeros
    totalZeros = getTotalZeros(res)
    print("TotalZeros: ", totalZeros)