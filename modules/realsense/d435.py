import pyrealsense2 as rs
import traceback
import sys

import numpy as np

class unexpectedDisconnect( Exception):
    # Camera unexpectably disconnected
    pass

class rs_t265:
    def __init__(self):
        pass

    def __enter__(self):
        self.openConnection()

    def __exit__(self, exception_type, exception_value, traceback):
        if traceback:
            print(traceback.tb_frame)

        self.closeConnection()

    def openConnection(self):
        self.pipe = rs.pipeline()

        self.width = 640
        self.height = 480
        self.fps = 6

        self.cfg = rs.config()
        self.cfg.enable_stream( rs.stream.depth, self.width, self.height, rs.format.any, self.fps )

        self.sensor = pipeline_profile = self.pipe.start( self.cfg  )

        self.getIntrinsics()

    def closeConnection(self):
        self.pipe.stop()

    def getIntrinsics( self ):
        profile = self.pipe.get_active_profile()
        profile = profile.get_stream( rs.stream.depth )

        self.intrin = profile.as_video_stream_profile().get_intrinsics()

        self.scale = self.sensor.get_depth_scale()

        self.FOV = rs.rs2_fov( self.intrin )
        self.FOV = np.deg2rad( self.FOV )

    def getFrame(self):
        frames = self.pipe.wait_for_frames()

        # Get depth data
        depth = frames.get_depth_frame()
        if not depth:
            return None

        depth_points = np.asarray( depth.get_data(), np.float32 )

        # Convert to meters
        depth_points *= self.scale

        return depth_pointss