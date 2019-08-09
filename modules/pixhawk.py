from abc import ABC
import typing # Why is this not working?
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