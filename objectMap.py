# ------------------------------------------------------------------------------
# realsense.py
# Abstraction layer for realsense camera
#
# Author: Freddie Sherratt
# Created: 05.02.2019
# Last Modified: 05.02.2019
#
# Change List
#
# ------------------------------------------------------------------------------

import pyrealsense2 as rs
import numpy as np
import os
from common import GPSUtil
import time
from scipy import interpolate

import matplotlib.pyplot as plt
from matplotlib.patches import Circle

from common import mavComm, mavAbstract


# ------------------------------------------------------------------------------
# CAMERA
# Class to realsensor camera abstract
# ------------------------------------------------------------------------------
class camera:
    # --------------------------------------------------------------------------
    # __init__
    # param self -
    # return void
    # --------------------------------------------------------------------------
    def __init__( self, reducedRange=False ):
        self._reducedRange = reducedRange
        self._pipeline = rs.pipeline()

        self._height = 0
        self._width = 0
        self._scale = 1

        self._FOV = (0, 0)

        self._start = False

        self.columns = np.arange( 30, 640 )
        self.rows = 240

        self._sensor = None
        self._intrin = None

        self._X = None
        self._Y = None
        self._Z = None

        self._ports = mavComm.MAVAbstract.portDict

    def setReducedRange( self, val ):
        self._reducedRange = val

    # --------------------------------------------------------------------------
    # start
    # param self -
    # param value - attribute value
    # return void
    # --------------------------------------------------------------------------
    def start( self ):
        if self._start:
            return False

        config = rs.config()
        config.disable_all_streams()
        config.enable_stream( rs.stream.depth, 640, 480, rs.format.any, 6 )

        pipeline_profile = self._pipeline.start( config )
        self._sensor = pipeline_profile.get_device().first_depth_sensor()

        self._start = True

        self.getIntrinsics()  # Get information about stream
        self.deprojectInit()

        self._sensor.set_option( rs.option.enable_auto_exposure, False )
        self._sensor.set_option( rs.option.exposure, 120 )
        self._sensor.set_option( rs.option.laser_power, 360 )

        return True

    # --------------------------------------------------------------------------
    # stop
    # param self -
    # return void
    # --------------------------------------------------------------------------
    def stop( self ):
        if self._start:
            self._pipeline.stop()

    # --------------------------------------------------------------------------
    # getIntrinsics
    # param self -
    # return void
    # --------------------------------------------------------------------------
    def getIntrinsics( self ):
        profile = self._pipeline.get_active_profile()
        profile = profile.get_stream( rs.stream.depth )

        self._intrin = profile.as_video_stream_profile().get_intrinsics()

        self._height = self._intrin.height
        self._width = self._intrin.width
        self._scale = self._sensor.get_depth_scale()

        self._FOV = rs.rs2_fov( self._intrin )

        self._FOV = np.deg2rad( self._FOV )

    # --------------------------------------------------------------------------
    # getFrame
    # Retrieve depth frame and convert to 3D coordinates
    # param self -
    # return void
    # --------------------------------------------------------------------------
    def getFrame( self ):
        frames = self._pipeline.wait_for_frames()

        # Get depth data
        frame = frames.get_depth_frame()
        depth_points = np.asarray( frame.get_data(), np.float32 )

        # Convert to meters
        depth_points *= self._scale

        if self._reducedRange:
            depth_points[ depth_points > 1] = 0
            depth_points *= 10

        return depth_points

    # --------------------------------------------------------------------------
    # getDepthFrame3D
    # Retrieve depth frame and convert to 3D coordinates
    # param self -
    # return void
    # --------------------------------------------------------------------------
    def getDepthFrame3D( self ):
        frame = self.getFrame()

        frame = frame[self.rows, :]
        # frame2 = np.zeros( 640 )
        #
        # for i in range(2,639):
        #     if all(t != 0 for t in frame[i - 1:i + 1]):
        #         frame2[i] += (frame[i - 1] + frame[i + 1]) * 0.5
        #         frame2[i] /= 2
        #
        # frame = frame2

        wh = np.where( (frame > 0) & (frame < 10) )
        wh = wh[0]
        frame = frame[wh]

        bins = [0, 90, 180, 270, 360, 450, 540, 641]
        minimum = np.zeros(7)

        for i in range( len(bins) - 1):
            try:
                elem = (wh > bins[i]) & (wh < bins[i+1])
                minimum[i] = np.amin( frame[elem] )
            except Exception as e:
                minimum[i] = 15

        frame3D = self.deprojectFrame( frame, self.rows, wh )

        return frame3D, minimum

    # --------------------------------------------------------------------------
    # getPixels
    # Retrieve depth frame and convert to 3D coordinates
    # return void
    # --------------------------------------------------------------------------
    def getPixels( self ):
        return self._width, self._height

    # --------------------------------------------------------------------------
    # deprojectInit
    # Retrieve depth frame and convert to 3D coordinates
    # return void
    # --------------------------------------------------------------------------
    def deprojectInit( self ):
        self._X = (np.arange( self._width ) - self._intrin.ppx) / self._intrin.fx
        self._Y = (np.arange( self._height ) - self._intrin.ppy) / self._intrin.fy
        self._Z = np.ones( (self._width, self._height) )

        self._Y = np.tile( self._Y, (self._width, 1) ).transpose()
        self._X = np.tile( self._X, (self._height, 1) )

    # --------------------------------------------------------------------------
    # deprojectFrame
    # Retrieve depth frame and convert to 3D coordinates
    # return void
    # --------------------------------------------------------------------------
    def deprojectFrame( self, frame, row, columns ):
        # Local coordinates in global rotational frame
        xDeprojectMatrix = self._X[row, columns]
        yDeprojectMatrix = self._Y[row, columns]

        X = frame  # + north
        Y = np.multiply( frame, xDeprojectMatrix )
        Z = np.multiply( frame, yDeprojectMatrix )

        return np.asanyarray( [X, Y, Z] )


