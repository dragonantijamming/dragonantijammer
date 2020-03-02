#!/bin/sh

# Video streaming receiver
sudo apt-get install vlc # Install VLC
sed -i 's/geteuid/getppid/' /usr/bin/vlc # Allow vlc to run when root (just a bit of magic here)
vlc udp://@:54545

