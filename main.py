from support import apa102, colorschemes, interface
from support.weatherbit import api
from colour import Color
import time, threading
import queue, os, sys

num_led = 10
woeid = 2347592

test=True

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

try:
    weatherbit_api = os.environ['weatherbit_api']
except KeyError:
    print('ERROR: \'weatherbit_api\' env variable is missing.')
    sys.exit(2)

try:
    weatherbit_city = os.environ['weatherbit_city']
except KeyError:
    print('ERROR: \'weatherbit_city\' env variable is missing.')
    sys.exit(2)

try:
    weatherbit_state = os.environ['weatherbit_state']
except KeyError:
    print('ERROR: \'weatherbit_state\' env variable is missing.')
    sys.exit(2)


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
        self._weatherbit = api.connection(weatherbit_api)
        self._lookup_timeout = 60*60
        self._last_lookup = 0
        self._forecast = -1
    def _get_high_low(self):
        if time.time() - self._last_lookup > self._lookup_timeout:
            weather = self._weatherbit.get_forecast_hourly(city=weatherbit_city, state=weatherbit_state)
            highest = None
            lowest = None
            for forecast in weather.forecasts:
                try:
                    if forecast.temperature.actual > highest:
                        highest = forecast.temperature.actual
                except TypeError:
                    highest = forecast.temperature.actual
                try:
                    if forecast.temperature.actual < lowest:
                        lowest = forecast.temperature.actual
                except TypeError:
                    lowest = forecast.temperature.actual

            self._forecast = ( round(highest), round(lowest) )
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
