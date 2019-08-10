from realsense.t265 import rs_t265
from realsense.d435 import rs_d435
import numpy as np

import time

from scipy import interpolate

import cv2

class mapper:
    def __init__(self):
        self._t265 = rs_t265()
        self._d435 = rs_d435( framerate = 30 )

        xRange = [-10, 10]
        yRange = [-10, 10]
        zRange = [-3, 3]

        xDivisions = 100
        yDivisions = 100
        zDivisions = 60

        self.xBins = np.linspace( xRange[0], xRange[1], xDivisions )
        self.yBins = np.linspace( yRange[0], yRange[1], yDivisions )
        self.zBins = np.linspace( zRange[0], zRange[1], zDivisions )

        self.grid = np.zeros((xDivisions, yDivisions, zDivisions))

        self.interpFunc = interpolate.RegularGridInterpolator( (self.xBins, self.yBins, self.zBins),
                                                               self.grid, method = 'linear',
                                                               bounds_error = False,
                                                               fill_value = np.nan )

    def loop(self):
        with self._t265, self._d435:
            while True:
                t0 = time.time()
                # Get frames of data - points and global 6dof
                depthFrame = self._d435.getFrame()
                pos, r, _ = self._t265.getFrame()

                # Filter depth frame so that some parts are ignored
                outOfRange = np.where( (depthFrame > 1) | (depthFrame < 0.5) )
                depthFrame[outOfRange] = np.nan

                # Convert to list of 3D coordinates
                depthFrame = self._d435.deproject_frame( depthFrame )
                points = np.reshape(depthFrame, (3, -1)).transpose()
                
                # Filter out invalid points
                points = points[ ~np.isnan(points[:, 2]), :]

                # Transform into global coordinate frame
                points_global = r.apply( points )
                points_global += np.tile(pos, (points.shape[0], 1))

                # Update map
                xSort = np.digitize( points_global[:, 0], self.xBins ) - 1
                ySort = np.digitize( points_global[:, 1], self.yBins ) - 1
                zSort = np.digitize( points_global[:, 2], self.zBins ) - 1

                np.add.at(self.grid, [xSort, ySort, zSort], 1)

                # Top down view
                tmpGrid = np.sum( self.grid, axis=2 )
                cv2.imshow('grid', tmpGrid)
                cv2.waitKey(1)