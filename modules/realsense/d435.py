import pyrealsense2 as rs
import traceback
import sys

import numpy as np

class unexpectedDisconnect( Exception):
    # Camera unexpectably disconnected
    pass

class rs_d435:
    def __init__(self, width=640, height=480, framerate=6):
        self.width = width
        self.height = height

        self.framerate = framerate

        self.intrin = None
        self.scale = 1

        self._FOV = (0, 0)

        self.xDeprojectMatrix = None
        self.yDeprojectMatrix = None

    def __enter__(self):
        self.openConnection()

    def __exit__(self, exception_type, exception_value, traceback):
        if traceback:
            print(traceback.tb_frame)

        self.closeConnection()
    
    # --------------------------------------------------------------------------
    # openConnection
    # return void
    # --------------------------------------------------------------------------
    def openConnection(self):
        self.pipe = rs.pipeline()

        self.width = 640
        self.height = 480
        self.fps = 6

        self.cfg = rs.config()
        self.cfg.enable_stream( rs.stream.depth, self.width, self.height, \
                                rs.format.any, self.framerate )

        self.profile = self.pipe.start( self.cfg  )

        self.initialise_deprojection_matrix()

        print('rs_t265:D435 Connection Open')
    
    # --------------------------------------------------------------------------
    # closeConnection
    # return void
    # --------------------------------------------------------------------------
    def closeConnection(self):
        self.pipe.stop()
        
        print('rs_t265:D435 Connection Closed')

    # --------------------------------------------------------------------------
    # getIntrinsics
    # get camera intrinsics
    # return void
    # --------------------------------------------------------------------------
    def getIntrinsics( self ):
        profile = self.pipe.get_active_profile()

        self.intrin = profile.get_stream( rs.stream.depth ).as_video_stream_profile().get_intrinsics()
        self.scale = profile.get_device().first_depth_sensor().get_depth_scale()

        self.FOV = rs.rs2_fov( self.intrin )
        self.FOV = np.deg2rad( self.FOV )

    # --------------------------------------------------------------------------
    # initialise_deprojection_matrix
    # Conversion matrix from detpth to
    # return void
    # --------------------------------------------------------------------------
    def initialise_deprojection_matrix( self ):
        self.getIntrinsics()
        
        # Create deproject row/column vector
        self.xDeprojectRow = (np.arange( self.width ) - self.intrin.ppx) / self.intrin.fx
        self.yDeprojectCol = (np.arange( self.height ) - self.intrin.ppy) / self.intrin.fy

        # Tile across full matrix height/width
        self.xDeprojectMatrix = np.tile( self.xDeprojectRow, (self.height, 1) )
        self.yDeprojectMatrix = np.tile( self.yDeprojectCol, (self.width, 1) ).transpose()


    # --------------------------------------------------------------------------
    # getFrame
    # Retrieve a depth frame with scale metres from camera
    # return np.float32[width, height]
    # --------------------------------------------------------------------------
    def getFrame(self):
        frames = self.pipe.wait_for_frames()

        # Get depth data
        depth = frames.get_depth_frame()
        if not depth:
            return None

        depth_points = np.asarray( depth.get_data(), np.float32 )

        depth_points *= self.scale

        return depth_points

    # --------------------------------------------------------------------------
    # deproject_frame
    # Conversion depth frame to 3D local coordiate system in meters
    # return [[x,y,z]] coordinates of depth pixels
    # --------------------------------------------------------------------------
    def deproject_frame( self, frame ):
        Z = frame
        X = np.multiply( frame, self.xDeprojectMatrix )
        Y = np.multiply( frame, self.yDeprojectMatrix )

        return np.asanyarray( [X, Y, Z] )

    # --------------------------------------------------------------------------
    # range_filter
    # Filter out points that are out of range, np.nan is applied to out of range
    # values
    # return in range depth frame
    # --------------------------------------------------------------------------
    def range_filter( self, frame, minRange = 0, maxRange = 10 ):
        outOfRange = np.where( (frame < minRange) | (frame > maxRange) )
        frame[outOfRange] = np.nan

        return frame