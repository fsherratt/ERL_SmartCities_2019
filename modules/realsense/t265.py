import pyrealsense2 as rs
import traceback
import sys

import numpy as np
import transformations as tf

class unexpectedDisconnect( Exception):
    # Camera unexpectably disconnected
    pass

class rs_t265:
    def __init__(self):
        # Setup variables
        self.pipe = None
        self.cfg = None

        # Adjust yaw to align north
        self.rot_Offset = np.deg2rad([0, 0, 20]) # roll, pitch yaw
        self.pos_Offset = [0, 0, 0] # x, y, z pixhawk coordinate system

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

            # Condition and return
            pos = [data.translation.x, data.translation.y, data.translation.z]
            quat = [data.rotation.w, data.rotation.x, data.rotation.y, data.rotation.z]
            conf = data.tracker_confidence

            # Calculate Euler angles from Quat - Quat is WXYZ
            eul = tf.euler_from_quaternion( quat, axes='sxyz')  

            return pos, eul, conf

        return None

    def correctOffset( self, pos, eul ):
        # Coordinates must be wrt pixhawk global coordinate system
    
        # euler[0] = rotation around 'x' RHR (pitch)
        # euler[1] = rotation around 'y' RHR (yaw)
        # euler[2] = rotation around 'z' RHR (roll)

        # pos[0] = 'x' axis perp to side, +ve towards USB (sway)
        # pos[1] = 'y' axis perp to top, +ve up (heave)
        # pos[2] = 'z' axis perp to front, +ve into front  (surge)

        # roll and pitch are about gravity vector - yaw is offset from startup 'ZYX' coordinate system

        # Transform into aircraft coordinates - maintaining right hand coordinate system
        pos = [-pos[2], -pos[0], pos[1]]
        eul = [-eul[2], -eul[0], eul[1]]

        # Apply offsets to align with pixhawk, no compass in T265 so north taken from pixhawk
        pos += self.pos_Offset
        eul += self.rot_Offset

        return pos, eul

    def calcNorthOffset( self, t265Yaw, pixYaw ):
        # Implement some form of gradient descent method to correct for yaw offset
        pass