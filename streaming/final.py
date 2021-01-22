import subprocess as sp
from cv2 import cv2
import time, os
import numpy as np
import threading
import queue  
import pickle

def readFile(img_q, name_q):
    count = 0
    t1 = t2 = t3 = t4 = t5= 0

    path = './imgs'
    rows = 2160
    cols = 4096

    while True:

            if count % 90 == 0 and count != 0:
                print('img_q size:', img_q.qsize(), '\n name_q size:', name_q.qsize())
                print('read: ',(t5 - t1) / count, (t2 - t1) / count, (t3 - t2) / count, (t4 - t3) / count, (t5 - t4) / count)
                count = 0
                t1 = t2 = t3 = t4 = t5 = 0
       
            count += 1
            t1 += time.time()

            file = name_q.get()
            

            t2 += time.time()
            img = np.fromfile(path + '/' + file , dtype=np.uint8,count=rows*cols)
            t3 += time.time()
            img = img.reshape(rows, cols)
            img = cv2.cvtColor(img, cv2.COLOR_BAYER_RG2RGB)
            t4 += time.time()

            img_q.put(img)
            t5 += time.time()


def stream(img_q, name_q):
    rtmpUrl = "rtmp://live-tpe01.twitch.tv/app/live_609869033_qAYmSs8oeMo1ZLJk9nU92kK2DDd4UY"
    # rtmpUrl = "rtmp://live-tpe01.twitch.tv/app/live_609869033_qAYmSs8oeMo1ZLJk9nU92kK2DDd4UY"
    # rtmpUrl = "rtmp://a.rtmp.youtube.com/live2/ss3h-9kkj-tm27-j0j4-4psf"
    fps = 30
    width = 2048*2
    height = 1080*2
    rows = 2160
    cols = 4096
    command = ['ffmpeg',
        '-y',
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
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'ultrafast',
        # '-b:v', '20M',
        # '-maxrate', '25M',
        # '-bufsize', '10M',
        '-b:v', '5.5M',
        '-maxrate', '6M',
        '-bufsize', '3M',
        # '-g', '5',
        '-f', 'flv', 
        rtmpUrl]
    p = sp.Popen(command, stdin=sp.PIPE)

    count = 0
    t1 = t2 = t3 = t4 = t5 = 0

    while True:
   
            if count % 90 == 0 and count != 0:
                    # print(img)
                    print('img_q size:', img_q.qsize(), 'name_q size:', name_q.qsize())
                    print('stream: ', (t5 - t1) / count, (t2 - t1) / count, (t3 - t2) / count, (t4 - t3) / count, (t5 - t4) / count)
                    count = 0
                    t1 = t2 = t3 = t4= t5 = 0
            count += 1
            t1 += time.time()
            img = img_q.get()
            

            t2 += time.time()
            
            

            t3 += time.time()
            img = bytes(img)
            t4 += time.time()
            p.stdin.write(img)
            t5 += time.time()
            


if __name__ == '__main__':
    img_q = queue.Queue(100)  
    name_q = queue.Queue(100) 

    read_thread = threading.Thread(target=readFile, args = (img_q, name_q,))
    stream_thread = threading.Thread(target=stream, args = (img_q, name_q,))

    read_thread.start()
    stream_thread.start()
    fp = open('./fns.pk','rb')
    names = pickle.load(fp)
    while True:
  
        for count,i in enumerate(names):
            
            start = time.time()

            name_q.put(i)

            mid = time.time()

            if (mid-start) <= 0.01:
                time.sleep(0.025 - (mid-start))    
            end = time.time()
             
            # if count % 60 == 29:
            #     # print('\n count:', count, '\n')
            #     print('name_q size:', name_q.qsize(), 'img_q size:', img_q.qsize())
            #     print('\n main', mid-start, end - start )
    # read_thread.join()
    # stream_thread.join()
    # python final.py