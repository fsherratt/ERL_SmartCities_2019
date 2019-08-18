from modules.MAVLinkThread.mavlinkThread import mavSocket, mavSerial
from modules import pixhawk
from modules.realsense import t265

import pymavlink.dialects.v20.ardupilotmega as pymavlink
import time

from threading import Thread

PI_2 = 1.5708

rotOffset=[-90,-90,0]
positionUpdateRate = 30 # Hz

comm = mavSocket.mavSocket( 0, 0 )

pixInterface = pixhawk.pixhawkAbstract( comm, pymavlink )

# Start pixhawk connection
pixThread = Thread( target = pixInterface.loop )
pixThread.daemon = True
pixThread.start()

t265Obj = t265.rs_t265( rotOffset=rotOffset )

try:
    with t265Obj:
        while True:
            pos, r, conf = t265Obj.getFrame()
            rot = r.as_euler('xzy', degrees=False)

            pixInterface.sendPosition(pos, rot, conf, 0 )

            print([pos, r.as_euler('xzy', degrees=True), conf])

            time.sleep(1/positionUpdateRate)
except KeyboardInterrupt:
    pass

finally:
    pixInterface.stopLoop()
    comm.closePort()