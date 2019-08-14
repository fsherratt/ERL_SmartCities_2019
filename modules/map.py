import numpy as np
from scipy import interpolate
import cv2
from abc import ABC, abstractmethod, ABCMeta

class aMap( ABC ):
    @abstractmethod
    def updateMap( self, points: np.ndarray ) -> None:
        raise NotImplementedError('updateMap is not implemented')

    @abstractmethod
    def queryMap(self, queryPoints: list[ int ]) -> list[ int ]:
        raise NotImplementedError('queryMap is not implemented')
    @abstractmethod
    def getCurrentMap( self ) -> np.ndarray:
        raise NotImplementedError('getCurrentMap is not implemented')


class mapper( aMap ):
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
    
    # --------------------------------------------------------------------------
    # frame_to_global_points
    # param frame - (3,X,Y) matrix of coordinates from d435 camera
    # param pos - [x,y,z] offset cooridnates
    # param r - scipy local->global rotation object
    # return Null
    # --------------------------------------------------------------------------
    @staticmethod
    def frame_to_global_points( frame, pos, r ):
        # Produce list of valid points
        points = np.reshape(frame, (3, -1)).transpose()
        points = points[ ~np.isnan(points[:, 2]), :]

        # Transform into global coordinate frame
        points_global = r.apply( points )
        points_global += np.tile(pos, (points.shape[0], 1))

        return points_global

    # --------------------------------------------------------------------------
    # updateMap
    # param points - (N,3) list of points to qadd to the map
    # return Null
    # --------------------------------------------------------------------------
    def updateMap(self, points: np.ndarray) -> None:
        # Update map
        xSort = np.digitize( points[:, 0], self.xBins ) - 1
        ySort = np.digitize( points[:, 1], self.yBins ) - 1
        zSort = np.digitize( points[:, 2], self.zBins ) - 1

        np.add.at(self.grid, [xSort, ySort, zSort], 1)
    
    # --------------------------------------------------------------------------
    # queryMap
    # param queryPoints - (N,3) list of points to query against map
    # return (N) list of risk for each point
    # --------------------------------------------------------------------------
    def queryMap(self, queryPoints: list[ int ]) -> list[ int ]:
        return self.interpFunc(queryPoints)