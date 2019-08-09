"""
This class deals with abstracting away the pixhawk implementation
It requires a number of features from the abstract base class,
otherwise any implementation of autopilot can be used
"""

__all__ = []
__version__ = '0.1'
__author__ = 'Alex Powell, Freddie Sherrat'

from abc import ABC

"""
Abstract base class for anything pixhawk related
"""
class pixhawk(ABC):
	@classmethod	
	def Get6DOF( self ) -> int:
		pass

	@classmethod
	def SetGoto( self, position ) -> int:
		pass

"""
Pixhawk implementation for using the PX2
"""
class PX2( pixhawk ):
	def __init__(self, port, baud):
		self.port = port
		self.baud = baud

	def Get6DOF( self ) -> int:
		return 1

	def SetGoto( self, position ) -> bool:
		print( "Sending mavlink messae" )
		return True