import abc

# ------------------------------------------------------------------------------
# commAbstract
# Interface class for communication methods that are called by a object
# inheriting from the MAVAbstract object
# ------------------------------------------------------------------------------

class commAbstract:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def openPort( self ):
        pass

    @abc.abstractmethod
    def closePort( self ):
        pass

    @abc.abstractmethod
    def read( self ):
        pass

    @abc.abstractmethod
    def write( self, b ):
        pass

    @abc.abstractmethod
    def isOpen( self ):
        pass

    @abc.abstractmethod
    def dataAvailable( self ):
        pass

    @abc.abstractmethod
    def flush( self ):
        pass