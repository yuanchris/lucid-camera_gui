import socket, sys, json
import asyncio
import websockets
import threading, time
import os
import random
from datetime import datetime
from pathlib import Path

import cv2  # pip install opencv-python
import numpy as np  # pip install numpy
import multiprocessing
from arena_api.__future__.save import Recorder
from arena_api.buffer import BufferFactory
from arena_api.system import system
from arena_api.enums import PixelFormat

import datetime
import base64
from PIL import Image as PIL_Image  # pip install Pillow
# from my_camera import streaming
class lucid_camera:
    def __init__(self):
        self.getImages_is_running = False
        self.preview_is_running = False
        self.change_flag = False

        self.server_socket = None
        self.preview_socket = None

        self.getImages_thread = None
        self.preview_process = None

        # camera parameters 
        self.camera_width = 4096
        self.camera_height = 2160
        self.gain = 0.0
        self.exposure_time = 90000.0

        self.exposure_time_max = 0.0
        self.exposure_time_min = 0.0
        self.fps = 0.0
        


    def run(self):
        print("===============camera Started=================")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)  # reuse tcp
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # reuse tcp, python3.6 cannot use reuseport
        self.server_socket.bind(('127.0.0.1', 8060))
        self.server_socket.listen(5)
        print("[*] Server Listening on %s:%d " % ('127.0.0.1', 8060))

        while True:
            csock, addr = self.server_socket.accept()
            csock.settimeout(5)
            print('Connected by ', addr, 'in 8060')
            try:
                msg = csock.recv(1024)
                receive_dict = msg.decode("utf-8")
                receive_dict = json.loads(receive_dict)
                if receive_dict["message"] == 'start_camera':
                    self.preview_is_running = False
                    if self.getImages_is_running:
                        print('camerea is already started')
                        data_to_send = dict()
                        data_to_send["success"] = True
                        data_to_send["fps"] = self.fps
                        csock.send(json.dumps(data_to_send).encode('utf-8'))
                    else:
                        print('Start camera')
                        self.getImages_is_running = True
                        
                        # getImages_thread = multiprocessing.Process(target=self.start_getImages_thread)
                        self.getImages_thread = threading.Thread(target=self.start_getImages_thread)
                        self.getImages_thread.start()

                        time.sleep(2)
                        data_to_send = dict()
                        data_to_send["success"] = True
                        data_to_send["data"] = {'fps': self.fps, 
                            'exposure_time': self.exposure_time,
                            'exposure_time_max': self.exposure_time_max, 
                            'exposure_time_min': self.exposure_time_min, 
                            'gain': self.gain,
                            }
                        csock.send(json.dumps(data_to_send).encode('utf-8'))


                elif receive_dict["message"] == 'stop_camera':
                    print('Stop camera')
                    self.getImages_is_running = False
                    self.preview_is_running = False
                    print('getimages_thread is closed')
                    data_to_send = dict()
                    data_to_send["success"] = True
                    csock.send(json.dumps(data_to_send).encode('utf-8'))

                elif receive_dict["message"] == 'start_preview':
                    self.getImages_is_running = False
                    self.preview_is_running = True

                    # self.preview_process = multiprocessing.Process(target=self.start_preview_process)

                    self.preview_process = threading.Thread(target=self.start_preview_process)
                    self.preview_process.start()

                    time.sleep(3)
                    data_to_send = dict()
                    data_to_send["success"] = True
                    data_to_send["data"] = {'fps': self.fps, 
                        'exposure_time': self.exposure_time,
                        'exposure_time_max': self.exposure_time_max, 
                        'exposure_time_min': self.exposure_time_min, 
                        'gain': self.gain,
                        }
                    csock.send(json.dumps(data_to_send).encode('utf-8'))

                elif receive_dict["message"] == 'submit_change':
                    self.change_flag = True

                    print(receive_dict['data'])
                    data = receive_dict['data']
                    self.camera_width = int(data['camera_width'])
                    self.camera_height = int(data['camera_height'])
                    self.gain = float(data['gain'])
                    self.exposure_time = float(data['exposure_time'])



                    data_to_send = dict()
                    data_to_send["success"] = True
                    csock.send(json.dumps(data_to_send).encode('utf-8'))

                else:
                    data_to_send = dict()
                    data_to_send["success"] = False
                    csock.send("fail".encode('utf-8'))
                
            except ConnectionResetError as e:
                print("#main_system socket encounter error :", e)

        csock.close()
    
    def start_getImages_thread(self):
        print('start_get_images_thread')
        devices = self.create_devices_with_tries()
        device = devices[0]
        print(device)

        # ====================== setting  ===========================================================
        # Nodes Height Width
        self.set_pixel(device, self.camera_width , self.camera_height)
        print('width height:',device.nodemap['Width'].value, device.nodemap['Height'].value)

        device.nodemap['PixelFormat'].value = PixelFormat.BayerRG8
        device.nodemap['ADCBitDepth'].value = 'Bits8'
        # print(nodemap['ADCBitDepth'])

        # FPS
        # self.set_fps(device, device.nodemap['AcquisitionFrameRate'].max)
        self.set_fps(device, 20.0)

        print('fps max', device.nodemap['AcquisitionFrameRate'].max)
        print('fps',  device.nodemap['AcquisitionFrameRate'].value)
        
        # Exposure Time and Gain
        self.set_exposure_time(device, self.exposure_time)
        print(f'''Exposure Time : {device.nodemap['ExposureTime'].value}''')

        self.set_gain(device, self.gain)
        print(f'''gain: {device.nodemap['Gain'].value}''')

        # ========================================================================
        with device.start_stream(2):
            count = 0
            t1 = t2 = t3 = t4 = 0
            interval = 40
            while self.getImages_is_running:
                if self.change_flag:
                    self.set_exposure_time(device, self.exposure_time)
                    self.set_gain(device, self.gain)
                    self.change_flag = False
            
                count += 1
                t1 += time.time()

                image_buffer = device.get_buffer()
                nparray_reshaped = np.ctypeslib.as_array(image_buffer.pdata,shape=(image_buffer.height, image_buffer.width, int(image_buffer.bits_per_pixel / 8)))
                t2 += time.time()
                # ====  save file ======
                path_time = self.time_update_function()
                # path_time = f'file_{count}'
                nparray_reshaped.tofile(f'/media/taoyuanipc1/disk/imgs/raw/{path_time}.raw')
                # nparray_reshaped.tofile(f'imgs/raw/{path_time}.raw')

                # nparray_reshaped = cv2.cvtColor(nparray_reshaped, cv2.COLOR_BAYER_RG2RGB)
                # if count % 4 == 1:
                #     cv2.imwrite(f'/media/taoyuanipc1/disk/imgs/jpg/{path_time}.jpg', nparray_reshaped)


                t3 += time.time()
                #==== show =======
                # frame = cv2.cvtColor(nparray_reshaped, cv2.COLOR_BGR2RGB)
                # frame = cv2.resize(nparray_reshaped,(1024, 540))
                # cv2.imshow('preview', frame)
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break
                
                device.requeue_buffer(image_buffer)
                t4 += time.time()
                if count % interval == 0 and count != 0:
                    print('total time:',(t4-t1) / interval)
                    print('time:',(t2-t1)/interval, (t3-t2)/interval, (t4-t3)/interval)
                    count = t1 = t2 = t3 = t4 = 0 
            # cv2.destroyAllWindows()

        system.destroy_device()
        print('finished get_images')
    
    def start_preview_process(self):
        print('start_preview_process')
        async def preview_func(websocket,path):
            devices = self.create_devices_with_tries()
            device = devices[0]
            print(device)

            # ====================== setting  ===========================================================
            # Nodes Height Width
            self.set_pixel(device, self.camera_width , self.camera_height)
            print('width height:',device.nodemap['Width'].value, device.nodemap['Height'].value)

            device.nodemap['PixelFormat'].value = PixelFormat.BayerRG8
            device.nodemap['ADCBitDepth'].value = 'Bits8'
            print('ADCBitDepth:', device.nodemap['ADCBitDepth'])

            # FPS
            self.set_fps(device, device.nodemap['AcquisitionFrameRate'].max)
            print('fps max', device.nodemap['AcquisitionFrameRate'].max)
            print('fps',  device.nodemap['AcquisitionFrameRate'].value)
            
            # Exposure Time and Gain
            self.set_exposure_time(device, self.exposure_time)
            print(f'''Exposure Time : {device.nodemap['ExposureTime'].value}''')
            self.set_gain(device, self.gain)
            print(f'''gain: {device.nodemap['Gain'].value}''')
            # ========================================================================
            with device.start_stream(2):
                count = 0
                t1 = t2 = t3 = t4 = 0
                interval = 40
                while self.preview_is_running:
                    if self.change_flag:
                        # self.set_pixel(device, self.camera_width , self.camera_height)
                        self.set_exposure_time(device, self.exposure_time)
                        self.set_gain(device, self.gain)
                        self.change_flag = False
    
                    count += 1
                    t1 += time.time()

                    image_buffer = device.get_buffer()
                    nparray_reshaped = np.ctypeslib.as_array(image_buffer.pdata,shape=(image_buffer.height, image_buffer.width, int(image_buffer.bits_per_pixel / 8)))
                    t2 += time.time()
                    # ====  save file ======
                    path_time = self.time_update_function()
                    # path_time = f'file_{count}'
                    # nparray_reshaped.tofile(f'/media/taoyuanipc1/disk/imgs/raw/{path_time}.raw')

                    nparray_reshaped = cv2.cvtColor(nparray_reshaped, cv2.COLOR_BAYER_RG2RGB)
                    if count % 4 == 1:
                        cv2.imwrite(f'/media/taoyuanipc1/disk/imgs/jpg/{path_time}.jpg', nparray_reshaped)
        
                        with open(f'/media/taoyuanipc1/disk/imgs/jpg/{path_time}.jpg', "rb") as image_file:  
                            await websocket.send(image_file.read())
                            # await websocket.send(cv2.imencode('.jpg', nparray_reshaped)[1].tostring())
                    t3 += time.time()
                    #==== show =======
                    # frame = cv2.cvtColor(nparray_reshaped, cv2.COLOR_BGR2RGB)
                    # frame = cv2.resize(nparray_reshaped,(int(self.camera_width/4), int(self.camera_height/4)))
                    # cv2.imshow('preview', frame)
                    # if cv2.waitKey(1) & 0xFF == ord('q'):
                    #     break

                    device.requeue_buffer(image_buffer)
                    t4 += time.time()
                    if count % interval == 0 and count != 0:
                        print('total time:',(t4-t1) / interval)
                        print('time:',(t2-t1)/interval, (t3-t2)/interval, (t4-t3)/interval)
                        count = t1 = t2 = t3 = t4 = 0 
                # cv2.destroyAllWindows()
            system.destroy_device()
    
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop = asyncio.get_event_loop()
        # start_server = websockets.serve(preview_func, "127.0.0.1", 8061,reuse_port=True)
        start_server = websockets.serve(preview_func, "127.0.0.1", 8061) # python 3.6: no reuse_port
        loop.run_until_complete(start_server)
        loop.run_forever()
        print('finished preview')
      

    def create_devices_with_tries(self):
        """
        This function waits for the user to connect a device before raising
        an exception
        """
        tries = 0
        tries_max = 6
        sleep_time_secs = 10
        while tries < tries_max:  # Wait for device for 60 seconds
            devices = system.create_device()
            if not devices:
                print(
                    f'Try {tries+1} of {tries_max}: waiting for {sleep_time_secs} '
                    f'secs for a device to be connected!')
                for sec_count in range(sleep_time_secs):
                    time.sleep(1)
                    print(f'{sec_count + 1 } seconds passed ',
                        '.' * sec_count, end='\r')
                tries += 1
            else:
                print(f'Created {len(devices)} device(s)')
                return devices
        else:
            raise Exception(f'No device found! Please connect a device and run '
                            f'the example again.')

    def set_exposure_time(self, device, exposure_set):
        """
        Manually set exposure time
        In order to get synchronized images, the exposure time must be
        synchronized as well.
        """
        device.nodemap['ExposureAuto'].value = 'Off'


        Exposure_Time = device.nodemap['ExposureTime']

        min_exposure = Exposure_Time.min
        max_exposure = Exposure_Time.max
        print('exposure min , max:',min_exposure, max_exposure)

        if (exposure_set >= min_exposure and
                exposure_set <= max_exposure):
            Exposure_Time.value = exposure_set
        else:
            Exposure_Time.value = max_exposure

        self.exposure_time = Exposure_Time.value
        self.exposure_time_max = max_exposure
        self.exposure_time_min = min_exposure

    def set_gain(self, device, gain_set):
        Gain = device.nodemap['Gain']

        min_gain = device.nodemap['Gain'].min # 0.0
        max_gain = device.nodemap['Gain'].max # 48.0
        # print('gain min , max:',min_gain,max_gain)
        if (gain_set >= min_gain and gain_set <= max_gain):
            Gain.value = gain_set
        else:
            Gain.value = min_gain
        
        self.gain = Gain.value

    def set_pixel(self,device, width, height): 
        device.nodemap['Width'].value = width
        device.nodemap['Height'].value = height


    def set_fps(self, device, fps):
        device.nodemap['AcquisitionFrameRateEnable'].value = True
        # if device.nodemap['AcquisitionFrameRate'].max < 250.0:
        #     device.nodemap['AcquisitionFrameRate'].value = device.nodemap['AcquisitionFrameRate'].max
        # else: 
        #     device.nodemap['AcquisitionFrameRate'].value = device.nodemap['AcquisitionFrameRate'].max
        device.nodemap['AcquisitionFrameRate'].value = fps
        device.nodemap['DeviceStreamChannelPacketSize'].value = device.nodemap['DeviceStreamChannelPacketSize'].max
        self.fps = device.nodemap['AcquisitionFrameRate'].value
        
    def time_update_function(self):
        now = datetime.datetime.now()
        return now.strftime('%Y%m%d_%H:%M:%S_%f')



if __name__ == '__main__':
    controller = lucid_camera()
    controller.run()