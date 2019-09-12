import LED
import threading
import time

ledObj = LED.LED()

ledThread = threading.Thread(target=ledObj.loop)
ledThread.daemon = True


with ledObj:
    ledThread.start()
    
    while True:
        ledObj.mode = 1
        time.sleep(5)
        ledObj.mode = 0
        time.sleep(3)
        ledObj.mode = 5
        time.sleep(2)
        ledObj.mode = 3
        time.sleep(2)
        ledObj.mode = 4
        time.sleep(2)