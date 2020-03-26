# read yuv file using Python

from numpy import *
import logging
import matplotlib.pyplot as plt

screenLevels = 255.0

def yuv_import(filename, dims, numfrm, startfrm):  
    fp = open(filename,'rb')  
    blk_size = int(prod(dims) * 3 / 2)  
    fp.seek( blk_size*startfrm, 0)  

    Y = []
    U = []
    V = []
    logging.debug("Y width: %d", dims[0])
    logging.debug("Y height: %d", dims[1])

    d00 = dims[0]//2
    d01 = dims[1]//2
    logging.debug("UV width: %d", d00)
    logging.debug("VV width: %d", d01)

    Yt = zeros((dims[0],dims[1]),uint8,'C')
    Ut = zeros((d00,d01),uint8,'C')
    Vt = zeros((d00,d01),uint8,'C')
    
    for i in range(numfrm):
        for m in range(dims[0]):
            for n in range(dims[1]):
                #print m,n
                Yt[m,n]=ord(fp.read(1))
        for m in range(d00):
            for n in range(d01):
                Ut[m,n]=ord(fp.read(1))
        for m in range(d00):
            for n in range(d01):
                Vt[m,n]=ord(fp.read(1))
        Y=Y+[Yt]
        U=U+[Ut]
        V=V+[Vt]
    fp.close()
    return (Y,U,V)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("yuv.log", mode='w'),
            logging.StreamHandler(),
        ]
    )

    width = 512
    height = 512

    data = yuv_import('lena2.yuv', (height, width), 1, 0)
    YY = data[0][0]

    logging.debug(YY)
    logging.debug(YY.size)

    plt.figure()
    plt.imshow(YY, cmap='gray')
    plt.show()

