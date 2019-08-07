class pixhawk():
	def __init__(self, pixhawkComms):
		self.comms = pixhawkComms

	def loop( self ):
		# Threading and queing items goes in here, allows for interaction with an item pixhawk based
		pass
		
	def Get6DOF( self ):
		return self.comms.get6DOF