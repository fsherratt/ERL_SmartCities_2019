import numpy as np

class navigation:
    pathMeshElements = 10
    elevationMeshElements = 10 # Number of elevation angles to evaluate
    azimuthMeshElements = 10 # Number of azimuth angles to evaluate

    azimuthRange = np.deg2rad(30)  # +- 30 degree view
    elevationRange = np.deg2rad(10)

    _numPaths = elevationMeshElements * azimuthMeshElements
    _numElements = 2 * _numPaths * pathMeshElements
    _numCoordinates = 3

    def __init__(self):
        
        self.aircraftPosition = np.asarray((0,0,0)) # x,y,z
        self.targetPosition = np.asarray((0,0,0)) # x,y,z

    def calcNewChasePoint(self, currPosition, targetPosition):
        self.setAircraftPosition = currPosition
        self.setTargetPosition = targetPosition

        chasePoints = self.generateEvaluationPoints()
        lowestRiskIndex, risk = self.evaluateRouteRisk(chasePoints)

        chasePoint = chasePoints[lowestRiskIndex, :] 


    # Take current position and target position
    def setTargetPosition(self, targetPosition):
        self.targetPosition = np.asarray(targetPosition)


    def setAircraftPosition(self, currPosition):
        self.aircraftPosition = np.asarray(currPosition)

    
    # Produce possible routes between the two
    def generateEvaluationPoints(self):
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
        el = np.reshape(el, np.size(el))
        az = np.reshape(az, np.size(az))

        # Convert from spherical to cartesian
        x_a = r * np.cos(el) * np.cos(az)
        y_a = r * np.cos(el) * np.sin(az)
        z_a = r * np.sin(el)

        pointA = self.aircraftPosition + np.column_stack((x_a, y_a, z_a))

        # Eliminate any point that exceeds competition volume - if a cuboid arena only possible if goto outside volume
        return pointA

    # Provide points along each route to evaluate risk at
    # Select route with minimum risk - If risk too high do something sensible
    def evaluateRouteRisk(self, gotoPoints):
        return 0, 0
        # Calculate vector between points aircraft -> goto & goto -> target

        # Linspace for number of points to evaluate. e.g. 10%, 20%, 30%...

        # Multiply vectors by linstpace to give all points to evaluate - don't double count goto position

        # Evaluate risk at every points

        # Split into routes and sum to give route risk

        # Normalise based on route distance -> shorter routes are prefered


if __name__ == "__main__":
    nav = navigation()

    nav.setTargetPosition((100,0,0))
    points = nav.generateEvaluationPoints()

    pass