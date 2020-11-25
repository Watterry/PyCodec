# The coding and decoding of H.264 CAVLC
#
# Copyright (C) <2020>  <cookwhy@qq.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from bitstring import BitStream, BitArray
import ZigZag
import vlc
import logging

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
    enStr = ''
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
            elif (x!=0):
                remains = np.append(remains, x)
        else:
            #get remain non-zeros
            if (x!=0):
                remains = np.append(remains, x)

    #print(enStr)
    #print(remains)
    return enStr, remains

def encodeLevels(remains_1D, totalCoeffs, t1s):
    '''
    Encode the levels of the remaining non-zero coefficients
    The level, i.e. the sign and magnitude, of each remaining
    non-zero coefficient in the block is encoded in reverse order,
    Args:
        remains_1D: remain no-zeros values after encode T1s in reverse order
        totalCoeffs: the sum of non-zeros in original block matrix
        t1s: the number of trailing +/−1 values (T1) in the macroblock
    '''
    enStr = ''
    suffixLength = 0  #default value
    if totalCoeffs>10 and t1s<=3:
        suffixLength = 1

    for x in remains_1D:
        level = int(x)
        levelCode = level
        if (level>0):
            levelCode = (level<<1) - 2
        else:
            levelCode = 0 - (level<<1) - 1

        level_prefix = int(levelCode / (1 << suffixLength))
        level_suffix = int(levelCode % (1 << suffixLength))

        print("level %d, levelCode %d, levelPrefix %d, suffixLength %d" % (level, levelCode, level_prefix, suffixLength))
 
        # TODO: when level_prefix larger than 15, what should I do?
        if level_prefix>15:
            level_prefix = 15

        code = vlc.level_prefix[level_prefix]
        if (suffixLength != 0):
            temp = bin(level_suffix).replace('0b','')
            while len(temp) < suffixLength:
                temp = '0' + temp
            code = code + temp

        print("code: ", code)
        enStr = enStr + code

        #update suffixLength
        if (suffixLength == 0):
            suffixLength = suffixLength + 1
        elif (levelCode > (3 << (suffixLength -1)) and suffixLength < 6):
            suffixLength = suffixLength + 1
            print("levelCode %d suffixLength %d" % (levelCode, suffixLength))

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

def encodeRunBefore(block_1D, totalCoeffs, totalZeros):
    """
    Encode each run of zeros.
    The number of zeros preceding each non-zero coefficient (run before) is
    encoded in reverse order.
    Args:
        block_1D: 1D array, that's Reordered macroblock which is 4x4 matrix
        totalCoeffs: the sum of non-zero coefficients in the block
        totalZeros: the sum of all zeros
    """
    enStr = ''
    [cols] = block_1D.shape

    total_runBefore = 0
    total_coeff = totalCoeffs

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
                if block_1D[y]==0:
                    runBefore = runBefore+1
                else:
                    break

            # stop condition 1: there are no more zeros left to encode
            if total_runBefore==totalZeros:
                print("ZerosLeft = %d; run before = %d; no code required: no more zeros" % (zeroLeft, runBefore))
                break
            total_runBefore = total_runBefore + runBefore

            # stop condition 2: the final or lowest frequency non-zero coefficient.
            if i==0 or total_coeff==1:
                print("ZerosLeft = %d; run before = %d; No code required: last coefficient." % (zeroLeft, runBefore))
                break

            if zeroLeft>6:
                zeroLeft = 7

            code = vlc.run_before[runBefore][zeroLeft]
            enStr = enStr + code
            total_coeff = total_coeff - 1
            print("ZerosLeft = %d; run before = %d; code: %s" % (zeroLeft, runBefore, code))

    return enStr

