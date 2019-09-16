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

    def __init__(self, hostname=''):
        self.hostname = hostname

        self.sockObj = None
        self.conn = None

        pass
    
    def _createSocket(self):
        self.sockObj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockObj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sockObj.settimeout(2)

    def startServer(self):
        self.addr = (self.hostname, self._PORT)
        
        self._createSocket()
        self.sockObj.bind(self.addr)
        self.sockObj.listen()

        while True:
            # Wait for incoming connection
            try:
                self.conn, addr = self.sockObj.accept()
                print('Connected to: {}'.format(addr))

            except (BlockingIOError, socket.timeout):
                print('*** Waiting for connection ***')
                time.sleep(1)
            
            else:
                return

    def close(self):
        if self.sockObj is not None:
            self.sockObj.close()
        
        if self.conn is not None:
            self.conn.close()

        print('*** Connection Closed ***')

    def startClient(self):
        self.addr = (self.hostname, self._PORT)

        while True:
            try:
                self._createSocket()
                self.sockObj.connect(self.addr)

            except (ConnectionRefusedError, socket.timeout):
                print('*** [61] Connection Refused ***')
                time.sleep(1)

            else:
                return

    def sendData(self, data):
        byteData = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        self.sendByteData(byteData)

    def sendByteData(self, byteData):
        try:
            writable = select.select([], [self.conn], [], self._TIMEOUT)[1]

            for conn in writable:
                msg =  b'$' + struct.pack('>I', len(byteData)) + b':' + byteData
                conn.sendall(msg)

        except ValueError as e:
            if self.conn.fileno() == -1:
                raise BrokenPipeError
            else:
                print(e)

        except BrokenPipeError:
            self.conn.close()

    def readMsg(self):
        try:
            readable = select.select([self.sockObj], [], [], self._TIMEOUT)[0]

            for conn in readable:
                # Syncronize stream
                msg = conn.recv(1)
                while msg != b'$':
                    msg = conn.recv(1)

                    if msg == b'':
                        return None

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

        except (ValueError):
            if self.sockObj.fileno() == -1:
                raise BrokenPipeError

        except (ConnectionResetError, socket.timeout):
            print( '*** Socket Closed ***' )
            self.close()

        return None


if __name__ == "__main__":
    import threading

    remoteTelem = telem()
    remoteTelem.startServer()

    # localTelem.sockObj.close()

    testImage = cv2.imread('/Users/freddiesherratt/Desktop/ERL_SmartCities_2019/modules/test.jpg', 0)

    totalTime = 0
    loops = 5
    for i in range(loops):
        print(i)
        startTime = time.time()
        remoteTelem.sendData(testImage)
        remoteTelem.close()
        time.sleep(1)

        totalTime += time.time() - startTime

    print(totalTime/loops)

    remoteTelem.close()