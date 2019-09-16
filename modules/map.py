import numpy as np
from scipy import interpolate
from scipy import io
from modules.realsense import d435


class mapper:
    num_coordinate = 3

    xRange = [-50, 50]
    yRange = [-50, 50]
    zRange = [-5, 20]

    localMapRange = 10

    voxelSize = 0.2
    voxelMaxWeight = 1000
    voxelWeightDecay = 20

    xDivisions = int((xRange[1] - xRange[0]) / voxelSize)
    yDivisions = int((yRange[1] - yRange[0]) / voxelSize)
    zDivisions = int((zRange[1] - zRange[0]) / voxelSize)

    cameraMinRange = 0.1
    cameraMaxRange = 6

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
        self.d435Obj = d435.rs_d435(framerate=60, width=480, height=270)
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

    # --------------------------------------------------------------------------
    # updateMap
    # param pos - (N,3) list of points to add to the map
    # param rot - 
    # return Null
    # --------------------------------------------------------------------------
    def update(self, pos, rot):
        frame = self.d435Obj.getFrame()

        # Add to map
        points = self.d435Obj.deproject_frame( frame, 
                                                minRange = self.cameraMinRange, 
                                                maxRange = self.cameraMaxRange )
        points = self.local_to_global_points(points, pos, rot)     
        self.updateMap(points, pos)

        return frame

    def digitizePoints(self, points):
        xSort = np.digitize( points[:, 0], self.xBins )
        ySort = np.digitize( points[:, 1], self.yBins )
        zSort = np.digitize( points[:, 2], self.zBins )

        return [xSort, ySort, zSort]

    # --------------------------------------------------------------------------
    # updateMap
    # param points - (N,3) list of points to qadd to the map
    # return Null
    # --------------------------------------------------------------------------
    def updateMap(self, points, pos):
        # Update map
        gridPoints = self.digitizePoints(points)
        np.add.at(self.grid, gridPoints, 1)

        activeGridCorners = np.asarray([pos - [self.localMapRange,
                                               self.localMapRange,
                                               self.localMapRange], 
                                        pos + [self.localMapRange,
                                               self.localMapRange,
                                               self.localMapRange]])
        activeGridCorners = self.digitizePoints(activeGridCorners)

        activeGrid = self.grid[activeGridCorners[0][0]:activeGridCorners[0][1], 
                            activeGridCorners[1][0]:activeGridCorners[1][1], 
                            activeGridCorners[2][0]:activeGridCorners[2][1]]

        activeGrid = np.where(activeGrid < self.voxelMaxWeight, 
                              activeGrid - self.voxelWeightDecay, # If True
                              activeGrid) # If False
        activeGrid = np.clip(activeGrid, a_min=0, a_max=self.voxelMaxWeight)

        self.grid[activeGridCorners[0][0]:activeGridCorners[0][1], 
                activeGridCorners[1][0]:activeGridCorners[1][1], 
                activeGridCorners[2][0]:activeGridCorners[2][1]] = activeGrid
    
    # --------------------------------------------------------------------------
    # queryMap
    # param queryPoints - (N,3) list of points to query against map
    # return (N) list of risk for each point
    # --------------------------------------------------------------------------
    def queryMap(self, queryPoints):
        return self.interpFunc(queryPoints)


    def saveToMatlab(self, filename):
        io.savemat( filename, mdict=dict(map=self.grid), do_compression=False)

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

        if map_on == 2:
            self.grid[:29, :2, :] = obstacle  # 1
            self.grid[10:29, 5:9, :] = obstacle  # 2
            self.grid[28:39, 8:11, :] = obstacle  # 3
            self.grid[36, 8:39, :] = obstacle  # 4
            self.grid[9:27, 13:16, :] = obstacle  # 5
            self.grid[15:32, 28:, :] = obstacle  # 6

        self.interpFunc = interpolate.RegularGridInterpolator( (self.xBins, self.yBins, self.zBins),
                                                               self.grid, method = 'nearest',
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
        try:
            while True:
                # Get frames of data - points and global 6dof
                pos, r, _ = t265Obj.getFrame()
                
                starttime = time.time()
                frame = mapObj.update(pos,r)
                print('Loop Time: {}'.format(time.time()-starttime))

                posGridCell = mapObj.digitizePoints(pos[np.newaxis,:])
                
                starttime = time.time()
                grid = mapObj.grid[:,:,posGridCell[2]] / np.max(mapObj.grid[:,:,posGridCell[2]])
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
        except KeyboardInterrupt:
            pass

    mapObj.saveToMatlab( 'TestMap.mat' )