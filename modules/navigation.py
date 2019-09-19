import numpy as np
import time
'''
meshPoints = navObj.updatePt1(pos, targetPos)
pointRisk = mapObj.queryMap(meshPoints)
goto, heading, risk = navObj.updatePt2(pointRisk)
'''

class navigation:
    percentGotoDist = 0.5
    minCPDistance = 2
    maxCPDistance = 10
    pathMeshElements = 10
    elevationMeshElements = 11 # Number of elevation angles to evaluate #11
    azimuthMeshElements = 11 # Number of azimuth angles to evaluate
    num_pts = elevationMeshElements*azimuthMeshElements # Number of points total to evaluate
    azimuthRange = np.deg2rad(110)  # +- 30 degree view
    elevationRange = np.deg2rad(110) #110

    _numCoordinates = 3

    def __init__(self, min_x=-20, max_x=20, min_y=-20, max_y=20, min_z=-0.5, max_z=-10):
        self.xRange = [min_x, max_x]
        self.yRange = [min_y, max_y]
        self.zRange = [min_z, max_z]

        self.aircraftPosition = np.asarray((0,0,0)) # x,y,z
        self.targetPosition = np.asarray((0,0,0)) # x,y,z
        self.heading = 0
        self.DistanceThreshold = 20

    # Produce possible positions to fly to on the way to a waypoint
    def calcGotoPoints(self):
        travelVector = self.targetPosition - self.aircraftPosition
        pathLength = np.linalg.norm(travelVector)

        # Using a spherical coordinate system
        # Calculate heading to next WP
        az = np.arctan2(travelVector[1], travelVector[0]) # Azimuth
        el = np.arcsin(travelVector[2] / pathLength) # Elevation

        # Calculate groups of points radiating from aircraft in general
        # direction of the next way point (polar coordinates)
        az = np.linspace(az - self.azimuthRange,
                         az + self.azimuthRange,
                         self.azimuthMeshElements)

        el = np.linspace(el - self.elevationRange,
                         el + self.elevationRange,
                         self.elevationMeshElements)

        el, az = np.meshgrid(el, az, indexing='ij')

        # Reshape to 1D Vector
        el = np.reshape(el, (-1))
        az = np.reshape(az, (-1))

        # generate vector of random distances to look ahead
        r = np.random.uniform(low=self.minCPDistance, high=pathLength, size=(self.num_pts,))

        # Convert from spherical to cartesian
        x_a = r * np.cos(el) * np.cos(az)
        y_a = r * np.cos(el) * np.sin(az)
        z_a = r * np.sin(el)

        # Create matrix of positions to fly to on the way to next waypoint
        pointA = self.aircraftPosition + np.column_stack((x_a, y_a, z_a))

        # Eliminate any point that exceeds competition volume - if a cuboid arena only possible if goto outside volume
        xValidPoints = np.logical_and(pointA[:, 0] > self.xRange[0], pointA[:, 0] < self.xRange[1])
        yValidPoints = np.logical_and(pointA[:, 1] > self.yRange[0], pointA[:, 1] < self.yRange[1])
        zValidPoints = np.logical_and(pointA[:, 2] > self.zRange[0], pointA[:, 2] < self.zRange[1])

        validPoints = np.logical_and(np.logical_and(xValidPoints, yValidPoints), zValidPoints)

        pointA = pointA[ validPoints, : ]
        return pointA

    # Provide points along each route to evaluate risk at
    # Select route with minimum risk - If risk too high do something sensible
    # Route goes from UAV location -> chase point -> target points
    # This function needs to be faster
    def pathMeshGrid(self, gotoPoints):
        numPaths = gotoPoints.shape[0]

        # Calculate vector between points aircraft -> goto & goto -> target location
        pathA_vector = (gotoPoints - self.aircraftPosition)
        pathB_vector = (self.targetPosition - gotoPoints)

        path_vectors = np.column_stack((pathA_vector, pathB_vector))
        path_vectors = np.reshape(path_vectors, (-1, self._numCoordinates))

        # Linspace for number of points to evaluate. e.g. 10%, 20%, 30%...
        ratio = np.linspace( 0, 1, self.pathMeshElements + 1 )[1:]

        ratio = np.tile(ratio, 2 * numPaths)
        ratio = np.tile(ratio, (self._numCoordinates, 1)).transpose()
        # Multiply vectors by linspace to give all points to evaluate - don't double count goto position
        points = np.repeat(path_vectors, self.pathMeshElements, 0) * ratio

        startPointA = np.tile(self.aircraftPosition, (numPaths, self.pathMeshElements))
        startPointB = np.tile(gotoPoints, (1, self.pathMeshElements))

        path_start = np.column_stack((startPointA, startPointB))
        path_start = np.reshape( path_start, (-1, 3) )

        # Add to vector
        points += path_start

        self.Euclideanpoints = np.linalg.norm(points - self.aircraftPosition[np.newaxis, :], axis=1)
        self.Euclideanpoints = np.reshape(self.Euclideanpoints, (numPaths, -1))
        return points

    def calculatePathRisk(self, gotoPoints, pointRisk):
        numPaths = gotoPoints.shape[0]
        pointRisk = np.reshape(pointRisk, (numPaths, -1))


        # Split into routes and sum to give route risk
        pointARisk = pointRisk[:, :self.pathMeshElements]
        pointBRisk = pointRisk[:, self.pathMeshElements:]

        # Normalise based on route distance -> shorter routes are prefered
        pathADist = np.linalg.norm(gotoPoints - self.aircraftPosition, axis=1)
        pathBDist = np.linalg.norm(self.targetPosition - gotoPoints, axis=1)

        # Remove leg A
        self.Euclideanpoints = self.Euclideanpoints[:, self.pathMeshElements:]

        # Threshold based on distance
        self.Euclideanpoints[self.Euclideanpoints <= self.DistanceThreshold] = 1
        self.Euclideanpoints[self.Euclideanpoints != 1] = 0

        # ignore any point risks outside threshold within legB
        pointBRisk *= self.Euclideanpoints

        # add base risk
        pointARisk += 1e-255
        pointBRisk += 1e-255

        # make longer routes more risky
        pointARisk = np.multiply(pointARisk, pathADist[:,np.newaxis])
        pointBRisk = np.multiply(pointBRisk, pathBDist[:,np.newaxis])

        # combine point risks
        pointRisk = np.column_stack((pointARisk, pointBRisk))

        # Sum points risks for each path
        pathRisk = np.sum(pointRisk, axis=1)

        return pathRisk

    def updatePt1(self, pos, targetPos):
        self.aircraftPosition = np.asarray(pos)
        self.targetPosition = np.asarray(targetPos)

        self.gotoPoints = self.calcGotoPoints()

        #this operation is slow
        meshPoints = self.pathMeshGrid(self.gotoPoints)

        return meshPoints

    def updatePt2(self, pointRisk):
        pathRisk = self.calculatePathRisk(self.gotoPoints, pointRisk)

        min_path_index = np.nanargmin(pathRisk)
        min_path_point = self.gotoPoints[min_path_index]
        min_path_risk = pathRisk[min_path_index]

        self.heading = np.arctan2((min_path_point[1] - self.aircraftPosition[1]),
                                  (min_path_point[0] - self.aircraftPosition[0]))

        return min_path_point, self.heading, min_path_risk


if __name__ == "__main__":
    nav = navigation()

    cummlativeTime = 0

    for i in range(1000):
        startTime = time.time()

        meshPoints = nav.updatePt1([0,0,0], [10,0,0])

        pointRisk = np.ones( meshPoints.shape[0] )
        nav.updatePt2( pointRisk )
        
        executionTime = time.time()-startTime
        cummlativeTime += executionTime
        print('%d\t%f' % (i, executionTime))

    print('-------------')
    print(cummlativeTime/(i+1))
