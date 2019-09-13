import board
import neopixel
import time

class LED:
    def __init__(self):
        self.num_pixels = 8
        self.pin = board.D21

        self.pixels = neopixel.NeoPixel(board.D21, self.num_pixels, auto_write=False)

        self.mode = 1
        self.newMode = True

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear()

    def loop(self):
        while True:

            if self.mode == 0:
                self.flashGreen()

            elif self.mode == 1:
                self.rainbow_cycle( 0.005 )
                #self.mode = 0
                #self.newMode = True
            elif self.mode == 2:
                self.pulseGreen()

            elif self.mode == 3:
                self.runDownOrange()

            elif self.mode ==  4:
                self.runUpBlue()

            elif self.mode == 5:
                self.flashRed()

            elif self.mode == 6:
                self.fflashRed()

    def flash(self, RGB, sleepTime):
        self.pixels.fill((RGB))
        self.pixels.show()
        time.sleep(sleepTime)
        self.clear()
        time.sleep(sleepTime)

    def flashGreen(self):
        RGB = (0,255,0)
        sleepTime = 0.2
        self.flash();

    def flashRed(self):
        RGB = (255,0,0)
        sleepTime = 0.2
        self.flash();

    def fflashRed(self):
        RGB = (255,0,0)
        sleepTime = 0.1
        self.flash();

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

    def runDownOrange(self):
        for i in range(8):
            self.clear()
            self.pixels[i] = (255,165,0)
            self.pixels.show()
            time.sleep(0.1)

    def runUpBlue(self):
        for i in range(7, -1, -1):
            self.clear()
            self.pixels[i] = (0,0,255)
            self.pixels.show()
            time.sleep(0.1)


    def rainbow_cycle(self, wait):
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
            ledObj.mode = 1
            time.sleep(5)
            ledObj.mode = 0
            time.sleep(3)
            ledObj.mode = 5
            time.sleep(2)
            ledObj.mode = 3
            time.sleep(2)
            ledObj.mode = 4
            time.sleep(2)
