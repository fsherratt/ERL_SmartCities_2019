from modules import telemetry
import time
import pickle
import cv2

if __name__ == "__main__":
    localTelem  = telemetry.telem( hostname='127.0.0.1')
    localTelem.startClient()

    while True:
        img = localTelem.readMsg()
        
        if img is None:
            print('*** No Data ***')
            time.sleep(0.5)
            continue

        img = pickle.loads(img)

        cv2.imshow('Sent', img)
        cv2.waitKey(500)
        time.sleep(0.5)

        # localTelem.close()

    localTelem.close()