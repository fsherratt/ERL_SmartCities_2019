import numpy as np
from scipy import interpolate
import cv2

class mapper:
    def __init__(self):
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

    def update(self, frame, pos, r):
        # Filter depth frame so that some parts are ignored
        outOfRange = np.where( (frame > 1) | (frame < 0.5) )
        frame[outOfRange] = np.nan

        # Convert to list of 3D coordinates
        frame = self._d435.deproject_frame( frame )
        points = np.reshape(frame, (3, -1)).transpose()
        
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