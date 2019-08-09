# !/bin/python
""" This module defines the main inerconnecting framework
ntrol.

It should deal with initilizing moudules, routing messages.
"""

__all__ = []
__version__ = '0.1'
__author__ = 'Alex Powell, Freddie Sherrat'

import utilities.argparser as ap
import modules.pixhawk as px

"""
Deals with message routing.
Setup should allow for items to be configured at runtime
"""
class SmartFrame():
	"""
	Default init. Unused properties can be null
	"""
	def __init__( self, pixhawk, mapping ):
		self.pixhawk = pixhawk
		self.mapping = mapping

	"""
	Generic run for the smart frame.
	This is an endless loop that will check the state of each module attached
	and respond to events when requried
	"""
	def Run(self):
		self._RunPix()
		self._CheckMap()

	"""
	Items included when checking the pixhawk
	"""
	def _RunPix(self):
		if self.pixhawk:
			print( "I have a pixhawk" )
			print( self.pixhawk.baud )
		else:
			pass

	"""
	Items for checking the map state
	"""
	def _CheckMap(self):
		if self.mapping:
			# Do all map related functionality
			print( "Checking map" )
		else:
			pass


if __name__=='__main__':
	# setup arguments
	args = ap.GetParser().parse_args()
	# Get pixhawk
	pix = px.PX2( args.pix[0], args.pix[1] )
	print( pix.Get6DOF() )
	# Startup frame
	sf = SmartFrame( pix, None )
	sf.Run()
