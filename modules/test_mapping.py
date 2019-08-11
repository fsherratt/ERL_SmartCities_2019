from realsense.t265 import rs_t265
from realsense.d435 import rs_d435

import map

import numpy as np
import time

t265 = rs_t265()
d435 = rs_d435( framerate = 30 )

mapObj = map.mapper()

try:
    with t265, d435:
        while True:
            t0 = time.time()
            # Get frames of data - points and global 6dof
            frame = d435.getFrame()
            pos, r, _ = t265.getFrame() 

            # Filter depth frame so that some parts are ignored
            frame = d435.range_filter(frame, minRange = 0.5, maxRange = 1)

            # Convert to list of 3D coordinates
            frame = d435.deproject_frame( frame )
            points = np.reshape(frame, (3, -1)).transpose()
            
            # Filter out invalid points
            points = points[ ~np.isnan(points[:, 2]), :]

            # Transform into global coordinate frame
            points_global = r.apply( points )
            points_global += np.tile(pos, (points.shape[0], 1))

            mapObj.update(points_global)
            t1 = time.time()

            print(t1-t0)
except KeyboardInterrupt:
    pass