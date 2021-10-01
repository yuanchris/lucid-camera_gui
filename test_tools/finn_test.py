import cv2 , os
import numpy as np
import time
import sys
# PATH = '/media/taoyuanipc1/disk/imgs/raw/'
# PATH = '/home/taoyuanipc1/Desktop/image_test/raw/'
PATH = '/media/taoyuanipc1/{}/test/raw/'.format(sys.argv[1])
def raw2jpg(filename):
    a = time.time()
    fd = open(PATH+filename, 'rb')
    rows = 1080
    cols = 2048
    num = 1
    f = np.fromfile(fd, dtype=np.uint8,count=rows*cols*num)
    b = time.time() 
    img = f.reshape(num,rows, cols)
    c = time.time()
    # img = cv2.cvtColor(img, cv2.COLOR_BAYER_RG2RGB)
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    d = time.time()
    fd.close()
    return b-a , c-b, d-c
    # return img
old_l = 0
fps = 50
while True:
    raw_list = os.listdir(PATH)
    # raw_list.sort()
    l = len(raw_list)
    print('len:',l)
    if old_l == l:
        break
    old_l = l
    total = 0
    total2 = 0
    total3 = 0
    max = 0
    for c,i in  enumerate(raw_list):
        st = time.time()
        t_a,t_b,t_c = raw2jpg(i)
        # img = cv2.imread(PATH + i)
        t = 0
        e = time.time() 
        a = e - st
        if a < 1/fps:
            time.sleep(1/fps - a)
        # else:
        if a > 1/fps:
            print('cost {} ,read use {}'.format(round(a,5), round(t,5)))
        total += e - st
        total2 += e - st
        total3 += e- st
        if e - st > max:
            max = e-st
        if c % 10 ==9:
            if c % 100 == 99:
                # print(t_a,t_b,t_c)
                # print(c+1,'all bias',total3 - (c+1)*0.005,'max',max)
                print('running {}/{} use {} max {}'.format(c+1,l, total2,max))
                # if total2 > 100/fps:
                #     print('100 times cost time :{} , {}'.format(total2,round(t,5)))
                total2 = 0
            # if total > 10/fps:
            #     print('10 times cost time :{} , {}'.format(total,round(t,5)))
            total = 0


