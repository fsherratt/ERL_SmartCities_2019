import d435
import numpy as np
import cv2

d435Obj = d435.rs_t265( framerate = 30 )

with d435Obj:
    while True:
        frame = d435Obj.getFrame()
        threeDFrame = d435Obj.deproject_frame(frame)

        cv2.imshow('frameX', threeDFrame[0,:,:])
        cv2.imshow('frameY', threeDFrame[1,:,:])
        cv2.imshow('frameZ', threeDFrame[2,:,:])
        cv2.waitKey(1)