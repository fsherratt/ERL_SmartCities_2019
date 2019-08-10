#!/bin/python3
"""
This class deals with abstracting away the pixhawk implementation
It requires a number of features from the abstract base class,
otherwise any implementation of autopilot can be used
"""

__all__ = [ 'pixhawk', 'PX2']
__version__ = '0.1'
__author__ = 'Alex Powell, Freddie Sherrat'

from abc import ABC, abstractmethod, ABCMeta

"""
Abstract base class for anything pixhawk related
"""
class pixhawk(ABC):
	@abstractmethod	
	def Get6DOF( self ) -> int:
		raise NotImplementedError('Get6DOF is not implemented')

	@abstractmethod
	def SetGoto( self, position ) -> bool:
		raise NotImplementedError('SetGoTo is not implemented')

	@abstractmethod
	def SetPosition( self, position ) -> bool:
		raise NotImplementedError('SetPosition is not implemented')

"""
Pixhawk implementation for using the PX2
"""
class PX2( pixhawk ):
	"""
	Simple init for pixhawk.
	Will likely need to use the mavlink thread module
	"""
	def __init__(self, port, baud):
		self.port = port
		self.baud = baud

	def Get6DOF( self ) -> int:
		return 1

	def SetGoto( self, position ) -> bool:
		print( "Sending mavlink messae" )
		return True

	def SetPosition( self, position ) -> bool:
		print( "Updaating position..." )
		return True

	def _SendMavlinK( self, msg ) -> bool:
		print( "Sending message..." )
		return True

	def _GetMavLinkMessage( self ) -> str:
		return "How should this wait??"