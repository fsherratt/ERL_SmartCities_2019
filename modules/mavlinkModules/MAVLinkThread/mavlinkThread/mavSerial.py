# ------------------------------------------------------------------------------
# serial.py
# Abstraction of serial port communication for use with a mavThreadAbstract 
# object
#
# Author: Freddie Sherratt
# ------------------------------------------------------------------------------

import threading
import serial
import traceback
import sys

from .commAbstract import commAbstract

class mavSerial( commAbstract ):
    # --------------------------------------------------------------------------
    # Public function definitions
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # __init__
    # initialise serialClass object, does not start the serial port. Call
    # openPort once object is initialised to start serial communication.
    # param serialPortName serial port address e.g. COM8
    # param baudrate - serial baudrate
    # param timeout - serial read timeout
    # param writeTimeout - serial write timeout
    # return void
    # --------------------------------------------------------------------------
    def __init__( self, serialPortAddress, baudrate = 57600, readtimeout = 0.01,
                  writeTimeout = 3 ):

        self._readTimeout = readtimeout

        self._serialObj = serial.Serial()

        self._serialObj.port = serialPortAddress
        self._serialObj.baudrate = baudrate
        self._serialObj.timeout = readtimeout
        self._serialObj.write_timeout = writeTimeout

        self._writeLock = threading.Lock()
        self._readLock = threading.Lock()

    # --------------------------------------------------------------------------
    # openPort
    # Open the serial port specified during __init__
    # param null
    # return raises an exception if there is an error
    # --------------------------------------------------------------------------
    def openPort( self ):
        if self.isOpen():
            raise Exception('Port already open')

        self._serialObj.open()


    # --------------------------------------------------------------------------
    # closePort
    # Close the serial port if it is open
    # param null
    # return void
    # --------------------------------------------------------------------------
    def closePort( self ):
        try:
            if self._serialObj.isOpen:
                self._serialObj.close()

        except serial.SerialException:
            traceback.print_exc(file=sys.stdout)

    # --------------------------------------------------------------------------
    # read
    # Thread safe operation, it reads data in from the serial FIFO buffer
    # param numBytes - number of bytes to read
    # return raises an Exception if there is an error
    # --------------------------------------------------------------------------
    def read( self, numBytes = 1 ):
        self._readLock.acquire()

        try:
            b = self._serialObj.read( numBytes )
        
        except serial.SerialTimeoutException:
            traceback.print_exc(file=sys.stdout)

        finally:
            self._readLock.release()

        return b

    # --------------------------------------------------------------------------
    # write
    # Thread safe operation, it writes byte array data out the serial port
    # param b - byte array to write
    # return raises an Exception if there is an error
    # --------------------------------------------------------------------------
    def write( self, b ):
        self._writeLock.acquire()

        try:
            self._serialObj.write( b )

        except serial.SerialTimeoutException:
            traceback.print_exc(file=sys.stdout)

        finally:
            self._writeLock.release()

    # --------------------------------------------------------------------------
    # isOpen
    # Check is serial port has been closed
    # param null
    # return void
    # --------------------------------------------------------------------------
    def isOpen( self ):
        try:
            return self._serialObj.isOpen()

        except serial.SerialException:
            return False

    # --------------------------------------------------------------------------
    # dataAvailable
    # Check is serial input FIFO has data waiting to be read
    # param null
    # return True if data available to read, False otherwise
    # --------------------------------------------------------------------------
    def dataAvailable( self ):
        if self._serialObj.inWaiting() > 0:
            return True

        return False

    # --------------------------------------------------------------------------
    # flush
    # Clear the serial input buffer
    # param null
    # return void
    # --------------------------------------------------------------------------
    def flush( self ):
        pass

# ------------------------------------ EOF -------------------------------------
