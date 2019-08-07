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

	"""
	def __init__( self, pixhawk ):
		self.pixhawk = pixhawk

if __name__=='__main__':
	# setup arguments
	args = ap.GetParser().parse_args()
	# Get pixhawk
	pix = px.pixhawk( args.pix[0], args.pix[1] )
	
	# Startup frame
	sf = SmartFrame( pix )
