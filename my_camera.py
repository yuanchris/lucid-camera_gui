import os
import time
from datetime import datetime
from pathlib import Path

import cv2  # pip install opencv-python
import numpy as np  # pip install numpy

from arena_api.__future__.save import Recorder
from arena_api.buffer import BufferFactory
from arena_api.system import system
from arena_api.enums import PixelFormat

from PIL import Image as PIL_Image  # pip install Pillow
# import pylab as plt


def create_devices_with_tries():
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

def set_exposure_time(device, exposure_set):
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

def set_gain(device, gain_set):
    Gain = device.nodemap['Gain']

    min_gain = device.nodemap['Gain'].min # 0.0
    max_gain = device.nodemap['Gain'].max # 48.0
    print('gain min , max:',min_gain,max_gain)
    if (gain_set >= min_gain and gain_set <= max_gain):
        Gain.value = gain_set
    else:
        Gain.value = max_gain

def set_pixel(device, width, height): 
    device.nodemap['Width'].value = width
    device.nodemap['Height'].value = height


def set_fps(device, fps):
    device.nodemap['AcquisitionFrameRateEnable'].value = True
    # if device.nodemap['AcquisitionFrameRate'].max < 250.0:
    #     device.nodemap['AcquisitionFrameRate'].value = device.nodemap['AcquisitionFrameRate'].max
    # else: 
    #     device.nodemap['AcquisitionFrameRate'].value = device.nodemap['AcquisitionFrameRate'].max
    device.nodemap['AcquisitionFrameRate'].value = fps
    device.nodemap['DeviceStreamChannelPacketSize'].value = device.nodemap['DeviceStreamChannelPacketSize'].max

def time_update_function():
    now = datetime.now()
    return now.strftime('%Y%m%d_%H:%M:%S_%f')


def streaming():
    devices = create_devices_with_tries()
    device = devices[0]
    print(device)

    #====================== setting  ===========================================================
    # Nodes Height Width
    set_pixel(device, device.nodemap['Width'].max , device.nodemap['Height'].max)
    print('width height:',device.nodemap['Width'].value, device.nodemap['Height'].value)

    device.nodemap['PixelFormat'].value = PixelFormat.BayerRG8
    device.nodemap['ADCBitDepth'].value = 'Bits8'
    # print(nodemap['ADCBitDepth'])

    # FPS
    set_fps(device, device.nodemap['AcquisitionFrameRate'].max)
    print('fps max', device.nodemap['AcquisitionFrameRate'].max)
    print('fps',  device.nodemap['AcquisitionFrameRate'].value)
    
    # Exposure Time and Gain
    set_exposure_time(device, 90000.0)
    print(f'''Exposure Time : {device.nodemap['ExposureTime'].value}''')
    set_gain(device, 0.0)
    print(f'''gain: {device.nodemap['Gain'].value}''')
    #========================================================================
    with device.start_stream(2):
        TOTAL_IMAGES = 10000
        t1 = t2 = t3 = t4 = 0
        interval = 30
        for count in range(TOTAL_IMAGES):
        
            t1 += time.time()

            image_buffer = device.get_buffer()
            
            # image_only_data = image_buffer.data
            # nparray = np.fromiter(image_only_data, dtype=np.uint8)
      
            nparray_reshaped = np.ctypeslib.as_array(image_buffer.pdata,shape=(image_buffer.height, image_buffer.width, int(image_buffer.bits_per_pixel / 8)))
            
            # print(nparray_reshaped)
     
            # cv2.imwrite(path, nparray_reshaped)
        
            # nparray_reshaped = nparray.reshape((
            #     image_buffer.height,
            #     image_buffer.width
            # ))
            
            

            t2 += time.time()
            # ====  save file ======
            path_time = time_update_function()
            nparray_reshaped.tofile(f'imgs/{path_time}.raw')

            nparray_reshaped = cv2.cvtColor(nparray_reshaped, cv2.COLOR_BAYER_RG2RGB)
            if count % 4 == 1:
                cv2.imwrite(f'imgs/{path_time}.jpg', nparray_reshaped)
                # png_array = PIL_Image.fromarray(nparray_reshaped)
                # png_array.save(path, quality = 95) # quality high the size is big, max 100

            t3 += time.time()
            # print(path)
            
            #==== show =======
     
            # frame = cv2.cvtColor(nparray_reshaped, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(nparray_reshaped,(1024, 540))
            cv2.imshow('image', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            device.requeue_buffer(image_buffer)
            t4 += time.time()
            if count % interval == 1:
                print('total time:',(t4-t1) / interval)
                print('time:',(t2-t1)/interval, (t3-t2)/interval, (t4-t3)/interval)
                t1 = t2 = t3 = t4 = 0
            
    system.destroy_device()

if __name__ == '__main__':
    start = time.time()
    streaming()
    print(time.time() - start)
