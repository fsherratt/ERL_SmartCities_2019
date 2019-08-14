# !/bin/python3
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
import modules.map as mp
import modules.realsense.d435 as realsense_d435
import modules.realsense.t265 as realsense_t265
from typing import List

"""
Deals with message routing.
Setup should allow for items to be configured at runtime.

RECOMMENDED CHANGE:
Have these items attempt to bind to ports and supply a retry period.
This should allow items to come up fall over without breaking the program.
There are fairly minor data needs (bar the map) that have to be passed around, so this could
simply act as a "ferrying" data structure.
This basically means every class becomes its own python class to run,
will keep good de-coupling and should allow for easy testing.
Internal state can be stored for passing between items.
Loops can then be checked on state of buffer/if items need to be recieved or not
"""
class SmartFrame():
	"""
	Default init. Unused properties can be null
	"""
	def __init__( self, 
				pixhawk:px.pixhawk, 
				mapping = None, 
				d435 = None,
				t265 = None,
				routeCalc = None, 
				mkHub = None, 
				SLAM = None,
				PoiCamera = None,
				GCS = None ):
		# Classes injected
		self.pixhawk = pixhawk
		self.d435 = d435
		self.t265 = t265
		self.mapping = mapping
		self.routeCalc = routeCalc
		self.MkHub = mkHub
		self.SLAM = SLAM
		self.PoiCamera = PoiCamera
		self.GCS = GCS

		# Internal variables
		self._CurrentMap = self.mapping.grid # Replace with ap defualt
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
		potentialRoutes = self._GetPotentialRoute( currMap, position, self._poiLocation )
		route = self._CalcSafeRoute( potentialRoutes )
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
	Items for checking the map state.
	Calls to the d435 depth sensor, then the t265 position sensor.
	Then updates the global map with risk data relevant to the current view.
	Return: Numpy array representing the risk mapping.
	TODO : Define numpy in output
	"""
	def _CheckMap(self, position) -> List[ int ]:
		if self.mapping and self.t265 and self.d435:
			# Get frames of data - points and global 6dof
			frame = d435.getFrame()
			pos, r, _ = t265.getFrame()

			# Limit range of depth camera
			frame = d435.range_filter(frame, minRange = 0, maxRange = 30)

			# Convert to 3D coordinates
			frame = d435.deproject_frame( frame )

			# Convert to global coordinates
			points_global = self.mapping.frame_to_global_points(frame, pos, r)

			# Update map
			self.mapping.updateMap(points_global)
			self._CurrentMap = self.mapping.grid

		return self._CurrentMap

	"""
	Items for estiamting routes
	currentMap : current state of the risk map
	position : current position
	poi : current poi
	Return : Potential routes
	"""
	def _GetPotentialRoute( self, currentMap, position, poi ):
		print( "add route finder here..." )
		return [ 0, 0 ,0 ]

	"""
	Items for calculating the safe route
	"""
	def _CalcSafeRoute( self, routes ) -> List[ List[ int ] ]:
		# Not sure about containing this in the mapping function.
		# Would like to have it in its own fuction
		if self.mapping:
			queryPoints = self.mapping.queryMap( routes )
			# linked list to get the min risk and get those points?
			self._currentRoute = minRiskRoute

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

	# To update the mapping we need either one or both of the cameras.
	d435 = realsense_d435.rs_d435()
	t265 = realsense_t265.rs_t265()
	mapping = mp.mapper()
	# Startup frame
	sf = SmartFrame( pixhawk=pix, mapping=mapping, d435=d435, t265=t265 )

	sf.Run()
