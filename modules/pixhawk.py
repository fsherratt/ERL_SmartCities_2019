from enum import Enum
from modules.MAVLinkThread.mavlinkThread import mavThread, mavSerial, mavSocket
import pymavlink.dialects.v20.ardupilotmega as pymavlink
from pymavlink import mavutil

from threading import Thread
import time

class pixhawkAbstract(mavThread.mavThread, object):
    home_lat = 151261321 # Somewhere in Africa
    home_lon = 16624301  # Somewhere in Africa
    home_alt = 163000

    def __init__( self, conn ):
        self._pixhawkTimeOffset = 0
        self._mode = 0
        self._armed = False
        self._home = [0,0,0]

        self.seenHeartbeat = False
        self.lastSentHeartbeat = 0

        self._heading_north_yaw = None

        super( pixhawkAbstract, self).__init__( conn, pymavlink )

    def _loopInternals(self):
        super( pixhawkAbstract, self)._loopInternals()

        if time.time() - self.lastSentHeartbeat > 0.5:
            self.sendHeartbeat()
            self.lastSentHeartbeat = time.time()
            # self.getHomePosition()

    # Process Messages
    def _processReadMsg(self, msglist):
        for msg in msglist:
            id = msg.get_msgId()
            if id == self._mavLib.MAVLINK_MSG_ID_HEARTBEAT:
                self._heartbeatHandler(msg)

            elif id == self._mavLib.MAVLINK_MSG_ID_ATTITUDE:
                self._attitudeHandler(msg)

            elif id == self._mavLib.MAVLINK_MSG_ID_STATUSTEXT:
                print(msg)

            elif id == self._mavLib.MAVLINK_MSG_ID_HOME_POSITION:
                self._homeHandler(msg)

            elif id == pymavlink.MAVLINK_MSG_ID_COMMAND_ACK:
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

            self.seenHeartbeat = True

    def _attitudeHandler(self, msg):
        self._heading_north_yaw = msg.yaw

    def _homeHandler(self, msg):
        self._home = [msg.x, msg.y, msg.z]

    @property
    def home(self):
        return self._home

    @property
    def compass_heading(self):
        return self._heading_north_yaw

    # Aircraft state
    @property
    def armed(self):
        return self._armed

    @property
    def mode(self):
        return self._mode

    # Send messages
    def sendHeartbeat(self):
        msg = self._mavLib.MAVLink_heartbeat_message(self._mavLib.MAV_TYPE_ONBOARD_CONTROLLER, self._mavLib.MAV_AUTOPILOT_INVALID,0,0,0,1)
        self.queueOutputMsg(msg)

    def requestCapabilities(self):
        msg = self._mavLib.MAVLink_autopilot_version_request_message(0,0)
        self.queueOutputMsg(msg)

    def requestParams(self):
        msg = self._mavLib.MAVLink_param_request_list_message(0,0)
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

    def setTakeoff(self, alt):
        msg = self._mavLib.MAVLink_command_long_message(0,0,self._mavLib.MAV_CMD_NAV_TAKEOFF,0,0,0,0,0,0,0,alt)
        self.queueOutputMsg(msg)


    def setTakeoffLocal(self, alt):
        msg = self._mavLib.MAVLink_command_long_message(0,0,self._mavLib.MAV_CMD_NAV_TAKEOFF_LOCAL,0,0,0,0.1,0,0,0,-alt)
        self.queueOutputMsg(msg)
        

    def sendSetGlobalOrigin(self):
        msg = self._mavLib.MAVLink_set_gps_global_origin_message(0,self.home_lat, self.home_lon, self.home_alt)
        self.queueOutputMsg(msg)

    def sendSetHomePosition(self):
        x = 0
        y = 0
        z = 0
        q = [1,0,0,0]
        approach_x = 0
        approach_y = 0
        approach_z = 1
        '''
        msg = self._mavLib.MAVLink_set_home_position_message(0,
            self.home_lat, self.home_lon, self.home_alt,
            x,y,z,q,
            approach_x,
            approach_y,
            approach_z)
        '''
        msg = pymavlink.MAVLink_command_long_message(0, 0, pymavlink.MAV_CMD_GET_HOME_POSITION, 0, 0, 0, 0, 0, self.home_lat, self.home_lon, self.home_alt)
        self.queueOutputMsg(msg)

    def getHomePosition(self):
        msg = pymavlink.MAVLink_command_long_message(0, 0, pymavlink.MAV_CMD_GET_HOME_POSITION, 0, 0, 0, 0, 0, 0, 0, 0)
        self.queueOutputMsg(msg)

    def directAircraft(self, pos, heading=None):
        ignore = pymavlink.POSITION_TARGET_TYPEMASK_VX_IGNORE + \
                pymavlink.POSITION_TARGET_TYPEMASK_VY_IGNORE + \
                pymavlink.POSITION_TARGET_TYPEMASK_VZ_IGNORE + \
                pymavlink.POSITION_TARGET_TYPEMASK_AX_IGNORE + \
                pymavlink.POSITION_TARGET_TYPEMASK_AY_IGNORE + \
                pymavlink.POSITION_TARGET_TYPEMASK_AZ_IGNORE# + \
        
        if heading is None:
            ignore += pymavlink.POSITION_TARGET_TYPEMASK_YAW_IGNORE + \
                    pymavlink.POSITION_TARGET_TYPEMASK_YAW_RATE_IGNORE

            heading = 0
        
        yawRate = 0.5 # rad/s

        # for global frames SET_POSITION_TARGET_GLOBAL_INT
        msg = pymavlink.MAVLink_set_position_target_local_ned_message(0,0,0,
            pymavlink.MAV_FRAME_LOCAL_NED,
            ignore,
            pos[0],
            pos[1],
            pos[2],
            0,0,0, # Vx, Vy, Vz
            0,0,0, # Ax, Ay, Az
            heading, yawRate) # yaw, yaw rate
            
        self.queueOutputMsg(msg)

    def sendPosition(self, pos, rot):
        UNIX_time = int(time.time()*1e6)
        # UNIX_time = 0

        rot = rot.as_euler('xyz')[0] # roll, pitch, yaw
        msg = self._mavLib.MAVLink_vision_position_estimate_message(UNIX_time, pos[0], pos[1], pos[2], 
                                                                rot[0], rot[1], rot[2])
        self.queueOutputMsg(msg, priority=1) # Highest priority

    def sendPlayTune(self, tune, tune2=b''):
        # Tx set temp
        # > Up Octave
        # < Down Octave
        # # Sharp
        # ?x - Note length
        # ' ' - Pause crotchet
        # P - semibreve
        # L Bar length
        # MF - Final
        # MB - Loop
        # MS - Sticato
        # ML - Legato
        # O - set octave
        # N - ???
        msg = pymavlink.MAVLink_play_tune_message(0, 0, tune, tune2)
        self.queueOutputMsg(msg)

if __name__ == "__main__":
    # Connect to pixhawk - write port is determined from incoming messages
    commObj = mavSocket.mavSocket(  listenAddress = ('', 14551) )
    commObj.openPort()
    
    mavObj = pixhawkAbstract( conn = commObj )

    # Start pixhawk connection
    pixThread = Thread( target = mavObj.loop )
    pixThread.daemon = True
    pixThread.start()

    print('***RUNNING***')

    # Wait until we have a complete connection
    while not commObj.isOpen() or not mavObj.seenHeartbeat:
        time.sleep(1)
        
    print('***CONNECTED***')

    try:
        while True:
            tune = b'MFMST255L4< F#2 A  >C#2 <A2 F# D#D#D#2'
            mavObj.sendPlayTune(b'', tune)
            time.sleep(10)
        
    except KeyboardInterrupt:
        pass

    mavObj.stopLoop()
    commObj.closePort()
