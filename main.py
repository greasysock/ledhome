from support import apa102, colorschemes, interface
from weather import Weather
from colour import Color
import time, threading
import queue

num_led = 10
woeid = 2347592

test=False

top_high = 100
bottom_low = 10
color_range = top_high - bottom_low
color_mid_range = int(color_range / 2)

blue = Color("blue")
red = Color("red")
white = Color("white")
colors_low = list(blue.range_to(white, color_mid_range))
colors_high = list(white.range_to(red, color_mid_range))
colors = colors_low + colors_high

q = queue.Queue()

def worker():
    while True:
         print(q.qsize())
         a = q.get()
         print(q.qsize())
         q.task_done()
         print(q.qsize())

class MainLoop(threading.Thread):
    def __init__(self, test_interface=None):
        threading.Thread.__init__(self, target=worker)
        self._test_interface = test_interface
        self._weather = Weather()
        self._lookup = self._weather.lookup(woeid)
        self._lookup_timeout = 60*10
        self._last_lookup = 0
        self._forecast = -1
    def _get_high_low(self):
        if time.time() - self._last_lookup > self._lookup_timeout:
            forecast = self._lookup.forecast()
            hi = int(forecast[0].high())
            lo = int(forecast[1].low())

            self._forecast = ( hi, lo )
            self._last_lookup = time.time()
        else:
            print("Using weather cache.")

        return self._forecast
    def _get_high_low_colors(self):
        return (self._forecast[0] - bottom_low - 1, self._forecast[1] - bottom_low - 1)
    def run(self):
        weather = self._get_high_low()
        print("High: {}, Low: {}".format(weather[0], weather[1]))
        color_code = int(colors[weather[0]].get_hex()[1:], 16)
        color_code_low = int(colors[weather[1]].get_hex()[1:], 16)

        cycle = colorschemes.Solid(num_led=num_led, pause_value=3, num_steps_per_cycle=100, num_cycles=0,
                                        color=int(white.get_hex_l()[1:], 16), brightness=100, test=test, test_interface=self._test_interface)
        cycle.start()

        #hi = top_high - bottom_low - 1
        #lo = 0
        while True:
            #print("High: {}, Low: {}".format(colors[hi].get_hex_l()[1:], colors[lo].get_hex_l()[1:]))
            weather = self._get_high_low()
            hi_lo = self._get_high_low_colors()
            print("High: {}, Low: {}".format(weather[0], weather[1]))
            color_code = int(colors[hi_lo[0]].get_hex_l()[1:], 16)
            color_code_low = int(colors[hi_lo[1]].get_hex_l()[1:], 16)
            cycle.update_color(color_code_low)
            time.sleep(60)
            cycle.update_color(color_code)
            time.sleep(60)

if __name__ == "__main__":
    test_interface = None
    if test:
        test_interface = interface.LedPanel(num_led)
    main = MainLoop(test_interface=test_interface)
    main.start()
    if test:
        test_interface.start()
