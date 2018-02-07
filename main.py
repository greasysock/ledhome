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
DEFAULT_CYCLE = 'np'
DEFAULT_NIGHT = False
DEFAULT_GRAPH = False
DEFAULT_BRIGHTNESS = 31

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

try:
    DEFAULT_LED = int(os.environ['tealight_leds'])
except KeyError:
    pass
except ValueError:
    print("Invalid number in tealight_leds")
    sys.exit(2)

try:
    DEFAULT_BRIGHTNESS = int(os.environ['tealight_brightness_day'])
except KeyError:
    pass
except ValueError:
    print("Invalid number in tealight_brightness_day")
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
    _MAX_BRIGHT = DEFAULT_BRIGHTNESS
    _DIM_BRIGHT = 15
    _NIGHT_BRIGHT = 0
    def __init__(self, cycle, test_interface=None, night_mode = DEFAULT_NIGHT, leds = DEFAULT_LED, graph = DEFAULT_GRAPH):
        threading.Thread.__init__(self, target=worker)
        self._cycle = cycle
        self._night = night_mode
        self._leds = leds
        self._graph = graph
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
            try:
                weather = self._weatherbit.get_forecast_hourly(city=weatherbit_city, state=weatherbit_state)
            except api.ConnectionError:
                weather = self._last_weather
                print("Connection Error. Using last forecast.")
            self._last_weather = weather
            self._get_np_high_low(weather)
            self._last_weather = weather

            highest = max(forecast.temperature.actual for forecast in weather.forecasts)
            lowest = min(forecast.temperature.actual for forecast in weather.forecasts)

            print("{}, {}".format(weather.city_name, weather.state))
            print("Hi: {}, Lo: {}".format(highest, lowest))
            self._forecast = ( round(highest), round(lowest) )
            self._last_lookup = time.time()

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
        if self._graph:
            xnew = np.linspace(0, weather.__len__(), num=100, endpoint=True)
            plt.plot(x_temp, temp, 'o', xnew, self._f(xnew), '--')
            name = "{}.png".format(datetime.datetime.now().hour)
            plt.savefig(name)
    def _get_brightness(self):
        latest_forecast = self._last_weather.forecasts[0]
        if datetime.datetime.now().hour >= self._DIM_TIME or datetime.datetime.now().hour <= self._BRIGHT_TIME:
            return self._NIGHT_BRIGHT
        elif self._night and latest_forecast.day_to_night:
            return self._DIM_BRIGHT
        return self._MAX_BRIGHT
    def run(self):
        if self._cycle == 0:
            cycle = colorschemes.Solid(num_led=self._leds, pause_value=3, num_steps_per_cycle=100, num_cycles=0,
                                        brightness=100, test=test, test_interface=self._test_interface, order="rgb")
        elif self._cycle == 1:
            cycle = colorschemes.NpFunction(num_led=self._leds, pause_value=3, num_steps_per_cycle=100, num_cycles=0,
                                       brightness=100, test=test, test_interface=self._test_interface, order="rgb",x_val=self._x_val)
            cycle.set_color_generator(self._tempscheme)
        else:
            cycle = colorschemes.Solid(num_led=self._leds, pause_value=3, num_steps_per_cycle=100, num_cycles=0,
                                        brightness=100, test=test, test_interface=self._test_interface, order="rgb")
        cycle.start()
        while True:
            weather = self._get_high_low()
            brightness = self._get_brightness()
            cycle.set_brightness(brightness)
            if self._cycle == 0:
                print("High: {}, Low: {}, Brightness: {}".format(weather[0], weather[1], brightness))
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
    parser.add_argument('-n', '--night', help='Enable night mode to dim brightness after sunset.', action='store_true', required=False)
    parser.add_argument('-g', '--graph', help='Enable hourly graphs.', action='store_true', required=False)



    args = parser.parse_args()

    test = DEFAULT_TEST
    leds = DEFAULT_LED
    cycle = DEFAULT_CYCLE
    night = DEFAULT_NIGHT
    graph = DEFAULT_GRAPH
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

    if args.night:
        night = True
    if args.graph:
        graph = True
    cycle = DEFAULT_CYCLES[cycle]
    return test, leds, cycle, night, graph

if __name__ == "__main__":
    test_interface = None
    test, num_led, cycle, night, graph = main()
    if test:
        from support import interface
        test_interface = interface.LedPanel(num_led)
    if graph:
        import matplotlib as mpl
        mpl.use('Agg')
        import matplotlib.pyplot as plt
    main = MainLoop(cycle, test_interface=test_interface, night_mode=night, leds=num_led, graph=graph)
    main.start()
    if test:
        test_interface.start()
