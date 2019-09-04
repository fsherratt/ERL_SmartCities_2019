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
# comm = mavSerial.mavSerial( '/dev/ttyUSB0', 921600 )

pix = pixhawk.pixhawkAbstract( comm, pymavlink )
pix.srcSystem = 20
pix.srcComponent = 0

# Start pixhawk connection
pixThread = Thread( target = pix.loop )
pixThread.daemon = True
pixThread.start()

while not comm.isOpen() or not pix.seenHeartbeat:
    pix.sendHeartbeat()
    time.sleep(0.5)

print('**Pixhawk Connected**')

lat = 151269321
lon = 16624301
alt = 163000

t265Obj = t265.rs_t265( rotOffset=rotOffset )

lastHeartbeat = time.time()

startTime = time.time()
setHomeDelay = 10
homeSet = False

try:
    with t265Obj:
        print('**T265 Connected**')
        while True:
            if not homeSet and time.time() - startTime > setHomeDelay:
                pix.sendSetGlobalOrigin(lat,lon,alt)
                pix.sendSetHomePosition(lat,lon,alt)

                print('Home Position Set')
                homeSet = True

            if time.time() - lastHeartbeat > 0.5:
                pix.sendHeartbeat()

                lastHeartbeat = time.time()
            
            pos, r, _ = t265Obj.getFrame()
            rot = r.as_euler('xzy', degrees=False)

            pix.sendPosition(pos, rot)

            time.sleep(1/positionUpdateRate)

except KeyboardInterrupt:
    pass

finally:
    pix.stopLoop()
    comm.closePort()