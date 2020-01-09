import numpy as np

class ZigzagMatrix:
    # @param: a matrix of integers
    # @return: a list of integers
    def zig2matrix(self, matrix):
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

    def matrix2zig(self, zig, m, n):
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

if __name__ == "__main__":
    #test code for ZigZag
    zig = ZigzagMatrix()
    test = np.array([[1, 2, 3, 4, 5, 6],
                     [7, 8, 9, 10, 11, 12],
                     [13, 14, 15, 16, 17, 18]])
    print("Test data:")
    print(test)

    print("ZiaZag transform:")
    res = zig.zig2matrix(test)
    print(res)

    print("Inverse ZiaZag")
    mat = zig.matrix2zig(res, test.shape[0], test.shape[1])
    print(mat)