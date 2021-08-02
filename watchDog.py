import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import *
import socket, json
import numpy as np
import cv2

rows = 2160
cols = 4096
count = 0
class LoggingEventHandler(FileSystemEventHandler):
    """Logs all the events captured."""

    def __init__(self, logger=None):
        super(LoggingEventHandler, self).__init__()

        self.logger = logger or logging.root

    def on_moved(self, event):
        super(LoggingEventHandler, self).on_moved(event)

        what = 'directory' if event.is_directory else 'file'
        self.logger.info("Moved %s: from %s to %s", what, event.src_path,
                         event.dest_path)

    def on_created(self, event):
        global count
        super(LoggingEventHandler, self).on_created(event)

        what = 'directory' if event.is_directory else 'file'
        self.logger.info("Created %s: %s", what, event.src_path)
        # if count % 2 == 1:
        #     time.sleep(1)
        #     t1 = time.time()
        #     image_array = np.fromfile(event.src_path, dtype = np.uint8)
        #     image_array = image_array.reshape(rows, cols)
        #     nparray_reshaped = cv2.cvtColor(image_array, cv2.COLOR_BAYER_RG2RGB)
        #     filename = event.src_path.split("/")[-1].split(".")[0]
        #     cv2.imwrite(f'/media/taoyuanipc1/disk/imgs/jpg/{filename}.jpg', nparray_reshaped)
        #     print('tansform time:', time.time()- t1)
        # count += 1
        # if count % 40 == 0 and count != 0:
        #     count = 0
        # print(event.src_path)
        # try:
        #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     sock.connect(('127.0.0.1', 8902))
        #     fileName = event.src_path
        #     fileName = fileName.replace("\\", "\\\\")
        #     # message = '{"message":"newFile", "fileName":"%s"}' % fileName
        #     message = fileName
        #     # print(message)
        #     sock.send(message.encode('UTF-8'))
        #     sock.close()

        # except socket.error as e:
        #     print("[ERROR] ", e)         


    def on_deleted(self, event):
        super(LoggingEventHandler, self).on_deleted(event)

        what = 'directory' if event.is_directory else 'file'
        self.logger.info("Deleted %s: %s", what, event.src_path)

    # def on_modified(self, event):
    #     super(LoggingEventHandler, self).on_modified(event)

    #     what = 'directory' if event.is_directory else 'file'
    #     self.logger.info("Modified %s: %s", what, event.src_path)

        # print(event.src_path)
        # try:
        #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     sock.connect(('127.0.0.1', 8902))
        #     fileName = event.src_path
        #     # fileName = fileName.replace("\\", "\\\\")
        #     # message = '{"message":"newFile", "fileName":"%s"}' % fileName
        #     message = fileName
        #     # print(message)
        #     sock.send(message.encode('UTF-8'))
        #     sock.close()

        # except socket.error as e:
        #     print("[ERROR] ", e)        


if __name__ == "__main__":
    print("=== watchDog is running ===")
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    # path = 'C:\\Users\\chris\\Desktop\\CS\\\Osense\\taoyuan\\watchDog\\8902'
    path = '/media/taoyuanipc1/disk/imgs/raw'
    # path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()