def encode(block):
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

    #Step1: get TotalCoeffs& T1s
    totalCoeffs = getTotalCoeffs(res)
    print("TotalCoeffs: ", totalCoeffs)
    if (totalCoeffs==0):
        NoFurther = BitStream('0b0')
        print("CAVLC: ", NoFurther.bin)
        return NoFurther

    t1s = getT1s(res)
    print("T1s: ", t1s)
    part1 = '0b' + vlc.coeff_token[0][totalCoeffs][t1s]
    print("coeff token:", part1)

    #step2: Encode the sign of each T1
    part2, remains = encodeT1s(res, t1s)
    print("T1 sign:", part2)

    #step3: Encode the levels of the remaining non-zero coefficients
    part3 = encodeLevels(remains, totalCoeffs, t1s)
    print("encode Levels:", part3)

    #Step4: Encode the total number of zeros before the last coefficient
    totalZeros = getTotalZeros(res)
    print("TotalZeros: ", totalZeros)
    part4 = ''
    if ( totalCoeffs<block.size ):
        part4 = vlc.total_zeros[totalZeros][totalCoeffs]
    print("encode TotalZeros: ", part4)

    #step5: Encode each run of zeros
    part5 = encodeRunBefore(res, totalCoeffs, totalZeros)
    
    stream = BitStream()
    temp = part1 + part2 + part3 + part4 + part5
    stream.append(temp)

    logging.debug("CAVLC: %s", stream.bin)

    # supplement zero at the end of stream, so we can print the hex code of the stream
    output_str = stream
    addon = 8 - len(stream.bin) % 8
    for i in range(0, addon):
        output_str.append('0b0')
    logging.debug("CAVLC hex: %s", output_str.hex)

    return stream

