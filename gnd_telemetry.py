from modules import telemetry
import time
import pickle
import cv2

if __name__ == "__main__":
    localTelem  = telemetry.tcpInterface( hostname='ERL-1.local')
    localTelem.startClient()

    while True:
        msg = localTelem.readMsg()
        
        if msg is None:
            time.sleep(0.5)
            continue
        
        if msg[0] == telemetry.DataType.TELEM_RGB_IMAGE:
            cv2.imshow('RGB', msg[1])
            cv2.waitKey(1)
        
        elif msg[0] == telemetry.DataType.TELEM_DEPTH_FRAME:
            cv2.imshow('Depth', msg[1])

        elif msg[0] == telemetry.DataType.TELEM_POSITION:
            print(msg[1])

        elif 
        time.sleep(0.5)

    localTelem.close()