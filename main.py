from support import colorschemes, interface, colorgenerator
from support.weatherbit import api
from colour import Color
import time, threading
import queue, os, sys

num_led = 10
test=False

q = queue.Queue()
white = Color("white")

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
        self._tempscheme = colorgenerator.TemperatureScheme()
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
            print("{}, {}".format(weather.city_name, weather.state))
            print("Hi: {}, Lo: {}".format(highest, lowest))
            self._forecast = ( round(highest), round(lowest) )
            self._last_lookup = time.time()
        else:
            print("Using weather cache.")

        return self._forecast

    def run(self):
        cycle = colorschemes.Solid(num_led=num_led, pause_value=3, num_steps_per_cycle=100, num_cycles=0,
                                        color=int(white.get_hex_l()[1:], 16), brightness=100, test=test, test_interface=self._test_interface)
        cycle.start()

        while True:
            weather = self._get_high_low()
            print("High: {}, Low: {}".format(weather[0], weather[1]))
            color_code = self._tempscheme.get(weather[0])
            color_code_low = self._tempscheme.get(weather[1])
            print(color_code)
            print(color_code_low)
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
