# ------------------------------------------------------------------------------
# helloWorld.py
# Queue incoming messages for processing in the main threadx
#
# Author: Freddie Sherratt
# ------------------------------------------------------------------------------

import threading
import time

import sys
if sys.version_info.major == 3:
    import queue
else:
    import Queue as queue
    
from mavlinkThread import mavSerial, mavThread
import pymavlink.dialects.v10.ardupilotmega as pymavlink


# Add incoming messages to a read queue
class mavClass( mavThread.mavThread ):
    def __init__( self, conn, mavLib, readQueue ):
        self.readQueue = readQueue

        super( mavClass, self).__init__( conn, mavLib )

    def _processReadMsg( self, msgList ):
        for msg in msgList:
            self.readQueue.put( msg )


if __name__ == "__main__":
    readQueue = queue.Queue()

    # Open serial port connection
    serialObj = mavSerial.mavSerial( '/dev/ttyu1', 57600 )
    serialObj.openPort()

    # Create mavlink thread object
    mavObj = mavClass( serialObj, pymavlink, readQueue )

    # Create mavlink thread
    mavThread = threading.Thread( target = mavObj.loop )
    mavThread.daemon = True
    mavThread.start()

    try:
        lastHeartbeat = 0

        while True:
            # Send heartbeat message at 2Hz
            if ( time.time() - lastHeartbeat > 0.5 ):
                heartbeatMsg = pymavlink.MAVLink_heartbeat_message( 0, 0, 0, 0, 0, 0 )
                mavObj.queueOutputMsg( heartbeatMsg )

                lastHeartbeat = time.time()

            # Process read queue
            try:
                msg = readQueue.get_nowait()
                print( msg )

            except queue.Empty:
                pass

            time.sleep(0.1)

    # Close on keyboard interrupt
    except KeyboardInterrupt:
        pass

    mavObj.stopLoop()
    serialObj.closePort()

    print('Bye')

# ------------------------------------ EOF -------------------------------------
