import d435
import numpy as np
import cv2

d435Obj = d435.rs_t265( framerate = 30 )

with d435Obj:
    for i in range(1000):
        frame = d435Obj.getFrame()
        
        frame = frame * (d435Obj.scale*25)
        frame = np.asarray(frame, np.uint8)
        
        frame = cv2.applyColorMap(frame, cv2.COLORMAP_JET)

        cv2.imshow('frame', frame)
        cv2.waitKey(1)