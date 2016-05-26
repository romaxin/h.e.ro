#!/bin/sh
#

cvlc -vvv --no-audio SampleVideo_176x144_1mb.3gp --sout "#transcode{vcodec=MJPG,vb=800}:standard{access=http,mux=mpjpeg,dst=:18223/}" --sout-http-mime="multipart/x-mixed-replace;boundary=--7b3cc56e5f51db803f790dad720ed50a"

