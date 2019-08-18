from enum import Enum
from MAVLinkThread.mavlinkThread import mavThread, mavSerial, mavSocket
import pymavlink.dialects.v20.ardupilotmega as pymavlink
from pymavlink import mavutil

from threading import Thread
import time

class pixhawkAbstract(mavThread.mavThread, object):
    def __init__( self, conn, mavLib ):
        self._pixhawkTimeOffset = 0
        self._mode = 0
        self._armed = False
        self._inair = False
        self._home = [0,0,0]
        self._attitude = [0,0,0]
        self._position = [0,0,0]

        self.mode_mapping = {0: 'UNKNOWN'}

        super( pixhawkAbstract, self).__init__( conn, mavLib )

    # Process Messages
    def _processReadMsg(self, msglist):
        for msg in msglist:
            id = msg.get_msgId()
            if id == self._mavLib.MAVLINK_MSG_ID_HEARTBEAT:
                self._heartbeatHandler(msg)

            elif id == self._mavLib.MAVLINK_MSG_ID_SYSTEM_TIME:
                self._systemTimeHandler(msg)

            elif id == self._mavLib.MAVLINK_MSG_ID_HOME_POSITION:
                self._homePosHandler(msg)

            elif id == self._mavLib.MAVLINK_MSG_ID_AHRS2 or \
                id == self._mavLib.MAVLINK_MSG_ID_AHRS3:
                self._attitudeHandler(msg)
                self._positionHandler(msg)

            elif id == self._mavLib.MAVLINK_MSG_ID_ATTITUDE:
                self._attitudeHandler(msg)

            # Don't think this works
            elif id == self._mavLib.MAVLINK_MSG_ID_EXTENDED_SYS_STATE or \
                id == self._mavLib.MAVLINK_MSG_ID_HIGH_LATENCY:
                self._highLatencyHandler(msg)
    
    def _heartbeatHandler(self, msg): 
        if not msg.autopilot == self._mavLib.MAV_AUTOPILOT_INVALID:
            # Arm State
            if msg.base_mode & self._mavLib.MAV_MODE_FLAG_SAFETY_ARMED != 0:
                self._armed = True
            else:
                self._armed = False
            
            # Mode
            self._mode = mavutil.mode_string_v10(msg)
            self.mode_mapping = mavutil.mode_mapping_byname(msg.type)

    def _systemTimeHandler(self, msg):
        self._pixhawkTimeOffset = msg.time_unix_usec - time.time()*1e6

    def _attitudeHandler(self, msg):
        self._attitude = [msg.roll, msg.pitch, msg.yaw]

    def _positionHandler(self, msg):
        self._position = [msg.lat, msg.lng, msg.altitude]

    def _homePosHandler( self, msg ):
        self._home = [msg.latitude, msg.longitude, msg.altitude]

        # self._home = [msg.x, msg.y, msg.z] # Could be this set if not using GPS

    # Doesn't work :(
    def _highLatencyHandler(self, msg):
        if (msg.landed_state == pymavlink.MAV_LANDED_STATE_UNDEFINED or \
            msg.landed_state == pymavlink.MAV_LANDED_STATE_ON_GROUND):
            self._inair = False
        else:
            self._inair = True

    # Aircraft state
    @property
    def UNIX_time(self):
        return int(time.time()*1e6 - self._pixhawkTimeOffset)

    @property
    def armed(self):
        return self._armed

    @property
    def mode(self):
        return self._mode

    # Doesn't work...
    @property
    def inAir(self):
        return self._inair

    @property
    def relativePosition(self):
        pass
        # return self._position - self._home

    def sendHeartbeat(self):
        msg = pymavlink.MAVLink_heartbeat_message(pymavlink.MAV_TYPE_ONBOARD_CONTROLLER, pymavlink.MAV_AUTOPILOT_INVALID, 0,0, pymavlink.MAV_STATE_ACTIVE,2)
        self.queueOutputMsg(msg)

    # Send messages - Not implemented
    def setModeGuided(self):
        self._setMode('GUIDED')

    def setModeLand(self):
        self._setMode('LAND')

    def _setMode(self, custom_mode):
        # Only subset required - land, takeoff, guided
        mode = pymavlink.MAV_MODE_GUIDED_ARMED
        custom_mode = self.mode_mapping['GUIDED']
        msg = self._mavLib.MAVLink_command_long_message(1,0,self._mavLib.MAV_CMD_DO_SET_MODE,0,mode,custom_mode,0,0,0,0,0)
        self.queueOutputMsg(msg)

    def takeoff(self, alt):
            msg = pymavlink.MAVLink_command_long_message(0, 0, pymavlink.MAV_CMD_NAV_TAKEOFF, 0,0,0,0,0,0,0, alt)
            self.queueOutputMsg(msg)

    def setHome(self, use_current = 1):
        # 1 use current location, 0 use specificified location
        msg = self._mavLib.MAVLink_command_long_message( 0, 0, self._mavLib.MAV_CMD_DO_SET_HOME, 0, use_current, 0,0,0,0,0,0)
        self.queueOutputMsg(msg)

    def requestHome(self):
        msg = self._mavLib.MAVLink_command_long_message(0,0, self._mavLib.MAV_CMD_GET_HOME_POSITION, 0,0,0,0,0,0,0,0)
        self.queueOutputMsg(msg)
    
    def sendPosition(self, pos):
        msg = self._mavLib.MAVLink_vision_position_estimate_message(self.UNIX_time, pos[0], pos[1], pos[2], 
                                                                pos[3], pos[4], pos[5])
        self.queueOutputMsg( msg, priority=1) # Highest priority

    def sendConditionYaw(self, heading, rate=25, dir=1, offset=0):
        # heading in degrees
        # yaw rate in deg/s
        # dir 1 CW, -1 CCW
        # offset 1 relative, 0 absolute

        msg = self._mavLib.MAVLink_command_long_message(0, 0, self._mavLib.MAV_CMD_CONDITION_YAW, 0, 
                                                        heading, rate, dir, offset, 0,0,0)
        self.queueOutputMsg(msg)

    def requestHighLatency(self):
        msg = self._mavLib.MAVLink_command_long_message(0, 0, self._mavLib.MAV_CMD_CONTROL_HIGH_LATENCY, 0, 1, 0,0,0,0,0,0)
        self.queueOutputMsg(msg)


if __name__ == "__main__":
    # Connect to pixhawk
    commObj = mavSocket.mavSocket( port = 14550, listenAddress='localhost' )
    commObj.openPort()
    
    mavObj = pixhawkAbstract( conn = commObj, mavLib = pymavlink )
                              mavLib = pymavlink )

    # Start pixhawk connection
    pixThread = Thread( target = mavObj.loop )
    pixThread.daemon = True
    pixThread.start()

    try:
        time.sleep(5)
        mavObj.setModeGuided()
        print('Set Mode Guided')
        time.sleep(1)
        mavObj.takeoff(5)

    while not commObj.isOpen() or not mavObj.sendHeartbeat:
        mavObj.sendHeartbeat()
        time.sleep(0.5)

    except KeyboardInterrupt:
        pass

    mavObj.stopLoop()
    commObj.closePort()
