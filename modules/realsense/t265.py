import pyrealsense2 as rs
import traceback
import sys

class unexpectedDisconnect( Exception):
    # Camera unexpectably disconnected
    pass

class rs_t265:
    def __init__(self):
        # Setup variables
        self.pipe = None
        self.cfg = None

    def __enter__(self):
        self.openConnection()

    def __exit__(self, exception_type, exception_value, traceback):
        if traceback:
            print(traceback.tb_frame)

        self.closeConnection()

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

            return pos, quat, conf

        return None

    def openConnection(self):
        # Declare RealSense pipeline, encapsulating the actual device and sensors
        self.pipe = rs.pipeline()

        # Build config object and request pose data
        self.cfg = rs.config()
        self.cfg.enable_stream(rs.stream.pose)
        # How set frame rate, how select data

        # Start streaming with requested config
        self.pipe.start(self.cfg)

    def closeConnection(self):
        self.pipe.stop()
    