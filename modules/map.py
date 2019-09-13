import numpy as np
from scipy import interpolate
from modules.realsense import d435


class mapper:
    num_coordinate = 3

    def __init__(self):
        xRange = [-20, 20]
        yRange = [-20, 20]
        zRange = [-20, 20]

        xDivisions = 10
        yDivisions = 10
        zDivisions = 10

        self.xBins = np.linspace( xRange[0], xRange[1], xDivisions )
        self.yBins = np.linspace( yRange[0], yRange[1], yDivisions )
        self.zBins = np.linspace( zRange[0], zRange[1], zDivisions )

        self.grid = np.zeros((xDivisions, yDivisions, zDivisions))

        self.interpFunc = interpolate.RegularGridInterpolator( (self.xBins, self.yBins, self.zBins),
                                                               self.grid, method = 'linear',
                                                               bounds_error = False,
                                                               fill_value = np.nan )

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


class sitlMapper:
    def __init__(self):
        xRange = [-20, 20]
        yRange = [-20, 20]
        zRange = [-10, 0]

        xDivisions = 41
        yDivisions = 41
        zDivisions = 20

        self.xBins = np.linspace( xRange[0], xRange[1], xDivisions )
        self.yBins = np.linspace( yRange[0], yRange[1], yDivisions )
        self.zBins = np.linspace( zRange[0], zRange[1], zDivisions )

        self.posOld = np.asarray([0,0,0])
        self.grid = np.zeros((xDivisions, yDivisions, zDivisions))

        # Add Obstacle
        #north east down

        #self.grid[20, :, 5:14] = 1
        map_on =1
        obstacle = 1
        if map_on == 1:
            self.grid[10:12, 3:11, 0:12] = obstacle    #1
            self.grid[7:18, 14:17, :] = obstacle       #2
            self.grid[18:20, 6:19, :] = obstacle       #3
            self.grid[25:28, 0:12, 8:20] = obstacle    #4
            self.grid[28:41, 17:20, :] = obstacle      #5
            self.grid[28:31, 26:41, 0:12] = obstacle   #6
            self.grid[0:14, 24:26, 5:15] = obstacle    #7
            self.grid[18:20, 23:36, :] = obstacle      #8

            self.grid[10:12, 3:11, :] = obstacle  # 1
            self.grid[25:28, 0:12, :] = obstacle  # 4
            self.grid[28:31, 26:41, :] = obstacle  # 6
            self.grid[0:14, 24:26, :] = obstacle  # 7


            #self.grid[17:19, 7:15, :] = 0
        self.interpFunc = interpolate.RegularGridInterpolator( (self.xBins, self.yBins, self.zBins),
                                                               self.grid, method = 'linear',
                                                               bounds_error = False,
                                                               fill_value = np.nan )
    # could try nearest interp method = 'nearest' -faster but at what cost



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