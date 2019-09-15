import time
import socket
import select
import struct
import pickle

import cv2

class telem():
    _PORT = 50006
    _MAX_READ_LEN = 60000
    _TIMEOUT = 1

    def __init__(self, server=True):
        self.addr = ('127.0.01', self._PORT)

        self.sockObj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockObj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sockObj.settimeout(2)

    def startServer(self):
        self.sockObj.bind(self.addr)
        self.sockObj.listen()

        while True:
            # Wait for incoming connection
            try:
                self.conn, addr = self.sockObj.accept()
                print('Connected to: {}'.format(addr))
                return

            except BlockingIOError:
                time.sleep(1)

    def startClient(self):
        self.sockObj.connect(self.addr)

    def sendData(self, data):
        byteData = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        self.sendByteData(byteData)

    def sendByteData(self, byteData):
        try:
            writable = select.select([], [self.conn], [], self._TIMEOUT)[1]

            msg =  b'$' + struct.pack('>I', len(byteData)) + b':' + byteData

            for conn in writable:
                conn.sendall(msg)

        except ValueError:
            return

        except BrokenPipeError:
            print('Connection Closed')
            self.conn.close()

    def readMsg(self):
        try:
            readable = select.select([self.sockObj], [], [], self._TIMEOUT)[0]
            
            for conn in readable:
                # Syncronize stream
                msg = conn.recv(1)
                while msg != b'$':
                    msg = conn.recv(1)

                # Get message length
                msg_len = struct.unpack('>I', conn.recv(4))[0]

                # Wait for all data to be returned
                if conn.recv(1) == b':':
                    msg = b''
                    while len(msg) < msg_len:

                        bytesIn = msg_len - len(msg)
                        if bytesIn > self._MAX_READ_LEN:
                            bytesIn = self._MAX_READ_LEN

                        try:
                            msg += conn.recv(bytesIn)
                        except BlockingIOError:
                            time.sleep(0.1)

                    return msg

        except (socket.timeout, ValueError):
            pass

        return None


if __name__ == "__main__":
    import threading

    remoteTelem = telem()
    localTelem = telem()

    remoteThread = threading.Thread(target=remoteTelem.startServer)
    remoteThread.start()

    localTelem.startClient()

    remoteThread.join()

    # localTelem.sockObj.close()

    testImage = cv2.imread('/Users/freddiesherratt/Desktop/ERL_SmartCities_2019/modules/test.jpg', 0)

    totalTime = 0
    loops = 100
    for _ in range(loops):
        startTime = time.time()

        remoteThread = threading.Thread(target=remoteTelem.sendData, args=[testImage])
        remoteThread.start()

        img = localTelem.readMsg()
        
        remoteThread.join()

        totalTime += time.time() - startTime

    print(totalTime/loops)

    img = pickle.loads(img)

    cv2.imshow('Sent', img)
    cv2.waitKey(100)

    localTelem.sockObj.close()