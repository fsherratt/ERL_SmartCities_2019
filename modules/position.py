from modules.MAVLinkThread.mavlinkThread import mavThread, mavSocket
from modules.realsense import t265

from scipy.spatial.transform import Rotation as R

import pymavlink.dialects.v20.ardupilotmega as pymavlink
import time

from threading import Thread

class position:
    def __init__(self, t265):
        self.t265 = t265

    def update(self):
        pos, r, conf = t265Obj.getFrame()

        return pos, r, conf


class sitlPosition(mavThread.mavThread):
    def __init__( self, conn, mavLib ):
        self._attitude = [0,0,0]
        self._position = [0,0,0]

        super( sitlPosition, self).__init__( conn, mavLib )


    def _processReadMsg(self, msglist):
        for msg in msglist:
            id = msg.get_msgId()

            if id == self._mavLib.MAVLINK_MSG_ID_HOME_POSITION:
                    self._homePosHandler(msg)

            elif id == self._mavLib.MAVLINK_MSG_ID_LOCAL_POSITION_NED:
                self._positionHandler(msg)

            elif id == self._mavLib.MAVLINK_MSG_ID_AHRS3 or \
                 id == self._mavLib.MAVLINK_MSG_ID_AHRS2 or \
                 id == self._mavLib.MAVLINK_MSG_ID_ATTITUDE:
                 self._attitudeHandler(msg)

            elif id == self._mavLib.MAVLINK_MSG_ID_ATTITUDE:
                self._attitudeHandler(msg)

    def _homePosHandler( self, msg ):
        self._home = [msg.latitude, msg.longitude, msg.altitude]

    def _attitudeHandler(self, msg):
        self._attitude = [msg.roll, msg.pitch, msg.yaw]

    def _positionHandler(self, msg):
        self._position = [msg.x, msg.y, msg.z]

    def update(self):
        r = R.from_euler('xzy', self._attitude, degrees=False)
        return self._position, r, 3


if __name__ == "__main__":
    SITL = True

    posObj = None
    
    if not SITL:
        t265 = t265.rs_t265( rotOffset=[-90,-90,0])
        t265.openConnection()

        posObj = position( t265 )

    else:
        commObj = mavSocket.mavSocket( listenAddress = ('', 14551) )
        commObj.openPort()

        posObj = sitlPosition( conn = commObj, mavLib = pymavlink )
        posObj.srcSystem = 21

        pixThread = Thread( target = posObj.loop )
        pixThread.daemon = True
        pixThread.start()

    try:
        while True:
            pos, r, _ = posObj.update()
            print(pos, r.as_euler('xzy', degrees=True))
            time.sleep(0.05)

    except KeyboardInterrupt:
        pass

    try:
        t265.closeConnection()
    except:
        pass