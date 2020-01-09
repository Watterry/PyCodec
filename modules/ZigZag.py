import numpy as np

class ZigzagMatrix:
    # @param: a matrix of integers
    # @return: a list of integers
    def zig2Matrix(self, matrix):
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