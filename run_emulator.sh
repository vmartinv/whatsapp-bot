#!/bin/sh

export ANDROID_SDK=~/.androidsdk                   
export PATH=$ANDROID_SDK/emulator:$ANDROID_SDK/tools:$PATH
sudo modprobe v4l2loopback

gst-launch-1.0 videotestsrc ! "video/x-raw,width=512,height=640,framerate=30/1,format=YUY2" ! v4l2sink device=/dev/video2 &

emulator -webcam-list @Pixel_API_28
emulator -camera-back webcam1 -no-snapshot-load -no-boot-anim @Pixel_API_28 &
sleep 3
kill %1
