import numpy as np
from scipy.ndimage import label
import cv2, time,datetime

def my_gamma(I):
    I = cv2.resize(I, (500, 500))
    fI = I/255.0
    gamma = 0.5
    O = np.power(fI, gamma)
    O = O * 255
    return O

def segment_on_dt(a, img):
    border = cv2.dilate(img, None, iterations=4)
    border = border - cv2.erode(border, None)
    dt = cv2.distanceTransform(img, 2, 3)
    '''# 用plt查看图片，可以看出来具体变化
    plt.figure("距离场图片") 
    plt.imshow(dt,cmap ='gray')
    plt.show()'''
    dt = ((dt - dt.min()) / (dt.max() - dt.min()) * 255).astype(np.uint8)
    _, dt = cv2.threshold(dt, 180, 255, cv2.THRESH_BINARY)
    lbl, ncc = label(dt)
    lbl = lbl * (255 / (ncc + 1))
    lbl[border == 255] = 255
    lbl = lbl.astype(np.int32)
    cv2.watershed(a, lbl)
    lbl[lbl == -1] = 0
    lbl = lbl.astype(np.uint8)
    return 255 - lbl

def my_segment(img):
    # 重置图片大小，在后续的操作中，一些操作的范围是写死的，
    # 改不了了，如果图片大小不一样，操作得到的结果会不理想
    img = cv2.resize(img,(150,150)) 
    imgo = img.copy()
    imgo = cv2.cvtColor(imgo, cv2.COLOR_BGR2GRAY)   
    imgo = cv2.bitwise_not(imgo) # 黑底白字

    # 将汉字进行膨胀操作,这个膨胀迭代的次数，再程序中写死了
    # 要求我们拍的照片最终的大小在150*150左右，其中图片中的字，要求占大部分
    img = cv2.erode(img,None,iterations = 5)

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    
    _, img_bin = cv2.threshold(img_gray, 0, 255, cv2.THRESH_OTSU)
    img_bin = cv2.bitwise_not(img_bin)
    # 上面这个img_bin是黑底白字，而且是经过膨胀过的

    img_bin = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN,np.ones((3, 3), dtype=int))

    # img 3通道的膨胀后的白底黑字   img_bin 单通道的膨胀后的黑底白字
    result = segment_on_dt(img, img_bin)
    # 这个result图片 黑底，其他像素(0到255之间的一个值)的每一块代表一个字
    # 即有多少种不同于0和255的像素值，就有多少块区域
    return result




# the input image must be "heidbaizi"
def get_dst_rect(img):
    rows, cols = img.shape
    mymax = max(rows, cols)+1
    # rect is the distance_field matrix
    rect = img 
    # hanzi set 0, otherwise set mymax
    for i in range(0, rows):
        for ii in range(0, cols):
            if rect[i][ii] == 255:
                rect[i][ii] = 0
            else:
                rect[i][ii] = mymax
    # build index of image
    # by order of rows, row by row
    xx = []
    yy = []
    for i in range(0, rows):
        for ii in range(0, cols):
            xx.append(i)
            yy.append(ii)
    xx = np.array(xx)
    yy = np.array(yy)
    # build xx's & yy's index
    index2 = []
    for i in range(0, xx.size):
        index2.append(i)
    index2 = np.array(index2)
    ################### build distance's index
    ################### the first iterate is by the distance:[0->mymax)
    maxtmp = max(rows, cols)
    index = []
    for i in range(0, maxtmp):
        index.append(i)
    index = np.array(index)
    ################### start caculating
    for iii in index: # distance from 0 ~ mymax-1
        tmp = iii + 1 # for set distance in new pixel
        ddis = 0
        # equal to iterate all pixel in image by th order of "row by row"
        for i, ii, hh in zip(xx, yy, index2):
            mm = index2.size
            tmp2 = rect[i][ii]
            if tmp2 == iii:
                ddis += 1
                # iterate the around 8 points
                if hh-cols-1>=0 and hh-cols-1<mm and rect[xx[hh-cols-1]][yy[hh-cols-1]]>tmp2:
                    rect[xx[hh-cols-1]][yy[hh-cols-1]] = tmp 
                if hh-cols>=0 and hh-cols<mm and rect[xx[hh-cols]][yy[hh-cols]]>tmp2:
                    rect[xx[hh-cols]][yy[hh-cols]] = tmp 
                if hh-cols+1>=0 and hh-cols+1<mm and rect[xx[hh-cols+1]][yy[hh-cols+1]]>tmp2:
                    rect[xx[hh-cols+1]][yy[hh-cols+1]] = tmp 
                if hh-1>=0 and hh-1<mm and rect[xx[hh-1]][yy[hh-1]]>tmp2:
                    rect[xx[hh-1]][yy[hh-1]] = tmp 
                if hh+1>=0 and hh+1<mm and rect[xx[hh+1]][yy[hh+1]]>tmp2:
                    rect[xx[hh+1]][yy[hh+1]] = tmp 
                if hh+cols-1>=0 and hh+cols-1<mm and rect[xx[hh+cols-1]][yy[hh+cols-1]]>tmp2:
                    rect[xx[hh+cols-1]][yy[hh+cols-1]] = tmp 
                if hh+cols>=0 and hh+cols<mm and rect[xx[hh+cols]][yy[hh+cols]]>tmp2:
                    rect[xx[hh+cols]][yy[hh+cols]] = tmp 
                if hh+cols+1>=0 and hh+cols+1<mm and rect[xx[hh+cols+1]][yy[hh+cols+1]]>tmp2:
                    rect[xx[hh+cols+1]][yy[hh+cols+1]] = tmp 
        if ddis==0:
            break
    return rect

def my_distance(img):
    np.set_printoptions(threshold=np.inf)
    #img = cv2.imread("./origin3.png", 0)
    img = cv2.resize(img, (100, 100))
    rows, cols = img.shape
    rer, img = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)
    img = cv2.bitwise_not(img)
  #  plt.figure("Image0")
   # plt.imshow(img,cmap="gray")

    rect = get_dst_rect(img)
    return rect

def my_binary(I, ratio=0.15):
    winSize = (155,155)
    # 缺省的borderType时BORDER_REFLECT_101
    # 缺省normalize是True, 均值滤波必须正则化，otherwise是叫方框滤波
    # 正则化是将卷积点除kernel的长*宽
    I_mean = cv2.boxFilter(I, cv2.CV_32FC1, winSize)
            #, normalize=False)
            #, borderType=cv2.BORDER_REFLECT_101)
    out = I - (1.0 - ratio) * I_mean
    out[out>=0] = 255
    out[out<0] = 0
    out = out.astype(np.uint8)
    return out