def decode(stream, nC, maxNumCoeff=16):
    """
    decode pure cavlc stream
    Args:
        nC: the nC calculating from nA & nB on page 158
        maxNumCoeff: passed in by residual_block()
        stream: the binary data of current 4x4 macroblock
    
    Returns:
        4x4 block of coefficients after unzig-zag
        the postion of the stream after parser
        the TotalCoeff of this block
    """

    # step1: 9.2.1 Parsing process for total number of transform coefficient levels and trailing ones
    # on page 157 of [H.264 standard Book]
    total = 1
    TotalCoeff = -1
    TrailingOnes = -1

    table_i = vlc.get_nC_table_index(nC)
    while True:
        temp = stream.peek(total)
        result = np.where(vlc.coeff_token[table_i] == temp.bin)

        if len(result[0])==0:
            total = total + 1
        else:
            TotalCoeff = int(result[0])
            TrailingOnes = int(result[1])
            logging.debug('TotalCoeff: %d , TrailingOnes: %d ', TotalCoeff, TrailingOnes)
            break

    temp = stream.read(total) #drop the data
    #print(stream.pos)
    #print(stream.peek(8).bin)

    # step2: 9.2.2 Parsing process for level information
    # decode the trailing one transform coefficient levels
    level = np.zeros(maxNumCoeff)
    index = 0 # described as variable i on page 160
    for x in range(0, TrailingOnes):
        trailing_ones_sign_flag = stream.read(1).int
        if trailing_ones_sign_flag==0:
            level[x] = 1
        else:
            level[x] = -1
        index = index + 1

    logging.debug("coefficient levels: %s", level) 

    #print(stream.pos)
    #print(stream.peek(8).bin)

    #Following the decoding of the trailing one transform coefficient levels,
    
    # initialize suffixLength as follows
    suffixLength = -1
    if TotalCoeff>10 and TrailingOnes<3:
        suffixLength = 1
    else:
        suffixLength = 0
    logging.debug("init suffixLength: %d", suffixLength) 

    remaining_levels = TotalCoeff - TrailingOnes

    while remaining_levels>0:

        #decode the remaining levels
        level_prefix = 0
        level_suffix = 0
        levelSuffixSize = 0

        total = 1
        while True:
            #level_prefix is decoded using the VLC specified in Table 9-6
            temp = stream.peek(total)
            result = np.where(vlc.level_prefix == temp.bin)

            if len(result[0])==0:
                total = total + 1
            else:
                level_prefix = int(result[0])
                break
        
        stream.read(total) #drop the level_prefix data
        #logging.debug('level_prefix: %d ', level_prefix)

        if level_prefix==14 and suffixLength==0:
            levelSuffixSize = 4
        elif level_prefix==15:
            levelSuffixSize = 12
        else:
            levelSuffixSize = suffixLength

        if levelSuffixSize > 0:
            level_suffix = stream.read(levelSuffixSize).uint
        else:
            level_suffix = 0

        levelCode = (level_prefix << suffixLength) + level_suffix

        if level_prefix==15 and suffixLength==0:
            levelCode = levelCode + 15

        if index==TrailingOnes and TrailingOnes<3:
            levelCode = levelCode + 2
        
        if levelCode%2==0:
            level[index] = (levelCode+2)>>1
        else:
            level[index] = (-levelCode-1)>>1 

        if suffixLength==0:
            suffixLength = 1

        if ( abs(level[index]) > (3 << ( suffixLength-1 )) ) and (suffixLength<6):
            suffixLength = suffixLength + 1

        remaining_levels = remaining_levels - 1
        index = index + 1

    logging.debug("coefficient levels: %s", level) 

    #step3: 9.2.3 Parsing process for run information
    index = 0
    zerosLeft = 0
    total_zeros = 0
    
    logging.debug("decoding run information")
    #print(stream.pos)
    #print(stream.peek(4).bin)

    if TotalCoeff==maxNumCoeff:
        zerosLeft = 0
    else:
        #decode total_zeros
        if maxNumCoeff == 4:
            #chroma parseing talbe
            #get total zeros from table 9-9
            if TotalCoeff>0:
                #logging.debug('test: xxxxx')
                total = 1
                while True:
                    temp = stream.peek(total)
                    result = np.where(vlc.total_zeros_2x2[:, TotalCoeff] == temp.bin)

                    if len(result[0])==0:
                        total = total + 1
                    else:
                        total_zeros = int(result[0])
                        logging.debug('total_zeros: %d', total_zeros)
                        break

                stream.read(total) #drop the level_prefix data
                zerosLeft = total_zeros
        else:
            #get total zeros from table 9-7 & 9-8
            if TotalCoeff>0:
                total = 1
                while True:
                    temp = stream.peek(total)
                    result = np.where(vlc.total_zeros[:, TotalCoeff] == temp.bin)

                    if len(result[0])==0:
                        total = total + 1
                    else:
                        total_zeros = int(result[0])
                        logging.debug('total_zeros: %d', total_zeros)
                        break

                stream.read(total) #drop the level_prefix data
                zerosLeft = total_zeros

    remaining_runs = TotalCoeff - 1
    run = np.zeros(maxNumCoeff, int)
    while remaining_runs>0:
        if zerosLeft>0:
            
            if zerosLeft>6:
                zeros_index = 7
            else:
                zeros_index = zerosLeft
            
            total = 1
            while True:
                temp = stream.peek(total)
                result = np.where(vlc.run_before[:, zeros_index] == temp.bin)

                if len(result[0])==0:
                    total = total + 1
                else:
                    run_before = int(result[0])
                    run[index] = run_before
                
                    logging.debug('run_before: %d', run_before)
                    break

            stream.read(total) #drop the level_prefix data

        else:
            run[index] = 0
            logging.debug('run_before: %d', run[index])

        zerosLeft = zerosLeft - run[index]
        index = index + 1

        if zerosLeft<0:
            zerosLeft = 0

        remaining_runs = remaining_runs - 1

    logging.debug('run information: %s', run)

    coeffLevel = np.zeros(maxNumCoeff, int)
    i = TotalCoeff - 1
    coeffNum = total_zeros - run.sum() - 1  # a different from [H.264 standard Book] on page 162
    for x in range(0, TotalCoeff):
        coeffNum = coeffNum + run[i] + 1
        #print("coeffNum: %d, i: %d, totalZeros: %d" % (coeffNum, i, total_zeros))
        coeffLevel[coeffNum] = level[i]
        i = i - 1

    if maxNumCoeff==15:
        coeffLevel = np.insert(coeffLevel, 0, 0)
    logging.debug('coeffLevel: %s', coeffLevel)

    zig = ZigZag.ZigzagMatrix()
    logging.debug("ZiaZag scan:")
    matrix_x = 4
    if maxNumCoeff==15 or maxNumCoeff==16:
        matrix_x = 4
    else:
        matrix_x = 2

    block = zig.zig2matrix(coeffLevel, matrix_x, matrix_x)

    logging.debug('block: \n%s', block)
    logging.debug('stream position: %d', stream.pos)

    return block, stream.pos, TotalCoeff

