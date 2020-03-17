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
    enStr = '0b'
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

    Args:
        block_1D: 1D array, that's Reordered macroblock which is 4x4 matrix
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

def encodeRunBefore(block_1D, totalZeros):
    """
    Encode each run of zeros.
    The number of zeros preceding each non-zero coefficient (run before) is
    encoded in reverse order.
    Args:
        block_1D: 1D array, that's Reordered macroblock which is 4x4 matrix
        totalZeros: the sum of all zeros
    """
    enStr = '0b'
    [cols] = block_1D.shape

    total_runBefore = 0

    for i in range(cols-1, -1, -1):
        val = block_1D[i]

        if val!=0:
            zeroLeft = 0
            for x in range(i):
                temp = block_1D[x]
                if temp==0:
                    zeroLeft = zeroLeft+1

            runBefore = 0
            for y in range(i-1, -1, -1):
                print("y %d i %d" % (y,i))
                if block_1D[y]==0:
                    runBefore = runBefore+1
                else:
                    break

            # stop condition 1: there are no more zeros left to encode
            if total_runBefore== totalZeros:
                print("ZerosLeft = %d; run before = %d; no code required: no more zeros" % (zeroLeft, runBefore))
                break
            total_runBefore = total_runBefore + runBefore

            # stop condition 2: the final or lowest frequency non-zero coefficient.
            if i==0:
                print("ZerosLeft = %d; run before = %d; No code required: last coefficient." % (zeroLeft, runBefore))
                break

            if zeroLeft>6:
                zeroLeft = 7

            code = vlc.run_before[runBefore][zeroLeft]
            enStr = enStr + code
            print("ZerosLeft = %d; run before = %d; code: %s" % (zeroLeft, runBefore, code))

    return enStr

def CAVLC(block):
    """
    Entropy of CAVLC
    Args:
        block: input macroblock, should be 4x4 intger matrix
    returns:
        A bitstream of CAVLC code
    """
    #use Zigzag to scan
    zig = ZigZag.ZigzagMatrix()
    print("ZiaZag scan:")
    res = zig.matrix2zig(block)
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
    part2, remains = encodeT1s(res, t1s)
    print("T1 sign:", part2)
    stream.append(part2)

    #step3: Encode the levels of the remaining non-zero coefficients
    SuffixLength = 0  #default value
    if totalCoeffs>10 and t1s<=1:
        SuffixLength = 1
    part3 = encodeLevels(remains, SuffixLength)
    print("encode Levels:", part3)
    stream.append(part3)

    #Step4: Encode the total number of zeros before the last coefficient
    totalZeros = getTotalZeros(res)
    part4 = '0b' + vlc.total_zeros[totalZeros][totalCoeffs]
    print("TotalZeros: ", totalZeros)
    print("encode TotalZeros: ", part4)
    stream.append(part4)

    #step5: Encode each run of zeros
    part5 = encodeRunBefore(res, totalZeros)
    stream.append(part5)

    print("CAVLC: ", stream.bin)

if __name__ == "__main__":
    # test = np.array([[0, 3, -1, 0],
    #                  [0, -1, 1, 0],
    #                  [1, 0, 0, 0],
    #                  [0, 0, 0, 0]])

    test = np.array([[-2, 4, 0, -1],
                     [3, 0, 0, 0],
                     [-3, 0, 0, 0],
                     [0, 0, 0, 0]])

    print("Test data:")
    print(test)
    CAVLC(test)