# ------------------------------------------------------------------------------
# helloWorld.py
# System attempts to automatically restart serial connection after an exception
#
# Author: Freddie Sherratt
# ------------------------------------------------------------------------------

import threading
import time
import traceback
import sys

from mavlinkThread import mavSerial, mavThread
import pymavlink.dialects.v20.ardupilotmega as pymavlink

# Print out all incoming message
class mavClass( mavThread.mavThread ):
    def _processReadMsg( self, msgList ):
        for msg in msgList:
            print( msg )

    def loop( self ):
        while not self._intentionallyExit:
            try:
                super( mavClass, self).loop()
            except:
                traceback.print_exc(file=sys.stdout)
                self.restartConnection()

    def restartConnection(self):
        time.sleep(1)

        try:
            self._ser.closePort()
            self._ser.openPort()
            self.startLoop()
        except:
            traceback.print_exc(file=sys.stdout)        


if __name__ == "__main__":
    # Open serial port connection
    serialObj = mavSerial.mavSerial( '/dev/ttyu1' )
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
