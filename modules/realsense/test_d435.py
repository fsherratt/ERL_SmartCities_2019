import d435
import numpy as np

t265Obj = d435.rs_t265()

with t265Obj:
    for i in range(10):
        frame = t265Obj.getFrame()
        print(frame[240, 320])