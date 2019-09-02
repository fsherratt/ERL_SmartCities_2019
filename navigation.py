import numpy as np
import time

class navigation:
    pathMeshElements = 10
    elevationMeshElements = 11 # Number of elevation angles to evaluate
    azimuthMeshElements = 11 # Number of azimuth angles to evaluate

    azimuthRange = np.deg2rad(30)  # +- 30 degree view
    elevationRange = np.deg2rad(10)

    _numPaths = elevationMeshElements * azimuthMeshElements
    _numElements = 2 * _numPaths * pathMeshElements
    _numCoordinates = 3

    def __init__(self):
        self.aircraftPosition = np.asarray((0,0,0)) # x,y,z
        self.targetPosition = np.asarray((0,0,0)) # x,y,z

        print('Number of mesh elements %d' % self._numElements)

    def calcNewChasePoint(self, currPosition, targetPosition):
        self.setAircraftPosition = currPosition
        self.setTargetPosition = targetPosition

        pass


    # Take current position and target position
    def setTargetPosition(self, targetPosition):
        self.targetPosition = np.asarray(targetPosition)


    def setAircraftPosition(self, currPosition):
        self.aircraftPosition = np.asarray(currPosition)

    
    # Produce possible routes between the two
    def calcGotoPoints(self):
        travelVector = self.targetPosition - self.aircraftPosition
        pathLength = np.linalg.norm(travelVector)

        # Using a spherical coordinate system
        # Calculate heading to next WP
        az = np.arctan2(travelVector[1], travelVector[0]) # Azimuth
        el = np.arcsin(travelVector[2] / pathLength) # Elevation
        r = 10 # Distance away

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

        # Convert from spherical to cartesian
        x_a = r * np.cos(el) * np.cos(az)
        y_a = r * np.cos(el) * np.sin(az)
        z_a = r * np.sin(el)

        pointA = self.aircraftPosition + np.column_stack((x_a, y_a, z_a))

        # Eliminate any point that exceeds competition volume - if a cuboid arena only possible if goto outside volume
        return pointA


    # Provide points along each route to evaluate risk at
    # Select route with minimum risk - If risk too high do something sensible
    # Route goes from UAV location -> chase point -> target points
    def pathMeshGrid(self, gotoPoints):
        # Calculate vector between points aircraft -> goto & goto -> target location
        pathA_vector = ( gotoPoints - self.aircraftPosition )
        pathB_vector = ( self.targetPosition - gotoPoints )

        path_vectors = np.column_stack((pathA_vector, pathB_vector))
        path_vectors = np.reshape( path_vectors, (-1, self._numCoordinates) )

        # Linspace for number of points to evaluate. e.g. 10%, 20%, 30%...
        ratio = np.linspace( 0, 1, self.pathMeshElements + 1 )
        ratio = ratio[1:] # remove first element

        # Matrix magic to calculate points to get things to correct shapes
        ratio = np.tile( ratio, 2*self._numPaths )
        ratio = np.tile( ratio, ( self._numCoordinates, 1 ) ).transpose()

        # Multiply vectors by linspace to give all points to evaluate - don't double count goto position
        points = np.repeat(path_vectors, self.pathMeshElements, 0) * ratio
        
        startPointA = np.tile(self.aircraftPosition, (self._numPaths, self.pathMeshElements))
        startPointB = np.tile(gotoPoints, (1, self.pathMeshElements))
        
        path_start = np.column_stack((startPointA, startPointB))
        path_start = np.reshape( path_start, (-1, 3) )

        # Add to vector
        points += path_start

        return points


    def getPointRisk(self, meshGrid):
        pointRisk = np.ones((self._numElements), dtype=np.float)
        return pointRisk


    def calculatePathRisk(self, gotoPoints, pointRisk):      
        # Split into routes and sum to give route risk
        pointRisk += 1e-256 # Baseline risk

        # Normalise based on route distance -> shorter routes are prefered
        pathADist = np.linalg.norm(gotoPoints[0] - self.aircraftPosition)
        pathADist = np.tile(pathADist, (self._numPaths,self.pathMeshElements))

        pathBDist = np.linalg.norm(self.targetPosition - gotoPoints, axis=1)
        pathBDist = np.tile(pathBDist, (self.pathMeshElements,1)).transpose()

        pathDist = np.column_stack((pathADist, pathBDist))
        pathDist = np.reshape(pathDist, (-1))
        pathDist /= self.pathMeshElements

        pointRisk *= pathDist

        # Sum points risks for each path
        pointRisk = np.reshape(pointRisk, (self._numPaths, -1) )

        pathRisk = np.sum(pointRisk, axis=1)

        return pathRisk

if __name__ == "__main__":
    nav = navigation()

    cummlativeTime = 0

    for i in range(1000):
        startTime = time.time()
        # nav.setAircraftPosition((1,2,3))
        nav.setTargetPosition((100,0,0))

        gotoPoints = nav.calcGotoPoints()
        meshPoints = nav.pathMeshGrid(gotoPoints)
        pointRisk = nav.getPointRisk(meshPoints)
        pathRisk = nav.calculatePathRisk(gotoPoints, pointRisk)

        min_path_index = np.nanargmin(pathRisk)
        min_path_point = gotoPoints[min_path_index]
        min_path_risk = pathRisk[min_path_index]

        executionTime = time.time()-startTime
        cummlativeTime += executionTime
        print('%d\t%f' % (i, executionTime))

    print('-------------')
    print(cummlativeTime/(i+1))
