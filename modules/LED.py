import time
from enum import Enum

class mode(Enum):
    INITIALISE = 0 
    RUNNING = 1
    TAKEOFF = 2 
    LANDING = 3
    ERROR = 4
    MUCHERROR = 5 
    COLLISION_AVOID_ON = 6

class sitlLED:
    def setMode():
        pass

    def loop():
        pass

class LED:
    def __init__(self):
        import board
        import neopixel

        self.num_pixels = 8
        self.pin = board.D21

        self.pixels = neopixel.NeoPixel(board.D21, self.num_pixels, auto_write=False)

        self.mode = mode.INITIALISE
        self.newMode = True

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear()

    def setMode(self, mode):
        self.mode = mode

    def loop(self):
        while True:
            if self.mode == mode.INITIALISE:
                self.rainbowCycle()

            elif self.mode == mode.RUNNING:
                self.pulseGreen()

            elif self.mode == mode.TAKEOFF:
                self.takeOff()
                
            elif self.mode ==  mode.LANDING:
                self.landing()

            elif self.mode == mode.ERROR:
                self.flashRed()

            elif self.mode == mode.MUCHERROR:
                self.fastFlashRed()
            
            elif self.mode == mode.COLLISION_AVOID_ON:
                self.alternatingPurple()
                
            elif self.mode == 7:
                self.flashGreen()
                
    def flashAll(self, RGB, wait):
        self.pixels.fill((RGB))
        self.pixels.show()
        time.sleep(wait)
        self.clear()
        time.sleep(wait)

    def flashGreen(self):
        RGB = (0,255,0)
        wait = 0.2
        self.flashAll(RGB, wait);

    def flashRed(self):
        RGB = (255,0,0)
        wait = 0.2
        self.flashAll(RGB, wait);

    def fastFlashRed(self):
        RGB = (255,0,0)
        wait = 0.1
        self.flashAll(RGB, wait);
    
    def alternatingPurple(self):
        self.clear()
        RGB = (128,0,128)
        for i in range(0, 8, 2):
            self.pixels[i] = RGB
            self.pixels.show()
        time.sleep(0.2)    
        self.clear()
        for i in range(1, 8, 2):
            self.pixels[i] = RGB
            self.pixels.show()
        time.sleep(0.2)
        
    def pulseGreen(self):
        i=0
        while i <= 254:
            self.pixels.fill((0,i,0))
            self.pixels.show()
            time.sleep(0.001)
            i+=1
        while i >= 0:
            self.pixels.fill((0,i,0))
            self.pixels.show()
            time.sleep(0.001)
            i-=1
    
    def singlePixelFlash(self, RGB, wait, i):
        self.clear()
        self.pixels[i] = RGB
        self.pixels.show()
        time.sleep(wait)
    
    def runDown(self, RGB, wait):
        for i in range(8):
            self.singlePixelFlash(RGB, wait, i)

    def runUp(self, RGB, wait):
        for i in range(7, -1, -1):
            self.singlePixelFlash(RGB, wait, i)
            
    def landing(self):
        RGB = (255,50,0) #orange
        wait = 0.1
        self.runDown(RGB, wait)        
            
    def takeOff(self):
        RGB = (0,0,255) #orange
        wait = 0.1
        self.runUp(RGB, wait)

    def rainbowCycle(self):
        wait = 0.005
        for j in range(255):
            for i in range(self.num_pixels):
                pixel_index = (i * 256 // self.num_pixels) + j
                self.pixels[i] = self.wheel(pixel_index & 255)
            self.pixels.show()
            time.sleep(wait)

    def wheel(self, pos):
        # Input a value 0 to 255 to get a color value.
        # The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos*3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos*3)
            g = 0
            b = int(pos*3)
        else:
            pos -= 170
            r = 0
            g = int(pos*3)
            b = int(255 - pos*3)
        return (r, g, b)

    def clear(self):
        self.pixels.fill((0,0,0))
        self.pixels.show()

if __name__ == '__main__':
    import threading

    ledObj = LED()

    ledThread = threading.Thread(target=ledObj.loop)
    ledThread.daemon = True


    with ledObj:
        ledThread.start()

        while True:
            ledObj.mode = mode.INITIALISE
            time.sleep(3)
            ledObj.mode = mode.RUNNING
            time.sleep(3)
            ledObj.mode = mode.TAKEOFF
            time.sleep(3)
            ledObj.mode = mode.COLLISION_AVOID_ON
            time.sleep(3)
            ledObj.mode = mode.LANDING
            time.sleep(3)
            ledObj.mode = mode.ERROR
            time.sleep(3) 
            ledObj.mode = mode.MUCHERROR 
            time.sleep(3)