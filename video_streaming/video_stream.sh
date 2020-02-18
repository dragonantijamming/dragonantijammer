#!/bin/sh

# Video streaming (transmitting) side
# Assumes dragonradio is already running
# Assumes video file is called temp.mp4
sudo apt-get install ffmpeg
ffmpeg -re -i temp.mp4 -movflags +frag_keyframe -f mpegts udp://10.10.10.1:54545

