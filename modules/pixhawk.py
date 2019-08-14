from enum import Enum
from MAVLinkThread.mavlinkThread import mavThread, mavSerial, mavSocket
from pymavlink.dialects.v20 import ardupilotmega as pymavlink
from pymavlink import mavutil

from threading import Thread
import time

import queue

class Mode(Enum):
    STABALISED = 0
    POS_HOLD = 1
    GUIDED = 2
    LAND = 3
    INITIALISING = 4

class pixhawkAbstract(mavThread.mavThread, object):
    def __init__( self, conn, mavLib ):
        self._mode = 0
        self._armed = False

        super( pixhawkAbstract, self).__init__( conn, mavLib )

    def _processReadMsg(self, msglist):
        for msg in msglist:
            if msg.get_msgId() == self._mavLib.MAVLINK_MSG_ID_HEARTBEAT:
                self._heartbeatHandler(msg)

    def _heartbeatHandler( self, msg ):
        if not msg.autopilot == self._mavLib.MAV_AUTOPILOT_INVALID:
            # Arm State
            if msg.base_mode & self._mavLib.MAV_MODE_FLAG_SAFETY_ARMED != 0:
                if not self._armed:
                self._armed = True

            else:
                if self._armed:
                self._armed = False
            
            # Mode
            mode_mapping = mavutil.mode_mapping_bynumber(msg.type)
            self._mode = mode_mapping[msg.custom_mode]

    @property
    def armed(self):
        return self._armed

    @property
    def mode(self):
        return self._mode

if __name__ == "__main__":
    # Connect to pixhawk
    commObj = mavSocket.mavSocket( broadcastPort = 14551, 
                                    listenPort = 14550 )
    
    mavObj = pixhawkAbstract( conn = commObj, 
                              mavLib = pymavlink )

    # Start pixhawk connection
    pixThread = Thread( target = mavObj.loop )
    pixThread.daemon = True
    pixThread.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        pass

    mavObj.stopLoop()
    commObj.closePort()