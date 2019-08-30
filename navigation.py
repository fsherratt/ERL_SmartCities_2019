from modules.MAVLinkThread.mavlinkThread import mavSocket, mavSerial
from modules import pixhawk
from modules.realsense import t265

import pymavlink.dialects.v20.ardupilotmega as pymavlink
import time

from threading import Thread

PI_2 = 1.5708

rotOffset=[-90,-90,0] # Degrees
positionUpdateRate = 30 # Hz

comm = mavSocket.mavSocket( ('localhost', 14550) )
# comm = mavSerial.mavSerial( '/dev/ttyUSB1', 115200 )

pix = pixhawk.pixhawkAbstract( comm, pymavlink )

# Start pixhawk connection
pixThread = Thread( target = pix.loop )
pixThread.daemon = True
pixThread.start()

while not comm.isOpen() or not pix.seenHeartbeat:
    pix.sendHeartbeat()
    time.sleep(0.5)

print('**Pixhawk Connected**')

t265Obj = t265.rs_t265( rotOffset=rotOffset )

try:
    with t265Obj:
        print('**T265 Connected**')
        while True:
            pos, r, _ = t265Obj.getFrame()
            rot = r.as_euler('xzy', degrees=False)

            pix.sendPosition(pos, rot)

            print([pos, r.as_euler('xzy', degrees=True)])

            time.sleep(1/positionUpdateRate)

except KeyboardInterrupt:
    pass

finally:
    pix.stopLoop()
    comm.closePort()