def testEncode():
    # test = np.array([[0, 3, -1, 0],
    #                  [0, -1, 1, 0],
    #                  [1, 0, 0, 0],
    #                  [0, 0, 0, 0]])

    test = np.array([[-2, 4, 0, -1],
                     [3, 0, 0, 0],
                     [-3, 0, 0, 0],
                     [0, 0, 0, 0]])

    # test = np.array([[0, 0, 1, 0],
    #                  [0, 0, 0, 0],
    #                  [1, 0, 0, 0],
    #                  [-1, 0, 0, 0]])

    # test = np.array([[-12, 1, -10, -3],
    #                  [0, 0, 0, 0],
    #                  [0, 0, 0, 0],
    #                  [0, 0, 0, 0]])

    # test = np.array([[-1, -8, 8, -4],
    #                  [1, -1, 1, 1],
    #                  [4, -7, 5, -3],
    #                  [-1, 2, -1, 2]])

    # test = np.array([[-78, 4, 9, 2],
    #                  [3, -6, 1, -1],
    #                  [2, 1, 0, -1],
    #                  [2, 0, 0, 1]])

    print("Test data:")
    print(test)
    encode(test)

def testDecode():
    nC = 0

    # example 1 from [the Richardson Book] on page 214
    stream = BitStream('0b000010001110010111101101')
    logging.debug('decoding CAVLC stream: %s', stream.bin)
    decode(stream, nC, 16)

    # example 2 from [the Richardson Book] on page 215
    stream = BitStream('0b000000011010001001000010111001100')    
    logging.debug('decoding CAVLC stream: %s', stream.bin)
    decode(stream, nC, 16)

    # example 3 from [the Richardson Book] on page 216
    stream = BitStream('0b0001110001110010')
    logging.debug('decoding CAVLC stream: %s', stream.bin)
    decode(stream, nC, 16)

def testDecode_15():
    nC = 0
    # test data from an encoded H.264 keyframe's AC level
    stream = BitStream('0b1')
    logging.debug('decoding CAVLC stream: %s', stream.bin)
    decode(stream, nC, 15)

    # test data from an encoded H.264 keyframe's AC level
    stream = BitStream('0b010000110001')
    logging.debug('decoding CAVLC stream: %s', stream.bin)
    decode(stream, nC, 15)

    # test data from an encoded H.264 keyframe's AC level
    stream = BitStream('0b000111000110001')
    logging.debug('decoding CAVLC stream: %s', stream.bin)
    decode(stream, nC, 15)

    # test data from an encoded H.264 keyframe's AC level
    stream = BitStream('0b0101000100101011111001101000110110000110101110001')
    logging.debug('decoding CAVLC stream: %s', stream.bin)
    decode(stream, 1, 15)

def testDecode_4():
    nC = 0

    # test data from an encoded H.264 keyframe's AC level
    stream = BitStream('0b11101000010000110000')
    logging.debug('decoding CAVLC stream: %s', stream.bin)
    decode(stream, -1, 4)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("cavlc.log", mode='w'),
            logging.StreamHandler(),
        ]
    )

    #testEncode()
    #testDecode()

    #testDecode_15()
    testDecode_4()