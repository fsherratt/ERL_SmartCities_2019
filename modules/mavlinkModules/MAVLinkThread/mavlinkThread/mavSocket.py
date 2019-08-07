# ------------------------------------------------------------------------------
# serial.py
# Abstraction of socket port communication for use with a mavThreadAbstract 
# object
#
# Author: Freddie Sherratt
# ------------------------------------------------------------------------------

import threading
import socket
import traceback
from .commAbstract import commAbstract

class mavSocket( commAbstract ):
    # --------------------------------------------------------------------------
    # __init__
    # initialise serialClass object, does not start the serial port. Call
    # openPort once object is initialised to start serial communication.
    # param broadcastPort - UDP socket broadcast port
    # param broadcastAddress - UDP socket broadcast address
    # param listenPort - UDP socket listen port
    # param listenAddress - UDP socket listen address
    # param readTimeout - UDP socket read timeout
    # param buffSize - listen UDP socket buffer size

    # return void
    # --------------------------------------------------------------------------
    def __init__( self, broadcastPort, listenPort,
                  broadcastAddress = '255.255.255.255', listenAddress = '',
                  readTimeout = 0.01, buffSize = 1024, ):
        
        self._writePort = broadcastPort
        self._readPort = listenPort

        self._sRead = None
        self._sWrite = None

        self.readTimeout = readTimeout
        self.buffSize = buffSize

        self._writeAddress = broadcastAddress
        self._readAddress = listenAddress

        self._writeLock = threading.Lock()
        self._readLock = threading.Lock()

        self._open = False

    # --------------------------------------------------------------------------
    # openPort
    # Open the socket connections specified during __init__
    # param null
    # return raises an exception if there is an error
    # --------------------------------------------------------------------------
    def openPort( self ):
        self._sRead = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self._sRead.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
        self._sRead.bind( ( self._readAddress, self._readPort ) )

        self._sRead.settimeout( self.readTimeout )

        self._sWrite = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self._sWrite.setsockopt( socket.SOL_SOCKET, socket.SO_BROADCAST, 1 )
        self._sWrite.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )

        self._sWrite.connect( ( self._writeAddress, self._writePort ) )

        self._open = True

    # --------------------------------------------------------------------------
    # closePort
    # Close the socket connection port if it is open
    # param null
    # return void
    # --------------------------------------------------------------------------
    def closePort( self ):
        if self._open:
            self._open = False

            self._sRead.close()
            self._sWrite.close()

    # --------------------------------------------------------------------------
    # read
    # Thread safe operation, it reads data in from the socket connection
    # param none
    # return tuple of (data, (recieved address)) for each message in buffer
    # --------------------------------------------------------------------------
    def read( self, b = 0 ):
        self._readLock.acquire()

        try:
            m = self._sRead.recv( self.buffSize )

        except socket.timeout:
            m =  None

        finally:
            self._readLock.release()

        return m

    # --------------------------------------------------------------------------
    # write
    # Thread safe operation, it writes byte string data out the socket
    # connection
    # param b - byte string to write
    # return raises an Exception if there is an error
    # --------------------------------------------------------------------------
    def write( self, b ):
        self._writeLock.acquire()
        try:
            self._sWrite.sendall( b )
            
        except Exception:
            traceback.print_exc(file=sys.stdout)

        finally:
            self._writeLock.release()

    # --------------------------------------------------------------------------
    # isOpen
    # Check is socket port has been intentionally closed
    # param null
    # return void
    # --------------------------------------------------------------------------
    def isOpen( self ):
        return self._open

    # --------------------------------------------------------------------------
    # dataAvailable
    # Check is socket data is available
    # param null
    # return True if data available to read, False otherwise
    # --------------------------------------------------------------------------
    def dataAvailable( self ):
        read,_,_ = select.select( [self._sRead], [], [], self.readTimeout )

        if len(read) > 0:
            return True

        return False

    # --------------------------------------------------------------------------
    # flush
    # Not possible to flush a socket connection so this is left blank
    # param null
    # return void
    # --------------------------------------------------------------------------
    def flush( self ):
        while self.dataAvailable():
            self.read()
            time.sleep(0.01)

# ------------------------------------ EOF -------------------------------------
