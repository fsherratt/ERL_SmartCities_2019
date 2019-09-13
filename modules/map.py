import numpy as np
from scipy import interpolate
from modules.realsense import d435


class mapper:
    num_coordinate = 3

    xDivisions = 500
    yDivisions = 500
    zDivisions = 100

    xRange = [-10, 10]
    yRange = [-10, 10]
    zRange = [-5, 20]

    def __init__(self):
        self.xBins = np.linspace( self.xRange[0], self.xRange[1], self.xDivisions )
        self.yBins = np.linspace( self.yRange[0], self.yRange[1], self.yDivisions )
        self.zBins = np.linspace( self.zRange[0], self.zRange[1], self.zDivisions )

        self.grid = np.zeros((self.xDivisions, self.yDivisions, self.zDivisions), dtype=np.int16)

        self.interpFunc = interpolate.RegularGridInterpolator( (self.xBins, self.yBins, self.zBins),
                                                               self.grid, method = 'linear',
                                                               bounds_error = False,
                                                               fill_value = np.nan )

        self.connectD435()

    def __del__(self):
        if self.d435Obj is not None:
            self.d435Obj.closeConnection()

    def connectD435(self):
        self.d435Obj = d435.rs_d435(framerate=90, width=480, height=270)
        self.d435Obj.openConnection()
    
    # --------------------------------------------------------------------------
    # frame_to_global_points
    # param frame - (3,X,Y) matrix of coordinates from d435 camera
    # param pos - [x,y,z] offset cooridnates
    # param r - scipy local->global rotation object
    # return Null
    # --------------------------------------------------------------------------
    def local_to_global_points( self, local_points, pos, r ):
        # Transform into global coordinate frame
        points_global = r.apply(local_points)
        points_global = np.add(points_global, pos)

        return points_global

    def update(self, pos, rot):
        frame = self.d435Obj.getFrame()

        # Add to map
        points = self.d435Obj.deproject_frame( frame, minRange = 0.1, maxRange = 10 )
        points_global = self.local_to_global_points(points, pos, r)     
        mapObj.updateMap(points_global)

        return frame

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

        # Filter
        self.grid = np.where(self.grid < 200, self.grid - 5, self.grid)
        self.grid = np.clip(self.grid, a_min=0, a_max=200)
    
    # --------------------------------------------------------------------------
    # queryMap
    # param queryPoints - (N,3) list of points to query against map
    # return (N) list of risk for each point
    # --------------------------------------------------------------------------
    def queryMap(self, queryPoints):
        return self.interpFunc(queryPoints)


class sitlMapper:
    def __init__(self):
        xRange = [-25, 25]
        yRange = [-25, 25]
        zRange = [-25, 1]

        xDivisions = 10
        yDivisions = 10
        zDivisions = 10

        self.xBins = np.linspace( xRange[0], xRange[1], xDivisions )
        self.yBins = np.linspace( yRange[0], yRange[1], yDivisions )
        self.zBins = np.linspace( zRange[0], zRange[1], zDivisions )

        self.grid = np.zeros((xDivisions, yDivisions, zDivisions))

        # Add Obstacle
        self.grid[4:5, :, 4:] = 10

        self.interpFunc = interpolate.RegularGridInterpolator( (self.xBins, self.yBins, self.zBins),
                                                               self.grid, method = 'linear',
                                                               bounds_error = False,
                                                               fill_value = np.nan )
    
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
            
            starttime = time.time()
            frame = mapObj.update(pos,r)
            print('Loop Time: {}'.format(time.time()-starttime))
            
            starttime = time.time()
            grid = np.sum(mapObj.grid[:,:,20:40], axis=2) / np.max(mapObj.grid)
            empty = np.zeros((mapObj.xDivisions, mapObj.yDivisions))

            img = cv2.merge((grid, empty, empty))
            img = cv2.transpose(img)

            x = np.digitize( pos[0], mapObj.xBins ) - 1
            y = np.digitize( pos[1], mapObj.yBins ) - 1

            img = cv2.circle(img, (x,y), 5, (0,1,0), 2)

            vec = [20,0,0]
            vec = r.apply(vec) # Aero-ref -> Aero-body

            vec[0] += x
            vec[1] += y

            img = cv2.line(img, (x,y), (int(vec[0]), int(vec[1])), (0,0,1), 2)

            cv2.imshow('frame', frame)
            cv2.imshow('map', img )
            cv2.waitKey(1)
            
            print('')