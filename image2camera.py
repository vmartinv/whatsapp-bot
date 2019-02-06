#!/usr/bin/python2
#Send image data to v4l2loopback using python
#Remember to do sudo modprobe v4l2loopback first!
#Released under CC0 by Tim Sheerman-Chase, 2013

# sudo modprobe v4l2loopback
# python2 image-to-v4l2loopback.py
# emulator  -camera-back webcam1 -no-snapshot-load -no-boot-anim @Pixel_API_28

import fcntl, sys, os
from v4l2 import *
import time
import scipy.misc as misc
import numpy as np
import cv2
from threading import Thread, Event
import logging
from PIL import Image

def ConvertToYUYV(sizeimage, bytesperline, im):
    padding = 0
    buff = np.zeros((sizeimage+padding, ), dtype=np.uint8)
    imgrey = im[:,:,0] * 0.299 + im[:,:,1] * 0.587 + im[:,:,2] * 0.114
    Pb = im[:,:,0] * -0.168736 + im[:,:,1] * -0.331264 + im[:,:,2] * 0.5
    Pr = im[:,:,0] * 0.5 + im[:,:,1] * -0.418688 + im[:,:,2] * -0.081312

    for y in range(imgrey.shape[0]):
        #Set lumenance
        cursor = y * bytesperline + padding
        for x in range(imgrey.shape[1]):
            try:
                buff[cursor] = imgrey[y, x]
            except IndexError:
                pass
            cursor += 2

        #Set color information for Cb
        cursor = y * bytesperline + padding
        for x in range(0, imgrey.shape[1], 2):
            try:
                buff[cursor+1] = 0.5 * (Pb[y, x] + Pb[y, x+1]) + 128
            except IndexError:
                pass
            cursor += 4

        #Set color information for Cr
        cursor = y * bytesperline + padding
        for x in range(0, imgrey.shape[1], 2):
            try:
                buff[cursor+3] = 0.5 * (Pr[y, x] + Pr[y, x+1]) + 128
            except IndexError:
                pass
            cursor += 4

    return buff.tostring()

def frame_image(img, frame_size):
    fh, fw = frame_size # border size in pixel
    ny, nx = img.shape[0], img.shape[1] # resolution / number of pixels in x and y
    if img.ndim == 3: # rgb or rgba array
        framed_img = np.zeros((fh, fw, img.shape[2]))
        framed_img[:, :, :3] = 255
    elif img.ndim == 2: # grayscale image
        framed_img = np.ones((fh, fw))
    framed_img[(fh-ny)/2:(fh-ny)/2+ny, (fw-nx)/2:(fw-nx)/2+nx] = img
    return framed_img
    
def sendImageSetup(image, devName, height=640, width=512):
    if not os.path.exists(devName):
        logging.error("Warning: device does not exist",devName)
    device = open(devName, 'wb', 0)

    capability = v4l2_capability()
    logging.debug("get capabilities result", (fcntl.ioctl(device, VIDIOC_QUERYCAP, capability)))
    logging.debug("capabilities", hex(capability.capabilities))

    fmt = V4L2_PIX_FMT_YUYV
    #fmt = V4L2_PIX_FMT_YVU420

    logging.info("v4l2 driver: " + capability.driver)
    format = v4l2_format()
    format.type = V4L2_BUF_TYPE_VIDEO_OUTPUT
    format.fmt.pix.pixelformat = fmt
    format.fmt.pix.width = width
    format.fmt.pix.height = height
    format.fmt.pix.field = V4L2_FIELD_NONE
    format.fmt.pix.bytesperline = width * 2
    format.fmt.pix.sizeimage = width * height * 2
    format.fmt.pix.colorspace = V4L2_COLORSPACE_JPEG

    logging.debug("set format result", (fcntl.ioctl(device, VIDIOC_S_FMT, format)))
    #Note that format.fmt.pix.sizeimage and format.fmt.pix.bytesperline 
    #may have changed at this point

    #Create image buffer
    image = misc.imrotate(image, 90)
    im = frame_image(image, (height, width))
    buff = ConvertToYUYV(format.fmt.pix.sizeimage, format.fmt.pix.bytesperline, im)
    return device, buff

def sendImage(image, devName, height=640, width=512):
    device, buff = sendImageSetup(image, devName, height, width)
    logging.info("sending data to camera")
    while True:     
        device.write(buff)
        time.sleep(1.)

class SendImageJob(Thread):
    def __init__(self, image, devName, height=640, width=512):
        Thread.__init__(self)
 
        # The shutdown_flag is a threading.Event object that
        # indicates whether the thread should be terminated.
        self.shutdown_flag = Event()
        self.device, self.buff = sendImageSetup(image, devName, height, width)
 
    def run(self): 
        while not self.shutdown_flag.is_set():
            self.device.write(self.buff)
            time.sleep(1.)
 
if __name__=="__main__":
    image = "sample_qr.png"
    if len(sys.argv) >= 2:
        image = sys.argv[1]
    sendImage(misc.imread(image), '/dev/video2')
