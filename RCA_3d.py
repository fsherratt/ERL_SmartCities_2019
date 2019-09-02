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
from scipy import interpolate
import time
import os

import airTraffic

from uavAbstract import MODE

from common import mavLib as mavlink
from common import mavAbstract
from common import mavComm

# ------------------------------------------------------------------------------
# manager
#
# ------------------------------------------------------------------------------
class manager:
    # --------------------------------------------------------------------------
    # Public class level variables
    # --------------------------------------------------------------------------
    minAltitude_Relative = 30.0  # Minimum flight altitude relative to home
    maxAltitude_Relative = 100.0 # Maximum
    maxClimbRate = 15 * ( np.pi / 180 ) # Degrees

    uavVelocity = 21.0 # Todo make this based on actual vx, vy, vz velocity
    waypointRadius = 100 #  Waypoint completion radius

    pathMeshElements = 10 # Number of point to evaluate along each path
    elevationMeshElements = 10 # Number of elevation angles to evaluate
    azimuthMeshElements = 10 # Number of azimuth angles to evaluate

    CpDist = 200.0
    azimuthRange = 30 * ( np.pi / 180 )
    elevationRange = 10 * ( np.pi / 180 )

    # --------------------------------------------------------------------------
    # Private class level variables
    # --------------------------------------------------------------------------
    _numPaths = elevationMeshElements * azimuthMeshElements
    _numElements = 2 * _numPaths * pathMeshElements
    _numCoordinates = 3

    # Altitude limits are set when the aircraft home location is received
    _minAltitudeAbsolute = 0.0
    _maxAltitudeAbsolute = 1000.0


    # --------------------------------------------------------------------------
    # Public function definitions
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # __init__
    # Initializer
    # param null
    # return void
    # --------------------------------------------------------------------------
    def __init__( self ):
        self._targetPosition_UTM = (0, 0, 0)

        self._groundInterpFunc = None

    # --------------------------------------------------------------------------
    # update
    # Run update code for avoidance algorithm
    # param null
    # return void
    # --------------------------------------------------------------------------
    def update( self ):

        if self._UAV.mode is not MODE.GUIDED:
            return False

        gotoPoint = self._calculateChasePoint()

        return gotoPoint


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

        return math.sqrt(  ( start[0] - end[0] ) ** 2
                         + ( start[1] - end[1] ) ** 2
                         + ( start[2] - end[2] ) ** 2 )

    # --------------------------------------------------------------------------
    # Private function definitions
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # _calculateChasePoint
    # Calculates a coordinate to aim for that minimises risk along the path
    # to it and then to the next targetPosition
    # param null
    # return 3-tuple  x, y and z coordinates of the calculated point
    # --------------------------------------------------------------------------
    def _calculateChasePoint( self ):
        currTime = time.time()
        min_path_point = self._targetPosition_UTM

        uavPosition = np.asarray( self._UAV.uavLocation_UTM )
        targetPosition = np.asarray( self._targetPosition_UTM )

        # Calculate vector from aircraft to next point
        travelVector = targetPosition - uavPosition

        # How far have we got to go to reach waypoint
        pathLength = np.linalg.norm( travelVector )


        # ----------------------------------------------------------------------
        # Path A
        # ----------------------------------------------------------------------
        # Calculate heading to next WP
        az = np.arctan2( travelVector[1], travelVector[0] ) # Azimuth
        el = np.arcsin( travelVector[2] / pathLength ) # Elevation


        # Calculate groups of points radiating from aircraft in general
        # direction of the next way point (polar coordinates)
        az = np.linspace( az - self.azimuthRange,
                          az + self.azimuthRange,
                          self.azimuthMeshElements )

        el = np.linspace( el - self.elevationRange,
                          el + self.elevationRange,
                          self.elevationMeshElements )

        r = np.linspace( 0, self.CpDist, self.pathMeshElements + 1 )
        r = r[1:]

        timeToPointA = ( r / self.uavVelocity ) + currTime
        tOffset = timeToPointA[-1]

        el, az, r = np.meshgrid( el, az, r, indexing = 'ij' )

        r = np.reshape( r, np.size( r ) )
        el = np.reshape( el, np.size( el ) )
        az = np.reshape( az, np.size( az ) )

        # Conversion from polar to cartesian
        x_a = r * np.cos( el ) * np.cos( az )
        y_a = r * np.cos( el ) * np.sin( az )
        z_a = r * np.sin( el )

        # Evaluate points in path A
        pointA = uavPosition + np.column_stack( (x_a, y_a, z_a) )
        pointA = pointA.reshape( ( self._numPaths,
                                   self.pathMeshElements,
                                   self._numCoordinates ) )


        # ----------------------------------------------------------------------
        # Path B
        # ----------------------------------------------------------------------
        # Start point of line B is the point of line A
        startPointB = pointA[:, -1, :]

        vectorA = ( startPointB - uavPosition ) / self.CpDist

        # Calculate vectors from pointA to target WP
        vectorB = targetPosition - startPointB

        # Percentage distances along line, e.g. 10%, 20%, 30%,...
        ratio = np.linspace( 0, 1, self.pathMeshElements + 1 )
        ratio = ratio[1:]

        # Matrix magic to calculate points to get things to correct shapes
        ratio = np.tile( ratio, self._numPaths )
        ratio = np.tile( ratio, ( self._numCoordinates, 1 ) ).transpose()

        # Evaluate points in path B
        pointBAbs = np.repeat( vectorB, self.pathMeshElements, 0 ) * ratio
        pointB = np.repeat( startPointB, self.pathMeshElements, 0 ) + pointBAbs
        pointB = np.reshape( pointB, ( self._numPaths,
                                       self.pathMeshElements,
                                       self._numCoordinates ) )

        timeToPointB = ( tOffset
                       + np.linalg.norm( pointBAbs, axis = 1 )
                       / self.uavVelocity )

        points = np.concatenate( ( pointA, pointB ), axis = 1 )


        # ----------------------------------------------------------------------
        # Calculate path velocity vectors
        # ----------------------------------------------------------------------
        vectorLength = np.sqrt( vectorB[:, 0] ** 2
                              + vectorB[:, 1] ** 2
                              + vectorB[:, 2] ** 2 )

        vectorB /= np.tile( vectorLength, (self._numCoordinates, 1) ) \
                     .transpose()

        # Calculate velocty vector at each point
        velocityVectorA = vectorA * self.uavVelocity
        velocityVectorA = np.repeat(
                velocityVectorA.reshape( self._numPaths, 1,
                                         self._numCoordinates ),
                self.pathMeshElements, 1 )
        velocityVectorB = vectorB * self.uavVelocity
        velocityVectorB = np.repeat(
                velocityVectorB.reshape( self._numPaths, 1,
                                         self._numCoordinates ),
                self.pathMeshElements, 1 )

        velocityVector = np.concatenate( ( velocityVectorA, velocityVectorB ),
                                         axis = 1 )


        # ----------------------------------------------------------------------
        # Calculate prior consequence value
        # ----------------------------------------------------------------------
        priorRisk = self._groundInterpFunc( points.reshape(
                                ( self._numElements, self._numCoordinates ) ) )
        priorRisk = np.reshape( priorRisk, ( self._numPaths,
                                             2 * self.pathMeshElements ) )


        # ----------------------------------------------------------------------
        # Scale and sum risk
        # ----------------------------------------------------------------------
        risk = priorRisk + aircraftRisk
        risk += 1e-256 # Baseline risk to allow distance minimisation

        # Scale by length of segment
        risk[:, 0:self.pathMeshElements] *= self.CpDist
        risk[:, self.pathMeshElements:]  *= np.tile( vectorLength,
                                                     (self.pathMeshElements, 1)
                                                    ).transpose()
        risk /= self.pathMeshElements

        risk = np.sum( risk, axis = 1 )


        # ----------------------------------------------------------------------
        # Mark invalid paths
        # ----------------------------------------------------------------------
        # Limit min/max altitude
        risk[ ( startPointB[ :, 2 ] < manager._minAltitudeAbsolute )
            | ( startPointB[ :, 2 ] > manager._maxAltitudeAbsolute ) ] = np.nan

        # Limit min/max climb rates
        maxClimb = np.sin( self.maxClimbRate )
        risk[ ( np.fabs( vectorB[:, 2] ) > maxClimb ) ] = np.nan

        # ----------------------------------------------------------------------
        # Select path of minimum risk
        # ----------------------------------------------------------------------
        try:
            min_path_index = np.nanargmin( risk )
            min_path_point = startPointB[min_path_index]

        except ValueError:
            pass

        try:
            print( 'Risk = %f, t = %f' % ( risk[min_path_index],
                                           time.time() - currTime, ) )
        except:
            pass

        return tuple( min_path_point )

# ------------------------------------- EOF ------------------------------------
