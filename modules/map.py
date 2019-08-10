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
                depthFrame = self._d435.getFrame()
                pos, eul, _ = self._t265.getFrame()
                
                # Transform into global coordinate frame

                # Update map