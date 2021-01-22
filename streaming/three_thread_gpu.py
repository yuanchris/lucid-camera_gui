import subprocess as sp
from cv2 import cv2
import time, os
import numpy as np
import threading
import queue  
import pickle

def readFile(img_q, name_q,middle_q):
    count = 0
    t1 = t2 = t3 = t4 = 0

    path = './raw'
    rows = 2160
    cols = 4096

    while True:

            if count % 90 == 0 and count != 0:
                print('\n name_q size:', name_q.qsize(),'middle_q: ',middle_q.qsize(),  'img_q size:', img_q.qsize())
                print('read: ',(t4 - t1) / count, (t2 - t1) / count, (t3 - t2) / count, (t4 - t3) / count)
                count = 0
                t1 = t2 = t3 = t4 = 0

            count += 1
            t1 += time.time()
            file = name_q.get()
            t2 += time.time()
            img = np.fromfile(path + '/' + file , dtype=np.uint8,count=rows*cols)
            t3 += time.time()
            
            middle_q.put(img)
            t4 += time.time()

def middle(img_q, name_q, middle_q):
    rows = 2160
    cols = 4096
    count = 0
    t1 = t2 = t3 = t4 = t5= 0

    while True:
        if count % 90 == 0 and count != 0:
            # print('\n name_q size:', name_q.qsize(),'middle_q: ',middle_q.qsize(),  'img_q size:', img_q.qsize())
            print('middle: ',(t5 - t1) / count, (t2 - t1) / count, (t3 - t2) / count, (t4 - t3) / count, (t5 - t4) / count)
            count = 0
            t1 = t2 = t3 = t4 = t5 = 0
        count += 1
        t1 += time.time()
        img = middle_q.get()
        t2 += time.time()
        img = img.reshape(rows, cols)
        img = cv2.cvtColor(img, cv2.COLOR_BAYER_RG2RGB)
        t3 += time.time()
        img = bytes(img)
        t4 += time.time()
        img_q.put(img)
        t5 += time.time()


def stream(img_q, name_q, middle_q):
    # rtmpUrl = "rtmp://live-tpe01.twitch.tv/app/live_610245024_Ke0rWhZaHj7UUOg10AqULR6uarFtCF"
    rtmpUrl = "rtmp://live-tpe01.twitch.tv/app/live_609869033_qAYmSs8oeMo1ZLJk9nU92kK2DDd4UY"

    # rtmpUrl = "rtmp://a.rtmp.youtube.com/live2/ss3h-9kkj-tm27-j0j4-4psf"
    fps = 30
    width = 2048*2
    height = 1080*2
    rows = 2160
    cols = 4096
    command = ['ffmpeg',
        '-y',
        '-hwaccel', 'cuvid',
        '-f', 'rawvideo',
        '-pix_fmt', 'bgr24',
        '-s', "{}x{}".format(width, height),
        '-r', str(fps),
        '-thread_queue_size', '1024',
        '-i', '-',
        '-stream_loop', '-1',
        '-thread_queue_size', '1024',
        '-i', 'peng.mp3',
        '-c:a', 'copy',
        '-c:v', 'h264_nvenc',
        '-pix_fmt', 'yuv420p',
        '-b:v', '20M',
        '-maxrate', '25M',
        '-bufsize', '10M',
        # '-b:v', '5.5M',
        # '-maxrate', '6M',
        # '-bufsize', '3M',
        # '-g', '5',
        '-f', 'flv', 
        rtmpUrl]
    p = sp.Popen(command, stdin=sp.PIPE)
    count = 0
    t1 = t2 = t3 = 0

    while True:
   
            if count % 90 == 0 and count != 0:
                # print('\n name_q size:', name_q.qsize(),'middle_q: ',middle_q.qsize(),  'img_q size:', img_q.qsize())
                print('stream: ',(t3 - t1) / count, (t2 - t1) / count, (t3 - t2) / count)
                count = 0
                t1 = t2 = t3 = 0

            count += 1
            t1 += time.time()
            img = img_q.get()
            t2 += time.time()
            p.stdin.write(img)
            t3 += time.time()
           



            


if __name__ == '__main__':
    img_q = queue.Queue(300)  
    name_q = queue.Queue(300) 
    middle_q = queue.Queue(300) 
    read_thread = threading.Thread(target=readFile, args = (img_q, name_q,middle_q,))
    middle_thread = threading.Thread(target=middle, args = (img_q, name_q, middle_q,))
    stream_thread = threading.Thread(target=stream, args = (img_q, name_q,middle_q,))

    read_thread.start()
    middle_thread.start()
    stream_thread.start()
    fp = open('./fns.pk','rb')
    names = pickle.load(fp)
    while True:
        for count,i in enumerate(names):
      
            start = time.time()
            name_q.put(i)
            mid = time.time()
            # if (mid-start) <= 0.001:
            time.sleep(0.02 - (mid-start))    
            end = time.time()
            if count % 180 == 29:
                # print('\n name_q size:', name_q.qsize(), 'middle_q size:', middle_q.qsize(), 'img_q size:', img_q.qsize(), '\n')
                print('main', mid-start, end - mid )
    # read_thread.join()
    # stream_thread.join()
    # python final.py