# ------------------------------------------------------------------------------
# MAP
# Camera
# ------------------------------------------------------------------------------
class riskMap:
    nDivisions = 150  # North divisions
    eDivisions = 120  # East divisions

    # Grid limits (Lat, Lon) ERL Competition Site
    GL_NorthEast_GPS = (37.2003074, -5.8804150, 0)
    GL_SouthWest_GPS = (37.1988679, -5.8817616, 0)

    # Courtyard
    # GL_NorthEast_GPS = (37.2009025, -5.8789125, 0)
    # GL_SouthWest_GPS = (37.2000896, -5.8802967, 0)
    #
    # OOB_NorthEast_GPS = (37.2008490, -5.8789950, 0)
    # OOB_SouthWest_GPS = (37.2001602, -5.8801867, 0)

    # # Grass area
    # GL_NorthEast_GPS = (37.2003770, -5.8800244, 0)
    # GL_SouthWest_GPS = (37.1990140, -5.8806467, 0)

    # OOB_NorthEast_GPS = (37.2010943, -5.8799366, 0)
    # OOB_SouthWest_GPS = (37.1995931, -5.8814038, 0)


    # --------------------------------------------------------------------------
    # __init__
    # return void
    # --------------------------------------------------------------------------
    def __init__( self, enablePlotting ):
        # Create grid between defined coordinates
        NorthEast_UTM = GPSUtil.GPStoUTM( self.GL_NorthEast_GPS )
        SouthWest_UTM = GPSUtil.GPStoUTM( self.GL_SouthWest_GPS )

        self.nBins = np.linspace( SouthWest_UTM[0], NorthEast_UTM[0], self.nDivisions )
        self.eBins = np.linspace( SouthWest_UTM[1], NorthEast_UTM[1], self.eDivisions )

        rootDir = os.path.dirname(os.path.abspath(__file__))
        self.grid = np.loadtxt(rootDir + '/risk.csv', delimiter=',')

        self.grid *= 40

        # Create interpolation function
        self.interpFunc = interpolate.RegularGridInterpolator( (self.nBins, self.eBins),
                                                               self.grid, method = 'linear',
                                                               bounds_error = False,
                                                               fill_value = np.nan )

        self._enablePlotting = enablePlotting

        if self._enablePlotting:
            # Initialise plotter
            plt.ion()
            self._fig = plt.figure()
            self._ax = self._fig.add_subplot(111)

    # --------------------------------------------------------------------------
    # mapObstacles
    # param self -
    # return void
    # --------------------------------------------------------------------------
    def mapRisk( self, frame, yaw, UTM ):

        # Transform to global coordinates
        frameGlobal = self.transformCoordinates( frame, yaw, UTM )

        # Create grid on new risk
        newGrid = np.zeros((self.nDivisions, self.eDivisions), float)

        # Sort into bins
        nSort = np.digitize( frameGlobal[0, :], self.nBins ) - 1
        eSort = np.digitize( frameGlobal[1, :], self.eBins ) - 1
        nnSort = nSort + 1
        snSort = nSort - 1
        eeSort = eSort + 1
        weSort = eSort - 1

        try:
            np.add.at(newGrid, [nSort, eSort], 1)

            np.add.at(newGrid, [nnSort, eSort], 0.5)
            np.add.at(newGrid, [snSort, eSort], 0.5)
            np.add.at(newGrid, [nSort, eeSort], 0.5)
            np.add.at(newGrid, [nSort, weSort], 0.5)

            np.add.at(newGrid, [nnSort, eeSort], 0.3)
            np.add.at(newGrid, [snSort, eeSort], 0.3)
            np.add.at(newGrid, [nnSort, weSort], 0.3)
            np.add.at(newGrid, [snSort, weSort], 0.3)

            self.grid += newGrid
        except:
            pass

        if self._enablePlotting:
            self.plotRiskMap( UTM )

    # --------------------------------------------------------------------------
    # plotRiskMap
    # param self -
    # return void
    # --------------------------------------------------------------------------
    def plotRiskMap( self, UTM ):
        quadN = np.digitize( UTM[0], self.nBins )
        quadE = np.digitize( UTM[1], self.eBins )

        plt.cla()
        plt.imshow( self.grid, cmap = 'hot', interpolation = 'nearest' )
        circ = Circle( (quadE, quadN), 5 )
        self._ax.add_patch( circ )
        plt.draw()
        plt.pause( 0.1 )

    # --------------------------------------------------------------------------
    # transformCoordinates
    # param self -
    # return void
    # --------------------------------------------------------------------------
    @staticmethod
    def transformCoordinates( frame, yaw, UTM ):
        X = frame[0, :] * np.cos( yaw ) - frame[1, :] * np.sin( yaw )
        Y = frame[0, :] * np.sin( yaw ) + frame[1, :] * np.cos( yaw )

        X += UTM[0]
        Y += UTM[1]

        frameGlob = np.asanyarray( [X, Y] )
        return frameGlob

    # --------------------------------------------------------------------------
    # interpolatePoint_UTM
    # param self -
    # return void
    # --------------------------------------------------------------------------
    def interpolatePoint_UTM( self, queryPoints ):
        points2D = queryPoints[:, 0:2]

        return self.interpFunc( points2D )

    # --------------------------------------------------------------------------
    # save
    # param self -
    # return void
    # --------------------------------------------------------------------------
    def save( self ):

        rootDir = os.path.dirname(os.path.abspath(__file__)) + '/Logs/'

        i = 0
        while os.path.exists(rootDir + ("heatmap_%03d.csv" % i)):
            i += 1

        fileName = rootDir + ('heatmap_%03d' % i)

        np.savetxt( fileName + '.csv', self.grid, delimiter="," )
        np.save( fileName + '.npy', self.grid, allow_pickle=False )

        print('Saving Heatmap')


# ------------------------------------- EOF ------------------------------------
