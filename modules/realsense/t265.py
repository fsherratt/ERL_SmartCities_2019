import pyrealsense2 as rs

class rs_t265:
    def __init__(self, framerate = 25, orientation = 0):
        # Setup
        pass

    def __enter__(self):
        self.openConnection()

    def __exit__(self):
        self.closeConnection()

    def getPose():
        # Wait for new frame

        # Fetch data

        # Condition and return
        pose = [0, 0, 0, 0, 0, 0] # 6 DOF pose data
        confidence = 0 # Quality of data

        return pose, confidence

    def openConnection(self):
        pass

    def closeConnection(self):
        pass