from realsense.t265 import rs_t265
from realsense.d435 import rs_d435

import map

t265 = rs_t265()
d435 = rs_d435( framerate = 30 )

mapObj = map.mapper()

try:
    with t265, d435:
        while True:
            # Get frames of data - points and global 6dof
            frame = d435.getFrame()
            pos, r, _ = t265.getFrame() 

            mapObj.update()

except KeyboardInterrupt:
    pass