import pyrealsense2 as rs

class rs_t265:
    def __init__(self):
        # Setup variables
        self.pipe = None
        self.cfg = None

    def __enter__(self):
        self.openConnection()

    def __exit__(self, exception_type, exception_value, traceback):
        if traceback:
            print(exception_type, exception_value)
            print(traceback.tb_frame)

        self.closeConnection()

    def getPose(self):
        # Wait for new frame
        frames = self.pipe.wait_for_frames()

        # Fetch data
        pose = frames.get_pose_frame()

        if pose:
            data = pose.get_pose_data()

            # Condition and return
            pose = [data.translation.x, data.translation.y, data.translation.z, \
                    data.rotation.w, data.rotation.x, data.rotation.y, data.rotation.z] # 6 DOF pose data

            confidence = data.tracker_confidence # Quality of data

            return pose, confidence

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
    