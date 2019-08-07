# ------------------------------------------------------------------------------
# serialMAVLink
# Abstraction layer for MAVLink communications over a serial connections
# ------------------------------------------------------------------------------

from MAVLinkThread.mavlinkThread import mavSerial, mavThread

class pixhawkTelemetry( mavThread.mavThread ):
    # --------------------------------------------------------------------------
    # __init__
    # Creates and opens a serial communication channel then calls the super
    # initializer
    # shortHand - Name to store port under in the portDict
    # param readQueue - queue object to write read messages to
    # param mavSystemID - MAVLink system ID default 78
    # param mavComponentID - MAVLink component ID
    # param serialPortAddress - serial port address e.g. COM8
    # param baudrate - serial baudrate
    # param noRWSleepTime - sleep time when nothing to read or write
    # param loopPauseSleepTime - sleep time when R/W loop is paused
    # return void
    # --------------------------------------------------------------------------
    def __init__( self, shortHand, mavSystemID, mavComponentID,
                  serialPortAddress, baudrate = 57600, noRWSleepTime = 0.1,
                  loopPauseSleepTime = 0.5 ):
        self._roll = 0
        self._pitch = 0
        self._yaw = 0

        self._lat = 0
        self._lon = 0
        self._alt = 0

        self._datetime = dt.fromtimestamp(0)
        self._satcount = 0
        self._ser = serialConnect( serialPortAddress = serialPortAddress,
                                   baudrate = baudrate )
        self._ser.openPort()

        super( pixhawkTelemetry, self ).__init__(
                shortHand, mavSystemID, mavComponentID,
                noRWSleepTime,loopPauseSleepTime )

    # --------------------------------------------------------------------------
    # _processReadMsg
    # Overload of proccess read msg to extract telemetry information of interest
    # param null
    # return void
    # --------------------------------------------------------------------------
    def _processReadMsg( self, msgList ):
        if msgList is None:
            return False

        for msg in msgList:
            if isinstance( msg, pymavlink.MAVLink_message ):
                if msg.get_msgId() == pymavlink.MAVLINK_MSG_ID_ATTITUDE:
                    self._roll = msg.roll
                    self._pitch = msg.pitch
                    self._yaw = msg.yaw
                if msg.get_msgId() == pymavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT:
                    self._lat = msg.lat
                    self._lon = msg.lon
                    self._alt = msg.relative_alt
                if msg.get_msgId() == pymavlink.MAVLINK_MSG_ID_GPS_RAW_INT:
                    self._satcount = msg.satellites_visible
                if msg.get_msgId() == pymavlink.MAVLINK_MSG_ID_SYSTEM_TIME:
                    self._datetime = dt.fromtimestamp((int)(msg.time_unix_usec/1000000))

    # --------------------------------------------------------------------------
    # get6DOF (getter)
    # Retrieve aricraft 6 degree of freedom data
    # param null
    # returns 6 degree of freedom object
    # --------------------------------------------------------------------------
    def get6DOF(self):
        return aircraft6DOF(self._lat, self._lon, self._alt, self._roll, self._pitch, self._yaw, self._datetime, self._satcount)

    def sendTxtMsg( self, text ):
        text_byte = bytearray(text, encoding='utf8')
        msg = pymavlink.MAVLink_statustext_message( pymavlink.MAV_SEVERITY_ERROR, text_byte )
        self.queueOutputMsg(msg)