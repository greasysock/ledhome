from support import apa102
from weather import Weather
import time

num_led = 10
woeid = 2347592

def get_high_low():
    weather = Weather()
    lookup = weather.lookup(woeid)
    forcast = lookup.forecast()
    return (forcast[0].high(), forcast[0].low())

if __name__ == "__main__":
    weather = get_high_low()
    print(weather)
    pass