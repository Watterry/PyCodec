# The coding and decoding of encoder
import numpy as np
from bitstring import BitStream, BitArray
import ZigZag
import vlc

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

def getT1s(block_1D):
    '''
    get the number of trailing +/−1 values (T1) in a macroblock
    : param block: 1D array, that's Reordered macroblock which is 4x4 matrix
    '''
    total = 0
    for x in block_1D:
        if x==1:
            total = total + 1
        elif x == -1:
            total = total + 1

    if total > 3:
        total = 3
    return total

def encodeT1s(block_1D, total):
    '''
    For each trailing +/−1 T1 signalled by coeff token, 
    the sign is encoded with a single bit, 0 = +, 1 = −, 
    in reverse order, starting with the highest-frequency T1.
    : param block: 1D array, that's Reordered macroblock which is 4x4 matrix
    : param total: the max number of T1 needed to encode, never more than 3
    Returns:
        1. return encode str of T1s
        2. return levels which needed to be encoded in next step
    '''
    enStr = '0b'
    remains = np.array([], dtype=int)

    sum = 0
    for x in block_1D[::-1]:
        if (sum<total):
            if x==1:
                enStr = enStr + '0'
                sum = sum + 1
            elif x==-1:
                enStr = enStr + '1'
                sum = sum + 1
        else:
            #get remain non-zeros
            if (x!=0):
                remains = np.append(remains, x)

    #print(enStr)
    #print(remains)
    return enStr, remains

def encodeLevels(remains_1D, suffixLength_init):
    '''
    Encode the levels of the remaining non-zero coefficients
    The level, i.e. the sign and magnitude, of each remaining
    non-zero coefficient in the block is encoded in reverse order,
    Args:
        remains_1D: remain no-zeros values after encode T1s in reverse order
        suffixLength_init: suffixLength init value
    '''
    enStr = ''
    suffixLength = int(suffixLength_init)

    for level in remains_1D:
        #print("level:", level)
        levelCode = level
        if (level>0):
            levelCode = (level * 2) - 2
        else:
            levelCode = 0 - (level *2) - 1

        #print("levelCode:", levelCode)

        level_prefix = int(levelCode / (1 << suffixLength))
        level_suffix = int(levelCode % (1 << suffixLength))

        enStr = enStr + vlc.level_prefix[level_prefix]
        if (suffixLength != 0):
            enStr = enStr + bin(level_suffix).replace('0b','')

        #update suffixleng
        if (suffixLength == 0):
            suffixLength = suffixLength + 1
        elif (abs(level) > (3 << (suffixLength -1)) and suffixLength < 6):
            suffixLength = suffixLength + 1

    #print("encode Levels:", enStr)
    return enStr

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

    stream = BitStream()

    #Step1: get TotalCoeffs& T1s
    totalCoeffs = getTotalCoeffs(res)
    print("TotalCoeffs: ", totalCoeffs)
    t1s = getT1s(res)
    print("T1s: ", t1s)
    part1 = vlc.coeff_token[0][totalCoeffs][t1s]
    print("coeff token:", part1)
    stream.append(part1)

    #step2: Encode the sign of each T1
    enT1, remains = encodeT1s(res, t1s)
    stream.append(enT1)

    #step3: Encode the levels of the remaining non-zero coefficients
    SuffixLength = 0  #default value
    if totalCoeffs>10 and t1s<=1:
        SuffixLength = 1
    part3 = encodeLevels(remains, SuffixLength)
    print("encode Levels:", part3)

    #Step4: get TotalZeros
    totalZeros = getTotalZeros(res)
    part4 = vlc.total_zeros[totalZeros][totalCoeffs]
    print("TotalZeros: ", part4)

    print(stream)