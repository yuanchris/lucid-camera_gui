import cv2
import numpy as np
import os
from datetime import datetime
PATH = '/media/taoyuanipc1/2TBDisk/test/raw/'
PATH2 = '/media/taoyuanipc1/sata2/test/raw/'

def rawToJpg(filename,path):
    fd = open(path+filename, 'rb')
    rows = 2160
    cols = 4096
    f = np.fromfile(fd, dtype=np.uint8,count=rows*cols)
    img = f.reshape(rows, cols)
    img = cv2.cvtColor(img, cv2.COLOR_BAYER_RG2RGB)
    img = img[::2,::2]
    fd.close()
    return img


name_list = os.listdir(PATH)
# name_list = os.listdir(PATH2)
# name_list = name_list + name_list_2
name_list.sort(reverse=False)
if len(name_list) == 0:
    print('no raw')
else:
    d = name_list[0][:8]
    #d = datetime.now().strftime(“%Y-%m-%d”)
    # out = cv2.VideoWriter('/home/taoyuanipc1/Desktop/{}.mp4'.format(d),cv2.VideoWriter_fourcc(*'MP4V'), 24, (2048,1080))
    for count,name in enumerate(name_list):
        os.remove(PATH + name)
        # if name > '20210827_18-33-25':
        #     try:
        #         img = rawToJpg(name,PATH)
        #         # cv2.imwrite('/media/taoyuanipc1/2TBDisk/test/jpg/'+name[:24]+'.jpg',img)
        #     except :
        #         # os.remove(‘/volume1/data/raw/’+name)
        #         try:
        #             img = rawToJpg(name,PATH2)
        #             # cv2.imwrite('/media/taoyuanipc1/2TBDisk/test/jpg/'+name[:24]+'.jpg',img)
        #         except :
        #             # os.remove(‘/volume1/data/raw/’+name)
        #             continue
            
        #     if count %100 == 0:
        #         print(name)
        #         #img = rawToJpg(name)
        #         now = datetime.now()
        #         current_time = now.strftime("%H:%M:%S")
        #         print('current {} finish {}/{}'.format(current_time, count, len(name_list)))
        #     if count == 4800:
        #         break
        #     out.write(img)
