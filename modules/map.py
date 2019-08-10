from realsense.t265 import rs_t265
from realsense.d435 import rs_d435
import numpy as np

class mapper:
    def __init__(self):
        self._t265 = rs_t265()
        self._d435 = rs_d435( framerate = 30 )

    def loop(self):
        with self._t265, self._d435:
            while True:
                # Get frames of data
                # Get frames of data - points and global 6dof
                depthFrame = self._d435.getFrame()
                pos, r, _ = self._t265.getFrame()

                depthFrame = self._d435.deproject_frame( depthFrame )

                # Down sample frame to reduce noise/increase performance?
                
                # Transform into global coordinate frame
                points = np.reshape(depthFrame, (3, -1)).transpose()
                points_global = r.apply( points )

                # Update map
