import multiprocessing as mp 
import threading
import time
import numpy as np
import threading

class TestMulti:
	def __init__( self ):
		self.lock = threading.Lock()
		# Define array and map size of this to shared memory
		self.array = np.zeros( (5, 5) )

	# forever loop. Keep updating the shared memory whenever you can.
	def Loop( self ):
		while( True ):
			self.lock.acquire()
			try:
				print( "locking to update array" )
				self.array = np.random.rand( 5, 5 )
				print( self.array )
			finally:
				self.lock.release() 
			time.sleep( 1 )

	# Can I call this when this is running in a seperate thread?
	def GetArray( self ):
		self.lock.acquire()
		try:
			print( "Getting array" )
			return self.array
		finally:
			self.lock.release()

if __name__ == "__main__":
	shared = TestMulti()
	p1 = mp.Process( target=shared.Loop, args=() )
	p1.start()
	time.sleep( 5 )
	print( shared.GetArray() )
	time.sleep( 2 )
	# Kill process at end
	p1.terminate()