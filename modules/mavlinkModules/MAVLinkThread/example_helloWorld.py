# ------------------------------------------------------------------------------
# helloWorld.py
# Mimimum working exampe of a threaded serial mavlink interface. Prints incoming 
# messages, send a heartbeat messages at 2Hz.
#
# Author: Freddie Sherratt
# ------------------------------------------------------------------------------

import threading
import time

from mavlinkThread import mavSerial, mavThread
import pymavlink.dialects.v10.ardupilotmega as pymavlink


# Print out all incoming message
class mavClass( mavThread.mavThread ):
    def _processReadMsg( self, msgList ):
        for msg in msgList:
            print( msg )


if __name__ == "__main__":
    # Open serial port connection
    serialObj = mavSerial.mavSerial( '/dev/ttyu1', 57600 )
    serialObj.openPort()

    # Create mavlink thread object
    mavObj = mavClass( serialObj, pymavlink )

    # Create mavlink thread
    mavThread = threading.Thread( target = mavObj.loop )
    mavThread.daemon = True
    mavThread.start()

    # Send heartbeat message at 2Hz
    try:
        while True:
            heartbeatMsg = pymavlink.MAVLink_heartbeat_message( 0, 0, 0, 0, 0, 0 )
            mavObj.queueOutputMsg( heartbeatMsg )

            time.sleep(0.5)

    # Close on keyboard interrupt
    except KeyboardInterrupt:
        pass

    mavObj.stopLoop()
    serialObj.closePort()

    print('Bye')

# ------------------------------------ EOF -------------------------------------
