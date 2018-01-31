"""This module contains a few concrete colour cycles to play with"""
import time
from support.colorcycletemplate import ColorCycleTemplate

class StrandTest(ColorCycleTemplate):
    """Runs a simple strand test (9 LEDs wander through the strip)."""

    color = None

    def init(self, strip, num_led):
        self.color = 0x000000  # Initialize with black

    def update(self, strip, num_led, num_steps_per_cycle, current_step,
               current_cycle):
        # One cycle = The 9 Test-LEDs wander through numStepsPerCycle LEDs.
        if current_step == 0:
            self.color >>= 8  # Red->green->blue->black
        if self.color == 0:
            self.color = 0xFF0000  # If black, reset to red
        len = 9
        if num_led - 1 < len:
            len = num_led - 1 
        # The head pixel that will be turned on in this cycle
        head = (current_step + len) % num_steps_per_cycle
        tail = current_step # The tail pixel that will be turned off
        strip.set_pixel_rgb(head, self.color)  # Paint head
        strip.set_pixel_rgb(tail, 0)  # Clear tail

        return 1 # Repaint is necessary


class TheaterChase(ColorCycleTemplate):
    """Runs a 'marquee' effect around the strip."""
    def update(self, strip, num_led, num_steps_per_cycle, current_step,
               current_cycle):
        # One cycle = One trip through the color wheel, 0..254
        # Few cycles = quick transition, lots of cycles = slow transition
        # Note: For a smooth transition between cycles, numStepsPerCycle must
        # be a multiple of 7
        start_index = current_step % 7 # One segment is 2 blank, and 5 filled
        color_index = strip.wheel(int(round(255/num_steps_per_cycle *
                                            current_step, 0)))
        for pixel in range(num_led):
            # Two LEDs out of 7 are blank. At each step, the blank
            # ones move one pixel ahead.
            if ((pixel+start_index) % 7 == 0) or ((pixel+start_index) % 7 == 1):
                strip.set_pixel_rgb(pixel, 0)
            else: strip.set_pixel_rgb(pixel, color_index)
        return 1


class RoundAndRound(ColorCycleTemplate):
    """Runs three LEDs around the strip."""

    def init(self, strip, num_led):
        strip.set_pixel_rgb(0, 0xFF0000)
        strip.set_pixel_rgb(1, 0xFF0000, 5) # Only 5% brightness
        strip.set_pixel_rgb(2, 0xFF0000)

    def update(self, strip, num_led, num_steps_per_cycle, current_step,
               current_cycle):
        # Simple class to demonstrate the "rotate" method
        strip.rotate()
        return 1


class Solid(ColorCycleTemplate):
    """Paints the strip with one colour."""
    color = None
    brightness = 5
    def __init__(self, num_led, pause_value, num_steps_per_cycle,num_cycles, color_tuple = (255, 255, 255), brightness = 5, test=False, test_interface=None, order="rbg"):
        self.color = color_tuple
        ColorCycleTemplate.__init__(self, num_led, pause_value, num_steps_per_cycle,num_cycles,test=test, test_interface=test_interface, order=order)
        self.num_led = num_led
    def _animation_weight(self, x_time):
        return ( x_time**2) / (self.num_steps_per_cycle * 100)
    def init(self, strip, num_led):
        for led in range(0, num_led):
            strip.set_pixel(led,self.color[0], self.color[1], self.color[2],self.brightness) # Paint 5% white
    def update_color(self, color_tuple):
        frame_time = float(1) / float(self.num_steps_per_cycle)

        Blue = self.color[2]
        Green = self.color[1]
        Red = self.color[0]

        frame = 1
        while frame <= self.num_steps_per_cycle:
            heavy = self._animation_weight(frame)
            BlueTemp = int(float(Blue * heavy))
            GreenTemp = int(float(Green * heavy))
            RedTemp = int(float(Red * heavy))
            #           print("Frame:{}, Weight:{}, RGB({},{},{})".format(frame, heavy, RedTemp, BlueTemp, GreenTemp))
            frame += 1
            for led in range(0, self.num_led):
                self.strip.set_pixel(led, Red-RedTemp, Green-GreenTemp, Blue-BlueTemp, self.brightness)
            self.strip.show()
            time.sleep(frame_time)
        time.sleep(.2)
        Blue = color_tuple[2]
        Green = color_tuple[1]
        Red = color_tuple[0]
        frame = 1

        while frame <= self.num_steps_per_cycle:
            heavy = self._animation_weight(frame)
            BlueTemp = int(float(Blue * heavy))
            GreenTemp = int(float(Green * heavy))
            RedTemp = int(float(Red * heavy))
#            print("Frame:{}, Weight:{}, RGB({},{},{})".format(frame, heavy, RedTemp, BlueTemp, GreenTemp))
            frame += 1
            for led in range(0, self.num_led):
                self.strip.set_pixel(led, RedTemp, GreenTemp, BlueTemp, self.brightness)
            self.strip.show()
            time.sleep(frame_time)

        for led in range(0, self.num_led):
            self.strip.set_pixel(led, Red, Green, Blue,self.brightness)
        self.strip.show()

        self.color = color_tuple
    def update(self, strip, num_led, num_steps_per_cycle, current_step,
               current_cycle):
        # Do nothing: Init lit the strip, and update just keeps it this way
        return 0


class Rainbow(ColorCycleTemplate):
    """Paints a rainbow effect across the entire strip."""
    def update(self, strip, num_led, num_steps_per_cycle, current_step,
               current_cycle):
        # One cycle = One trip through the color wheel, 0..254
        # Few cycles = quick transition, lots of cycles = slow transition
        # -> LED 0 goes from index 0 to 254 in numStepsPerCycle cycles.
        #     So it might have to step up more or less than one index
        #     depending on numStepsPerCycle.
        # -> The other LEDs go up to 254, then wrap around to zero and go up
        #     again until the last one is just below LED 0. This way, the
        #     strip always shows one full rainbow, regardless of the
        #     number of LEDs
        scale_factor = 255 / num_led # Index change between two neighboring LEDs
        start_index = 255 / num_steps_per_cycle * current_step # LED 0
        for i in range(num_led):
            # Index of LED i, not rounded and not wrapped at 255
            led_index = start_index + i * scale_factor
            # Now rounded and wrapped
            led_index_rounded_wrapped = int(round(led_index, 0)) % 255
            # Get the actual color out of the wheel
            pixel_color = strip.wheel(led_index_rounded_wrapped)
            strip.set_pixel_rgb(i, pixel_color)
        return 1 # All pixels are set in the buffer, so repaint the strip now
