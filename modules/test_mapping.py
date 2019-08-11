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

            # Filter depth frame so that some parts are ignored
            frame = d435.range_filter(frame, minRange = 0, maxRange = 30)
            frame = d435.deproject_frame( frame )

            # Convert to global coordinates
            points_global = mapObj.frame_to_global_points(frame, pos, r)

            # Update map
            mapObj.updateMap(points_global)

except KeyboardInterrupt:
    pass