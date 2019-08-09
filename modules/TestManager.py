import multiprocessing as mp 
import threading
import time
import numpy as np
import threading
import random

class TestMemory:
	def __init__( self, sharedArray, arrayCol, arrayRow ):
		# Define array and map size of this to shared memory
		self._arrayCol = arrayCol
		self._arrayRow = arrayRow
		# Do this with array
		self.memory = sharedArray
		#self.array = np.zeros( (arrayCol, arrayRow) )
		self.array = sharedArray
		self.array = self.array.reshape( arrayRow, arrayCol )

	# forever loop. Keep updating the shared memory whenever you can.
	def Loop( self ):
		while( True ):
			print( "updating arr" )
			self.array[ random.randint( 0, self._arrayRow - 1 ),
						random.randint( 0, self._arrayCol - 1 ) ] = random.random();
			time.sleep( 1 )

	# Can I call this when this is running in a seperate thread?
	def GetArray( self ):
		with self.memory.get_lock():
			return self.memory 

if __name__ == "__main__":
	mp.Manager.BaseManager().register( 'Numpy', np.array)

	with mp.Manager() as manager:
		shared_arr = manager.Numpy( )
		shared = TestMemory( shared_arr, 5, 5 )
		p1 = mp.Process( target=shared.Loop, args=() )
		p1.start()
		time.sleep( 5 )
		print( shared.GetArray() )
		print( shared_arr[ : ] )
		time.sleep( 2 )
		# Kill process at end
		p1.terminate()