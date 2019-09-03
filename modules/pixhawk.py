from enum import Enum
from .MAVLinkThread.mavlinkThread import mavThread, mavSerial, mavSocket
import pymavlink.dialects.v20.ardupilotmega as pymavlink
from pymavlink import mavutil

from threading import Thread
import time

class pixhawkAbstract(mavThread.mavThread, object):
    def __init__( self, conn, mavLib ):
        self._pixhawkTimeOffset = 0
        self._mode = 0
        self._armed = False
        self._home = [0,0,0]
        self._attitude = [0,0,0]
        self._position = [0,0,0]

        self.seenHeartbeat = False

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

            elif id == self._mavLib.MAVLINK_MSG_ID_AUTOPILOT_VERSION:
                print(msg)

            elif id == self._mavLib.MAVLINK_MSG_ID_STATUSTEXT:
                print(msg)
    
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

            self.seenHeartbeat = True

    def _systemTimeHandler(self, msg):
        self._pixhawkTimeOffset = msg.time_unix_usec - time.time()*1e6

    def _attitudeHandler(self, msg):
        self._attitude = [msg.roll, msg.pitch, msg.yaw]

    def _positionHandler(self, msg):
        self._position = [msg.lat, msg.lng, msg.altitude]

    def _homePosHandler( self, msg ):
        self._home = [msg.latitude, msg.longitude, msg.altitude]

        # self._home = [msg.x, msg.y, msg.z] # Could be this set if not using GPS

    # Aircraft state
    @property
    def UNIX_time(self):
        return int(time.time()*1e6)# - self._pixhawkTimeOffset)

    @property
    def armed(self):
        return self._armed

    @property
    def mode(self):
        return self._mode

    @property
    def relativePosition(self):
        pass
        # return self._position - self._home

    # Send messages
    def sendHeartbeat(self):
        msg = self._mavLib.MAVLink_heartbeat_message(self._mavLib.MAV_TYPE_ONBOARD_CONTROLLER, self._mavLib.MAV_AUTOPILOT_INVALID,0,0,0,1)
        self.queueOutputMsg(msg)

    def requestCapabilities(self):
        msg = self._mavLib.MAVLink_autopilot_version_request_message(1,1)
        self.queueOutputMsg(msg)

    def requestParams(self):
        msg = self._mavLib.MAVLink_param_request_list_message(1,1)
        self.queueOutputMsg(msg)

    def setArm(self, state):
        msg = self._mavLib.MAVLink_command_long_message(0,0,self._mavLib.MAV_CMD_COMPONENT_ARM_DISARM,0,state,0,0,0,0,0,0)
        self.queueOutputMsg(msg)
    
    def setModeGuided(self):
        self.setCustomMode(4)

    def setModeLand(self):
        self.setCustomMode(9)

    def setModePosHold(self):
        self.setCustomMode(16)

    def setCustomMode(self, cMode):
        msg = self._mavLib.MAVLink_command_long_message(0,0,self._mavLib.MAV_CMD_DO_SET_MODE,
                                    0,self._mavLib.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,cMode,0,0,0,0,0)
        self.queueOutputMsg(msg)

    # To test
    def setHome(self, use_current = 1):
        # 1 use current location, 0 use specificified location
        msg = self._mavLib.MAVLink_command_long_message( 0, 0, self._mavLib.MAV_CMD_DO_SET_HOME, 0, use_current, 0,0,0,0,0,0)
        self.queueOutputMsg(msg)

    def requestHome(self):
        msg = self._mavLib.MAVLink_command_long_message(0,0, self._mavLib.MAV_CMD_GET_HOME_POSITION, 0,0,0,0,0,0,0,0)
        self.queueOutputMsg(msg)
    
    def sendPosition(self, pos, rot):
        msg = self._mavLib.MAVLink_vision_position_estimate_message(self.UNIX_time, pos[0], pos[1], pos[2], 
                                                                rot[0], rot[1], rot[2])
        self.queueOutputMsg( msg, priority=1) # Highest priority

    def setTakeoff(self, alt):
        msg = self._mavLib.MAVLink_command_long_message(0,0,self._mavLib.MAV_CMD_NAV_TAKEOFF,0,0,0,0,0,0,0,alt)
        self.queueOutputMsg(msg)

    def sendConditionYaw(self, heading, rate=25, dir=1, offset=0):
        # heading in degrees
        # yaw rate in deg/s
        # dir 1 CW, -1 CCW
        # offset 1 relative, 0 absolute

        msg = self._mavLib.MAVLink_command_long_message(0, 0, self._mavLib.MAV_CMD_CONDITION_YAW, 0, 
                                                        heading, rate, dir, offset, 0,0,0)
        self.queueOutputMsg(msg)

    def sendSetGlobalOrigin(self,lat,lon,alt):
        msg = self._mavLib.MAVLink_set_gps_global_origin_message(0,lat,lon,alt)
        self.queueOutputMsg(msg)

    def sendSetHomePosition(self,lat,lon,alt):
        x = 0
        y = 0
        z = 0
        q = [1,0,0,0]
        approach_x = 0
        approach_y = 0
        approach_z = 1

        msg = self._mavLib.MAVLink_set_home_position_message(0,
            lat,lon,alt,
            x,y,z,q,
            approach_x,
            approach_y,
            approach_z)

        self.queueOutputMsg(msg)

if __name__ == "__main__":
    # Connect to pixhawk - write port is determined from incoming messages
    commObj = mavSocket.mavSocket(  listenAddress = ('localhost', 14550) )
    commObj.openPort()
    
    mavObj = pixhawkAbstract( conn = commObj, mavLib = pymavlink )

    # Start pixhawk connection
    pixThread = Thread( target = mavObj.loop )
    pixThread.daemon = True
    pixThread.start()

    print('***RUNNING***')

    # Wait until we have a complete connection
    while not commObj.isOpen() or not mavObj.seenHeartbeat:
        mavObj.sendHeartbeat()
        time.sleep(0.5)
        
    print('***CONNECTED***')

    mavObj.requestCapabilities()

    mavObj.setModeGuided()
    time.sleep(0.5)
    mavObj.setArm(True)
    time.sleep(0.5)
    mavObj.setTakeoff(10)

    time.sleep(10)
    
    mavObj.setModeLand()

    time.sleep(10)

    mavObj.stopLoop()
    commObj.closePort()
