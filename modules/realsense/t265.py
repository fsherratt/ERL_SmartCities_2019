import pyrealsense2 as rs
import traceback
import sys

import numpy as np
from scipy.spatial.transform import Rotation as R

class unexpectedDisconnect( Exception):
    # Camera unexpectably disconnected
    pass

class rs_t265:
    def __init__(self, posOffset=[0,0,0], rotOffset=[90,90,0]):
        # Setup variables
        self.pipe = None
        self.cfg = None

        # Adjust yaw to align north
        self.pos_offset = posOffset
        self.rot_offset = rotOffset

        self.ROffset = R.from_euler('zyx', self.rot_offset, degrees=True) # roll, pitch yaw

    def __enter__(self):
        self.openConnection()

    def __exit__(self, exception_type, exception_value, traceback):
        if traceback:
            print(traceback.tb_frame)

        self.closeConnection()

    def openConnection(self):
        # Declare RealSense pipeline, encapsulating the actual device and sensors
        self.pipe = rs.pipeline()

        # Build config object and request pose data
        self.cfg = rs.config()
        self.cfg.enable_stream(rs.stream.pose)
        # How set frame rate, how select data

        # Start streaming with requested config
        self.pipe.start(self.cfg)

        print('rs_t265:T265 Connection Open')

    def closeConnection(self):
        self.pipe.stop()

        print('rs_t265:T265 Connection Closed')

    def getFrame(self):
        # Wait for new frame
        try:
            frames = self.pipe.wait_for_frames()
        except RuntimeError as e:
            traceback.print_exc(file=sys.stdout)
            raise unexpectedDisconnect( e )

        # Fetch data
        pose = frames.get_pose_frame()

        if pose:
            data = pose.get_pose_data()

            pos = [data.translation.x, data.translation.y, data.translation.z]
            quat = [data.rotation.x, data.rotation.y, data.rotation.z, data.rotation.w]
            conf = data.tracker_confidence

            # Calculate Euler angles from Quat - Quat is WXYZ
            rot = R.from_quat( quat )

            # Apply pixhawk rotational offset
            pos = self.ROffset.apply(pos)

            return pos, rot, conf

        return None

    def calcNorthOffset( self, t265Yaw, pixYaw ):
        # Implement some form of gradient descent method to correct for yaw offset
        pass

if __name__ == "__main__":
    t265Obj = rs_t265()

    with t265Obj:
        while True:
            pos, eul, conf = t265Obj.getFrame()
            # print(i, pos, conf)

            pos, eul = t265Obj.correctOffset( pos, eul )

            print(pos)