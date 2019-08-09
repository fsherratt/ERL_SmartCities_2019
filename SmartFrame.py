# !/bin/python
""" This module defines the main interconnecting framework
ntrol.

It should deal with initilizing moudules, routing messages.
It will simply run as a loop to check the state and send relevant updates
following a simple flow. Complexity can be added later if requried.
"""

__all__ = [ 'SmartFrame' ]
__version__ = '0.1'
__author__ = 'Alex Powell, Freddie Sherrat'

import utilities.argparser as ap
import modules.pixhawk as px
from typing import List

"""
Deals with message routing.
Setup should allow for items to be configured at runtime
"""
class SmartFrame():
	"""
	Default init. Unused properties can be null
	"""
	def __init__( self, 
				pixhawk:px.pixhawk, 
				mapping = None, 
				routeCalc = None, 
				mkHub = None, 
				SLAM = None,
				PoiCamera = None,
				GCS = None ):
		# Classes injected
		self.pixhawk = pixhawk
		self.mapping = mapping
		self.routeCalc = routeCalc
		self.MkHub = mkHub
		self.SLAM = SLAM
		self.PoiCamera = PoiCamera
		self.GCS = GCS

		# Internal variables
		self._CurrentMap = [ 0, 0 ] # Replace with ap defualt
		# Not sure this is needed, can deal with updating to same pos in pixhawk?
		self._currentRoute = [ [ 0, 0, 0 ] ] 
		self._poiLocation = [ [0, 0, 0] ]
		self._currentFrame = "Hello World"
		self._position = [ [0, 0, 0 ] ]

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
	If any modules get bound using an add method, it will begin to incorperate them.
	Deal with return and updating interal values to pass them around nicer. Not sure this is
	the best way to do but allows for a clean seperation currently
	"""
	def Run(self) -> None:
		position = self._CheckPosition()
		currMap = self._CheckMap( position )
		route = self._CalcSafeRoute( currMap )
		self._SetGoto( route[ 0 ] )
		self._CheckMKSmart()
		self._UpdateSmartHub()
		if( self._CheckPoiCamera() ):
			self._UpdatePoiLocation( self._position )
		currentFrame = self._GetCameraFrame()
		self._CheckGCS()
		self._UpdateGCS( position, currentFrame, route, currentFrame )

	"""
	Items included when updating the position
	Will do data fusion between all avaliable objects
	"""
	def _CheckPosition(self) -> List[ List[ int ] ]:
		if self.pixhawk:
			# Update 6DOF. Probably should be more like Check current position
			print( "I have a pixhawk" )
		if self.SLAM:
			print( "Updating from SLAM sensor" )

		self._position = [ [1337, 1, 1 ] ] 
		return self._position

	"""
	Items for checking the map state
	"""
	def _CheckMap(self, position) -> List[ int ]:
		if self.mapping:
			# Do all map related functionality
			# Basically update and pull
			print( "Checking map" )
			self._CurrentMap = [ 1, 1 ]

		return self._CurrentMap

	"""
	Items for calculating the safe route
	"""
	def _CalcSafeRoute( self, map ) -> List[ List[ int ] ]:
		if self.routeCalc:
			print( "Calculating route" )
			# Interpolate all routes, calculate the best safe route
			# Definate candidate for threading
			self._currentRoute = [ [ 0, 1 , 1] ]

		return self._currentRoute # return defualt

	"""
	Items for setting the new position on autopilot
	"""
	def _SetGoto( self, position ) -> None:
		if self.pixhawk:
			# If setting the goto works, log correct, else show error
			if self.pixhawk.SetGoto( position ):
				print( "Updated position to: " + str( position ) )
			else:
				print( "Failed to update position..." )

	"""
	Check details recieved from smart hub
	"""
	def _CheckMKSmart( self ) -> None:
		if self.MkHub:
			print( "Checking items from MK HUB..." )
			# Check for any data in the buffer
			# Check what it is and update
			self._poiLocation = [ [ 1, 1 ,2 ] ]

	"""
	Items to update the smart hub.
	Should send current position and images?
	"""
	def _UpdateSmartHub( self ) -> None:
		if self.MkHub:
			print( "Passing items to smart hub..." )
			# Send position
			# Send image from camera
		else:
			pass

	"""
	Items for checking the POI camera has located subject.
	Returns true if they are found
	"""
	def _CheckPoiCamera( self ) -> bool:
		if self.PoiCamera:
			print( "Checking if POI is present in frame.." )
			if( self.PoiCamera.PoiLocated() ):
				return True
		return False

	"""
	Update the poi location with data recieved from Camera
	"""
	def _UpdatePoiLocation( self, position ) -> List[ List[ int ] ]:
		# If we have a camera, return the new location, else return previous
		if self.PoiCamera:
			self._poiLocation = [ [ 1, 1, 1 ] ]
		return self._poiLocation

	"""
	Gets a camera frame as a byte list for transmission
	"""
	def _GetCameraFrame( self ) -> str:
		if self.PoiCamera:
			print( "Sending frame back" )
			self._currentFrame = self.PoiCamera.GetFrame()
			return 'This is a byte frame!'

		return self._currentFrame

	"""
	Set items sent by the GCS (This still nees to be defiend!)
	"""
	def _CheckGCS( self ):
		if self.GCS:
			print( "doing GCS check stuff" )

	"""
	Update the GCS with any releavant data
	"""
	def _UpdateGCS( self, position, currentFrame, route, poiLocation ):
		if self.GCS:
			print( "Sending items to GCS" )

"""
Simple main loop for iniial developing
"""
if __name__=='__main__':
	# setup arguments
	args = ap.GetParser().parse_args()

	# Get pixhawk
	pix = px.PX2( args.pix[0], args.pix[1] )

	# Startup frame
	sf = SmartFrame( pixhawk=pix )

	sf.Run()
