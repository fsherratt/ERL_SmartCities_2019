from modules.MAVLinkThread.mavlinkThread import mavSocket, mavSerial
from modules import pixhawk
from modules.realsense import t265

import pymavlink.dialects.v20.ardupilotmega as pymavlink
import time

comm = mavSocket.mavSocket( 0, 0 )

pixInterface = pixhawk.pixhawkAbstract( comm, pymavlink )
t265Obj = t265.rs_t265( rotOffset=[90,90,0] )

positionUpdateRate = 30 # Hz

with t265Obj:
    while True:
        pos, r, conf = t265Obj.getFrame()
        rot = r.as_euler(degrees=False)

        pixInterface.sendPosition([pos, rot], conf, 0 )

        time.sleep(1/positionUpdateRate)