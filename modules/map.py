import numpy as np
from scipy import interpolate
from modules.realsense import d435

class mapper:
    num_coordinate = 3

    def __init__(self, SITL):
        xRange = [-10, 10]
        yRange = [-10, 10]
        zRange = [-3, 3]

        xDivisions = 100
        yDivisions = 100
        zDivisions = 3

        self.xBins = np.linspace( xRange[0], xRange[1], xDivisions )
        self.yBins = np.linspace( yRange[0], yRange[1], yDivisions )
        self.zBins = np.linspace( zRange[0], zRange[1], zDivisions )

        self.grid = np.zeros((xDivisions, yDivisions, zDivisions))

        self.interpFunc = interpolate.RegularGridInterpolator( (self.xBins, self.yBins, self.zBins),
                                                               self.grid, method = 'linear',
                                                               bounds_error = False,
                                                               fill_value = np.nan )

        if SITL:
            self.d435Obj = None
        else:
            self.connectD435()

    def __del__(self):
        if self.d435Obj is not None:
            self.d435Obj.closeConnection()

    def connectD435(self):
        self.d435Obj = d435.rs_d435( framerate = 30 )
        self.d435Obj.openConnection()
    
    # --------------------------------------------------------------------------
    # frame_to_global_points
    # param frame - (3,X,Y) matrix of coordinates from d435 camera
    # param pos - [x,y,z] offset cooridnates
    # param r - scipy local->global rotation object
    # return Null
    # --------------------------------------------------------------------------
    def frame_to_global_points( self, frame, pos, r ):
        # Produce list of valid points
        points = np.reshape(frame, (self.num_coordinate, -1)).transpose()
        points = points[ ~np.isnan(points[:, 2]), :]

        # Transform into global coordinate frame
        points_global = r.apply( points )
        points_global += np.tile(pos, (points.shape[0], 1))

        return points_global

    def update(pos, rot):
        # Limit range of depth camera
        frame = self.d435Obj.range_filter(frame, minRange = 0, maxRange = 30)
        # Convert to 3D coordinates
        frame = self.d435Obj.deproject_frame( frame )

        # Convert to global coordinates
        points_global = self.mapObj.frame_to_global_points(frame, pos, r)

        # Update map
        mapObj.updateMap(points_global)

    # --------------------------------------------------------------------------
    # updateMap
    # param points - (N,3) list of points to qadd to the map
    # return Null
    # --------------------------------------------------------------------------
    def updateMap(self, points):
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
    def queryMap(self, queryPoints):
        return self.interpFunc(queryPoints)

if __name__ == "__main__":
    
    from modules.realsense import t265

    import cv2
    import time

    t265Obj = t265.rs_t265()

    mapObj = mapper()

    with t265Obj:
        while True:
            # Get frames of data - points and global 6dof
            pos, r, _ = t265Obj.getFrame()

            mapObj.update(pos,r)

            cv2.imshow('map', mapObj.grid / np.max(mapObj.grid))
            cv2.waitkey(1)

            time.sleep(1)