from support import colorschemes, colorgenerator, __title__, __author__, __version__
from support.weatherbit import api
from colour import Color
from enum import Enum
import time, threading, datetime
import queue, os, sys, argparse
import numpy as np
from scipy.interpolate import interp1d

DEFAULT_LED = 10
DEFAULT_TEST = False
DEFAULT_CYCLE = 'high_low'
DEFAULT_CYCLES = {
    'high_low' : 0,
    'np' : 1
}

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
    _DIM_TIME = 23
    _BRIGHT_TIME = 7
    _MAX_BRIGHT = 31
    _DIM_BRIGHT = 1
    def __init__(self, cycle, test_interface=None):
        threading.Thread.__init__(self, target=worker)
        self._cycle = cycle
        self._test_interface = test_interface
        self._weatherbit = api.connection(weatherbit_api)
        self._lookup_timeout = 60*20
        self._last_lookup = 0
        self._forecast = -1
        self._tempscheme = colorgenerator.TemperatureScheme()
        self._f = None
        self._x_val = None
    def _get_high_low(self):
        if time.time() - self._last_lookup > self._lookup_timeout:
            weather = self._weatherbit.get_forecast_hourly(city=weatherbit_city, state=weatherbit_state)
            self._get_np_high_low(weather)
            self._last_weather = weather

            highest = max(forecast.temperature.actual for forecast in weather.forecasts)
            lowest = min(forecast.temperature.actual for forecast in weather.forecasts)

            print("{}, {}".format(weather.city_name, weather.state))
            print("Hi: {}, Lo: {}".format(highest, lowest))
            self._forecast = ( round(highest), round(lowest) )
            self._last_lookup = time.time()
        else:
            print("Using weather cache.")

        return self._forecast
    def _get_np_high_low(self, weather):
        temp = list()
        x_temp = list()
        for x, forecast in enumerate(weather.forecasts):
            temp.append(forecast.temperature.actual)
            x_temp.append(x)
        temp = np.array(temp)
        self._x_val = np.array(x_temp)
 #       temp = np.array([50,45,65,70,65,40,45,25,21,28,20,19])
        self._f = interp1d(self._x_val, temp, bounds_error=False, kind='cubic')
    def _get_brightness(self):
        if datetime.datetime.now().hour >= self._DIM_TIME or datetime.datetime.now().hour <= self._BRIGHT_TIME:
            return self._DIM_BRIGHT
        return self._MAX_BRIGHT
    def run(self):
        if self._cycle == 0:
            cycle = colorschemes.Solid(num_led=DEFAULT_LED, pause_value=3, num_steps_per_cycle=100, num_cycles=0,
                                        brightness=100, test=test, test_interface=self._test_interface, order="rgb")
        elif self._cycle == 1:
            cycle = colorschemes.NpFunction(num_led=DEFAULT_LED, pause_value=3, num_steps_per_cycle=100, num_cycles=0,
                                       brightness=100, test=test, test_interface=self._test_interface, order="rgb",x_val=self._x_val)
            cycle.set_color_generator(self._tempscheme)
        else:
            cycle = colorschemes.Solid(num_led=DEFAULT_LED, pause_value=3, num_steps_per_cycle=100, num_cycles=0,
                                        brightness=100, test=test, test_interface=self._test_interface, order="rgb")
        cycle.start()
        while True:
            weather = self._get_high_low()
            brightness = self._get_brightness()
            cycle.set_brightness(brightness)
            print("High: {}, Low: {}, Brightness: {}".format(weather[0], weather[1], brightness))
            if self._cycle == 0:
                color_code = self._tempscheme.get(weather[0])
                color_code_low = self._tempscheme.get(weather[1])
                cycle.update_color(color_code_low)
                time.sleep(30)
                cycle.update_color(color_code)
                time.sleep(30)
            elif self._cycle == 1:
                cycle.update_function(self._f, self._x_val)
                cycle.run()



def main():
    parser = argparse.ArgumentParser(prog=__title__)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(__version__))
    parser.add_argument('-t', '--test', help='Simulates led animations in a tkinter window.', action='store_true', required=False)
    parser.add_argument('-l', '--leds', help='Number of LEDs to power. Default is 10.', metavar='\'(int)\'', required=False)
    parser.add_argument('-c', '--cycle', help='Choose cycle type.', metavar='\'(cycle)\'', required=False)


    args = parser.parse_args()

    test = DEFAULT_TEST
    leds = DEFAULT_LED
    cycle = DEFAULT_CYCLE
    if args.test:
        test = True
    if args.leds:
        try:
            value = int(args.leds)
            if value < 1:
                raise(ValueError)
            else:
                leds = value
        except ValueError:
            print("Must enter valid number of LEDs")
            sys.exit(2)
    if args.cycle:
        try:
            cycle = args.cycle
            DEFAULT_CYCLES[cycle]
        except KeyError:
            print("Enter a valid cycle type")
            sys.exit(2)
    cycle = DEFAULT_CYCLES[cycle]
    return test, leds, cycle

if __name__ == "__main__":
    test_interface = None
    test, num_led, cycle = main()
    if test:
        from support import interface
        test_interface = interface.LedPanel(num_led)
    main = MainLoop(cycle, test_interface=test_interface)
    main.start()
    if test:
        test_interface.start()
