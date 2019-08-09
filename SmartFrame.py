# !/bin/python
""" This module defines the main interconnecting framework
ntrol.

It should deal with initilizing moudules, routing messages.
It will simply run as a loop to check the state and send relevant updates
following a simple flow. Complexity can be added later if requried.
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
	def __init__( self, pixhawk, mapping, routeCalc ):
		self.pixhawk = pixhawk
		self.mapping = mapping
		self.routeCalc = routeCalc
		self._CurrentMap = [ 0, 0 ] # Replace with ap defualt
		# Not sure this is needed, can deal with updating to same pos in pixhawk?
		self._currentRoute = [ [ 0, 0 ] ] 

	"""
	Generic run for the smart frame.
	This is an endless loop that will check the state of each module attached
	and respond to events when requried.

	Will effectivly follow this control flow:
	Update position -> check the map state ->
	Calculate the safe route -> send new goto
	-> check any mk hub -> send to mk hub
	-> Check POI camera -> Update POI location -> 
	-> Rip video feed -> Check GCS
	-> send to GCS

	If any modules are no-existant, the code will continue and pass.
	If any modules get bound using an add method, it will begin to incorperate them
	"""
	def Run(self):
		position = self._RunPix()
		map = self._CheckMap( position)
		route = self._CalcSafeRoute( map )
		self._SetGoto( [ 0, 0 ,0 ] )
		self._CheckMKSmart()
		self._UpdateSmartHub()


	"""
	Items included when updating the position
	Will do data fusion between all avaliable objects
	"""
	def _CheckPosition(self) -> int:
		if self.pixhawk:
			# Update 6DOF. Probably should be more like Check current position
			print( "I have a pixhawk" )
		if self.SLAM:
			print( "Updating from SLAM sensor" )
		else:
			pass
		self.position = 1337 
		return 5

	"""
	Items for checking the map state
	"""
	def _CheckMap(self, position):
		if self.mapping:
			# Do all map related functionality
			# Basically update and pull
			print( "Checking map" )
			self._CurrentMap = [ 1, 1 ]
		else:
			pass

	"""
	Items for calculating the safe route
	"""
	def _CalcSafeRoute( self, map ):
		if self.routeCalc:
			print( "Calculating route" )
			# Interpolate all routes, calculate the best safe route
			# Definate candidate for threading
			return [ 0, 1 , 1]
		else:
			pass

	"""
	Items for setting the new position on autopilot
	"""
	def _SetGoto( self, position ):
		if self.pixhawk:
			# If setting the goto works, log correct, else show error
			if self.pixhawk.SetGoto( position ):
				print( "Updated position to: " + str( position ) )
			else:
				print( "Failed to update position..." )
		else:
			pass

	"""
	Check details recieved from smart hub
	"""
	def _CheckMKSmart( self ):
		if self.MkHub:
			print( "Checking items from MK HUB..." )
			# Check for any data in the buffer
			# Check what it is and update
			self.patient = [ 1, 1 ,2 ]
		else:
			pass

	"""
	Items to update the smart hub.
	Should send current position and images?
	"""
	def _UpdateSmartHub( self ):
		if self.MkHub:
			print( "Passing items to smart hub..." )
			# Send position
			# Send image from camera
		else:
			pass

"""
Simple main loop for iniial developing
"""
if __name__=='__main__':
	# setup arguments
	args = ap.GetParser().parse_args()
	# Get pixhawk
	pix = px.PX2( args.pix[0], args.pix[1] )
	print( pix.Get6DOF() )
	# Startup frame
	sf = SmartFrame( pix, None, None )
	sf.Run()
