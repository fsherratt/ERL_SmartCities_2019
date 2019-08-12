import board
import neopixel
import time

class LED:
    def __init__(self):
        self.num_pixels = 8
        self.pin = board.D21

        self.pixels = neopixel.NeoPixel(board.D21, self.num_pixels, auto_write=False)

        self.mode = 0
        self.newMode = True
    
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear()

    def loop(self):
        while True:
            if self.mode == 0:
                self.flashGreen()

            else:
                self.rainbow_cycle( 0.02 )
                self.mode = 0
                self.newMode = True

            time.sleep(0.02)

    def flashGreen(self):
        if self.newMode:
            self.i = 0

            self.clear()
            self.newMode = False
            
            self.pixels.fill((0, 255, 0))
            self.pixels[0] = (0, 0, 0)
            self.pixels[2] = (0, 0, 0)
            self.pixels[4] = (0, 0, 0)
            self.pixels[6] = (0, 0, 0)
            self.pixels.show()
        
        self.i += 1

        if self.i % 100 == 0:
            self.newMode = True
            self.mode = 1

        elif self.i % 50 == 0:
            self.pixels.fill( (0, 255, 0) )
            self.pixels[1] = (0, 0, 0)
            self.pixels[3] = (0, 0, 0)
            self.pixels[5] = (0, 0, 0)
            self.pixels[7] = (0, 0, 0)
            self.pixels.show()

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