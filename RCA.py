# ------------------------------------------------------------------------------
# RCA.py
# Real time collision avoidance. Code is heavily based on original work by Paul
# Hetherington
#
# Author: Freddie Sherratt
# Created: 03.01.2018
# Last Modified: 03.01.2018
#
# Change List
# 03.01.2018 - Version 1 - FS
# ------------------------------------------------------------------------------
import math
import numpy as np
import time
from common import mavLib as mavlink

from uavAbstract import MODE

from gpiozero import LED


# ------------------------------------------------------------------------------
# manager
#
# ------------------------------------------------------------------------------
class manager:
    # --------------------------------------------------------------------------
    # Public class level variables
    # --------------------------------------------------------------------------
    minAltitude_Relative = 30.0  # Minimum flight altitude relative to home
    maxAltitude_Relative = 100.0  # Maximum
    maxClimbRate = 15 * (np.pi / 180)  # Degrees

    waypointRadius = 4  # Waypoint completion radius

    pathMeshElements = 50  # Number of point to evaluate along each path
    elevationMeshElements = 1  # Number of elevation angles to evaluate
    azimuthMeshElements = 20  # Number of azimuth angles to evaluate

    maxCpDist = 25
    minCpDist = 0.5
    azimuthRange = np.deg2rad( 100 )
    elevationRange = 0

    riskBaseline = 1e-256

    # --------------------------------------------------------------------------
    # Private class level variables
    # --------------------------------------------------------------------------
    _numPaths = elevationMeshElements * azimuthMeshElements
    _numElements = 2 * _numPaths * pathMeshElements
    _numCoordinates = 3

    # --------------------------------------------------------------------------
    # Public function definitions
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # __init__
    # Initializer
    # param null
    # return void
    # --------------------------------------------------------------------------
    def __init__( self, UAV, mapObj ):
        self._UAV = UAV
        self._map = mapObj  # Dynamic risk map

        self._targetMissionNum = None
        self._targetPosition_UTM = None
        self._chasePoint = (0, 0, 0)

        self._lastPos_UTM = (0, 0, 0)

        self.currentRisk = 0

        self.rLED = LED(26)
        self.rLED.off()

    # --------------------------------------------------------------------------
    # update
    # Run update code for avoidance algorithm
    # param null
    # return void
    # --------------------------------------------------------------------------
    def update( self ):
        if self._UAV.mode is not MODE.GUIDED:
            return False

        if self._UAV.missionCount == 0:
            try:
                self._UAV.reloadMission()
            except self._UAV.WaypointLoadError:
                return False

        try:
            self._checkWpProgress()

            self._directAircraft()
        except Exception as e:
            print(e)

        self.rLED.toggle()

    # --------------------------------------------------------------------------
    # reloadTarget
    # Reload target waypoint, called when mission items are force reloaded
    # param null
    # return void
    # --------------------------------------------------------------------------
    def reloadTarget( self ):
        self._targetPosition_UTM = self._UAV.targetMissionLocation_UTM
        self._UAV.goTo_UTM( self._targetPosition_UTM )

    # --------------------------------------------------------------------------
    # distanceToWp
    # Calculate norm2 of two (3-tuples)
    # param point - Point currently at (3-tuple)
    # param target - Point you aiming for (3-tuple)
    # return void
    # --------------------------------------------------------------------------
    @staticmethod
    def pointDistance( start, end ):
        if start is None or end is None:
            return None

        return math.sqrt( (start[0] - end[0]) ** 2
                          + (start[1] - end[1]) ** 2
                          + (start[2] - end[2]) ** 2 )

    # --------------------------------------------------------------------------
    # Private function definitions
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # _directAircraft
    # Call collision avoidance algorithm and use output to set new target
    # location
    # param null
    # return void
    # --------------------------------------------------------------------------
    def _directAircraft( self ):
        cP_UTM, heading = self._calculateChasePoint()
        self._chasePoint = cP_UTM

        if cP_UTM is not None:
            self._UAV.goTo_UTM( cP_UTM )

        if heading is not None:
            self._UAV.condition_yaw( heading )

        # self._UAV.sendADSB( cP_UTM, heading )

    # --------------------------------------------------------------------------
    # _checkWpProgress
    # Check if we have passed through a waypoint, if we have set a new target
    # mission item and location
    # param null
    # return void
    # --------------------------------------------------------------------------
    def _checkWpProgress( self ):
        if self._targetMissionNum is None or self._targetPosition_UTM is None:
            self._targetMissionNum = self._UAV.targetMissionIndex
            self._targetPosition_UTM = self._UAV.targetMissionLocation_UTM

        # Have we hit the waypoint
        dist = self.pointDistance( self._targetPosition_UTM,
                                   self._UAV.uavLocation_UTM )
        print("Distance to WP %d is %fm" % (self._targetMissionNum + 1, dist))

        if dist <= self.waypointRadius:
            print('WP %d Complete' % (self._targetMissionNum + 1))
            self._setNewTarget()

        # ----------------------------------------------------------------------
        # Update where we are aiming for
        if (not self._targetMissionNum == self._UAV.targetMissionIndex and
                self._UAV.targetMissionIndex is not None):

            try:
                self._targetPosition_UTM = self._UAV.targetMissionLocation_UTM
                self._targetMissionNum = self._UAV.targetMissionIndex

            except (TypeError, ValueError):
                pass

    # --------------------------------------------------------------------------
    # _setNewTarget
    # Update target mission item based of current item
    # param null
    # return void
    # --------------------------------------------------------------------------
    def _setNewTarget( self ):
        newWP = self._targetMissionNum + 1

        # If we've run out of things to do
        if newWP >= self._UAV.missionCount:
            self._UAV.mode = MODE.LOITER
            return False

        currWPItem = self._UAV.getMissionItem( self._targetMissionNum )
        nextWPItem = self._UAV.getMissionItem( newWP )

        if currWPItem.command == mavlink.MAV_CMD_NAV_LOITER_UNLIM:
            self._UAV.mode = MODE.LOITER

        elif (nextWPItem.command == mavlink.MAV_CMD_NAV_WAYPOINT
              or nextWPItem.command == mavlink.MAV_CMD_NAV_LOITER_UNLIM):
            self._UAV.targetMissionIndex = newWP

        elif nextWPItem.command == mavlink.MAV_CMD_DO_JUMP:
            self._UAV.targetMissionSeq = nextWPItem.param1

        else:
            self._UAV.mode = MODE.RTL

    # --------------------------------------------------------------------------
    # _calculateChasePoint
    # Calculates a coordinate to aim for that minimises risk along the path
    # to it and then to the next targetPosition
    # param null
    # return 3-tuple  x, y and z coordinates of the calculated point
    # --------------------------------------------------------------------------
    def _calculateChasePoint( self ):
        currTime = time.time()

        min_path_index = 0
        min_path_point = self._targetPosition_UTM
        cpHeading = 0

        uavPosition = np.asarray( self._UAV.uavLocation_UTM )
        targetPosition = np.asarray( self._targetPosition_UTM )

        # Calculate vector from aircraft to next point
        travelVector = targetPosition - uavPosition

        # How far have we got to go to reach waypoint
        pathLength = np.linalg.norm( travelVector ) * 0.25

        # Limit how far ahead we plan
        if pathLength > self.maxCpDist:
            pathLength = self.maxCpDist

        elif pathLength < self.minCpDist:
            pathLength = self.minCpDist

        # ----------------------------------------------------------------------
        # Path A
        # ----------------------------------------------------------------------
        # Calculate heading to next WP
        heading = np.arctan2( travelVector[1], travelVector[0] )  # Azimuth

        # Calculate groups of points radiating from aircraft in general
        # direction of the next way point (polar coordinates)
        az = np.linspace( heading - self.azimuthRange,
                          heading + self.azimuthRange,
                          self.azimuthMeshElements )

        r = np.linspace( 0, pathLength, self.pathMeshElements + 1 )
        r = r[1:]

        az, r = np.meshgrid( az, r, indexing = 'ij' )

        r = np.reshape( r, np.size( r ) )
        az = np.reshape( az, np.size( az ) )

        # Conversion from polar to cartesian
        x_a = r * np.cos( az ) + uavPosition[0]
        y_a = r * np.sin( az ) + uavPosition[1]
        z_a = np.tile( targetPosition[2], self._numElements / 2 )

        # Evaluate points in path A
        pointA = np.column_stack( (x_a, y_a, z_a) )
        pointA = pointA.reshape( (self._numPaths,
                                  self.pathMeshElements,
                                  self._numCoordinates) )

        # ----------------------------------------------------------------------
        # Path B
        # ----------------------------------------------------------------------
        # Start point of line B is the point of line A
        startPointB = pointA[:, -1, :]

        # Calculate vectors from pointA to target WP
        vectorB = targetPosition - startPointB

        # Percentage distances along line, e.g. 10%, 20%, 30%,...
        ratio = np.linspace( 0, 1, self.pathMeshElements + 1 )
        ratio = ratio[1:]

        # Matrix magic to calculate points to get things to correct shapes
        ratio = np.tile( ratio, self._numPaths )
        ratio = np.tile( ratio, (self._numCoordinates, 1) ).transpose()

        # Evaluate points in path B
        pointBAbs = np.repeat( vectorB, self.pathMeshElements, 0 ) * ratio
        pointB = np.repeat( startPointB, self.pathMeshElements, 0 ) + pointBAbs
        pointB = np.reshape( pointB, (self._numPaths,
                                      self.pathMeshElements,
                                      self._numCoordinates) )

        points = np.concatenate( (pointA, pointB), axis = 1 )

        # ----------------------------------------------------------------------
        # Calculate prior consequence value
        # ----------------------------------------------------------------------
        interpPoints = points.reshape( (self._numElements, self._numCoordinates) )

        priorRisk = self._map.interpolatePoint_UTM( interpPoints )
        priorRisk = np.reshape( priorRisk, (self._numPaths,
                                            2 * self.pathMeshElements) )

        # ----------------------------------------------------------------------
        # Scale and sum risk
        # ----------------------------------------------------------------------
        risk = priorRisk
        risk += self.riskBaseline  # Baseline risk to allow distance minimisation

        vectorBLength = np.sqrt( vectorB[:, 0] ** 2 + vectorB[:, 1] ** 2 + vectorB[:, 2] ** 2 )

        # Scale by length of segment
        risk[:, 0:self.pathMeshElements] *= pathLength
        risk[:, self.pathMeshElements:] *= np.tile( vectorBLength,
                                                    (self.pathMeshElements, 1)
                                                    ).transpose()
        risk /= self.pathMeshElements

        risk = np.sum( risk, axis = 1 )

        # ----------------------------------------------------------------------
        # Select path of minimum risk
        # ----------------------------------------------------------------------
        try:
            min_path_index = np.nanargmin( risk )
            min_path_point = startPointB[min_path_index]

            self.currentRisk = risk[min_path_index]
        except ValueError:
            pass
        except Exception as e:
            print(e.message)

        try:
            # Set aircraft heading
            if pathLength > 2:
                cpHeading = np.arctan2( (min_path_point[1] - uavPosition[1]),
                                      (min_path_point[0] - uavPosition[0]) )
            else:
                cpHeading = heading

            if cpHeading < 0:
                cpHeading += 2*np.pi

            cpHeading = np.rad2deg( cpHeading )

            print('Risk = %f, Heading %f' % ( risk[min_path_index], cpHeading ) )

        except ValueError:
            pass
        except Exception as e:
            print( e.message )

        return tuple( min_path_point ), cpHeading

# ------------------------------------- EOF ------------------------------------
