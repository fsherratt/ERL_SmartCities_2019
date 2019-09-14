from modules.MAVLinkThread.mavlinkThread.mavSocket import mavSocket
import pickle

import numpy as np
import time
import threading

import base64
import cv2

class telem():
    _MAX_DATA_LEN = 60000

    def __init__(self, port, remote=True):
        if remote :
            self.sockObj = mavSocket( broadcastAddress=('255.255.255.255', port))
        else:
            self.sockObj = mavSocket( listenAddress=('', port))
        
        self.sockObj.openPort()

        self.seq = 0
        self.lastId = -1
        self.lastSeq = 0
        self.objBuffer = b''

    def close(self):
        self.sockObj.closePort()

    def sendObject(self, dataObj, objName):
        data_string = pickle.dumps(dataObj, protocol=pickle.HIGHEST_PROTOCOL)

        data_len = len(data_string)

        data_to_send = data_len
        seq = 0
        
        # Split data into transmittable chunks
        while data_to_send > 0:
            if data_to_send > self._MAX_DATA_LEN:
                data_chunk = data_string[seq*self._MAX_DATA_LEN:(seq+1)*self._MAX_DATA_LEN]
                data_to_send -= self._MAX_DATA_LEN
            else:
                data_chunk = data_string[seq*self._MAX_DATA_LEN:]
                data_to_send = 0

            chunk_string = pickle.dumps((objName, data_len, seq, data_chunk), protocol=pickle.HIGHEST_PROTOCOL)
            self.sockObj.write(chunk_string)

            seq += 1

    def loop(self):
        while True:
            data_string = self.sockObj.read()

            if data_string == b'':
                time.sleep(0.5)
                continue

            try:
                dataObj = pickle.loads(data_string)
            except pickle.UnpicklingError:
                pass
            
            print('ID: {} Name: {}\t Seq: {}\t Len: {}\n'.format(dataObj[3], dataObj[0], dataObj[2], len(dataObj[4])))
            
            if self.lastId != dataObj[3] and dataObj[2] == 0:
                self.objBuffer = dataObj[4]
                self.lastId = dataObj[3]
                self.lastSeq = dataObj[2]

            elif self.lastSeq == dataObj[2] - 1:
                self.objBuffer = self.objBuffer + dataObj[4]
                self.lastSeq = dataObj[2]


            if len(self.objBuffer) == dataObj[1]:
                img = pickle.loads(self.objBuffer)
                nparr = np.fromstring(img, np.uint8)
                img = cv2.imdecode(img, cv2.IMREAD_COLOR)
                cv2.imshow(dataObj[0], img/np.max(img))
                cv2.waitKey(1)
                
if __name__ == "__main__":
    localTelem  = telem( 50007, remote=False)

    try:
        localTelem.loop()
    except KeyboardInterrupt:
        pass

    localTelem.close()